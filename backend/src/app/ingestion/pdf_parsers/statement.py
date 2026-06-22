from __future__ import annotations
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Tuple
import pdfplumber
from app.ingestion.base import BaseParser, RawTransaction

_DATE_RE = re.compile(r"\b(\d{2}[\/\-]\d{2}[\/\-]\d{2,4}|\d{2}\s+\w{3}\s+\d{4})\b")
_AMOUNT_RE = re.compile(r"[\d,]+\.\d{2}")


class PdfStatementParser(BaseParser):
    SOURCE_NAME = "pdf_statement"

    def can_parse(self, filepath: str, headers: List[str]) -> bool:
        return Path(filepath).suffix.lower() == ".pdf"

    def parse(self, filepath: str) -> List[RawTransaction]:
        rows: List[RawTransaction] = []
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        rows.extend(self._parse_table(table))
                else:
                    text = page.extract_text() or ""
                    rows.extend(self._parse_text(text))
        return rows

    def _parse_table(self, table: List[List]) -> List[RawTransaction]:
        if not table or len(table) < 2:
            return []

        rows: List[RawTransaction] = []
        header_row = [str(c).strip().lower() if c else "" for c in table[0]]

        date_idx = self._find_idx(header_row, ["date", "txn date", "value date"])
        desc_idx = self._find_idx(header_row, ["description", "narration", "particulars", "remarks"])
        debit_idx = self._find_idx(header_row, ["debit", "withdrawal", "dr"])
        credit_idx = self._find_idx(header_row, ["credit", "deposit", "cr"])
        amount_idx = self._find_idx(header_row, ["amount"])

        if date_idx is None or desc_idx is None:
            return []

        for row in table[1:]:
            if not row or not row[date_idx]:
                continue
            try:
                txn_date = self._parse_date(str(row[date_idx]).strip())
                if not txn_date:
                    continue
                description = str(row[desc_idx]).strip() if row[desc_idx] else ""
                if not description:
                    continue

                amount, txn_type = self._resolve_amount(row, debit_idx, credit_idx, amount_idx)
                if amount is None or amount == 0.0:
                    continue

                rows.append(RawTransaction(
                    date=txn_date,
                    amount=amount,
                    transaction_type=txn_type,
                    description=description,
                    source=self.SOURCE_NAME,
                ))
            except (ValueError, IndexError):
                continue
        return rows

    def _parse_text(self, text: str) -> List[RawTransaction]:
        rows: List[RawTransaction] = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            date_match = _DATE_RE.search(line)
            if not date_match:
                continue
            txn_date = self._parse_date(date_match.group(0))
            if not txn_date:
                continue
            amounts = _AMOUNT_RE.findall(line)
            if not amounts:
                continue
            amount = float(amounts[-1].replace(",", ""))
            description = line[:date_match.start()].strip() or line[date_match.end():].strip()
            description = re.sub(r"\s+", " ", description).strip()
            if not description or amount == 0.0:
                continue
            rows.append(RawTransaction(
                date=txn_date,
                amount=amount,
                transaction_type="debit",
                description=description,
                source=self.SOURCE_NAME,
            ))
        return rows

    def _find_idx(self, headers: List[str], candidates: List[str]) -> Optional[int]:
        for candidate in candidates:
            for i, h in enumerate(headers):
                if candidate in h:
                    return i
        return None

    def _resolve_amount(self, row: List, debit_idx: Optional[int], credit_idx: Optional[int], amount_idx: Optional[int]) -> Tuple[Optional[float], str]:
        def clean(val) -> Optional[float]:
            if val is None:
                return None
            s = str(val).strip().replace(",", "")
            if not s:
                return None
            try:
                return float(s)
            except ValueError:
                return None

        if debit_idx is not None:
            v = clean(row[debit_idx] if debit_idx < len(row) else None)
            if v and v > 0:
                return v, "debit"
        if credit_idx is not None:
            v = clean(row[credit_idx] if credit_idx < len(row) else None)
            if v and v > 0:
                return v, "credit"
        if amount_idx is not None:
            v = clean(row[amount_idx] if amount_idx < len(row) else None)
            if v:
                return abs(v), "debit"
        return None, "debit"

    def _parse_date(self, raw: str) -> Optional[object]:
        for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y", "%d %b %Y", "%d %B %Y"):
            try:
                return datetime.strptime(raw.strip(), fmt).date()
            except ValueError:
                continue
        return None
