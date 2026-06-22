import threading
import time
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent
from app.database import SessionLocal
from app.ingestion.pipeline import run_ingestion

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".csv", ".pdf", ".xlsx", ".xls"}
DEBOUNCE_SECONDS = 0.5


class _DropFolderHandler(FileSystemEventHandler):
    def __init__(self):
        self._pending: dict[str, float] = {}
        self._lock = threading.Lock()

    def on_created(self, event: FileCreatedEvent):
        if event.is_directory:
            return
        path = Path(event.src_path)
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            return
        with self._lock:
            self._pending[str(path)] = time.time()

    def on_modified(self, event):
        # Reset debounce timer on modification too (handles slow file copies)
        if event.is_directory:
            return
        path = Path(event.src_path)
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            return
        with self._lock:
            if str(path) in self._pending:
                self._pending[str(path)] = time.time()

    def drain_ready(self) -> list[str]:
        """Return paths that haven't been modified in DEBOUNCE_SECONDS."""
        now = time.time()
        ready = []
        with self._lock:
            for path, ts in list(self._pending.items()):
                if now - ts >= DEBOUNCE_SECONDS:
                    ready.append(path)
                    del self._pending[path]
        return ready


def _watcher_loop(folder: str, handler: _DropFolderHandler, observer: Observer):
    while observer.is_alive():
        for filepath in handler.drain_ready():
            logger.info(f"Watcher: ingesting {filepath}")
            db = SessionLocal()
            try:
                log = run_ingestion(filepath, db)
                logger.info(f"Watcher: ingested {filepath} — {log.rows_inserted} inserted, {log.rows_skipped} skipped")
            except Exception as e:
                logger.error(f"Watcher: failed to ingest {filepath}: {e}")
            finally:
                db.close()
        time.sleep(0.25)


def start_watcher(folder: str) -> None:
    Path(folder).mkdir(parents=True, exist_ok=True)
    handler = _DropFolderHandler()
    observer = Observer()
    observer.schedule(handler, folder, recursive=False)
    observer.start()

    loop_thread = threading.Thread(target=_watcher_loop, args=(folder, handler, observer), daemon=True)
    loop_thread.start()
    logger.info(f"File watcher started on: {folder}")
