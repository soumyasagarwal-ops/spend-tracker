from __future__ import annotations
from typing import Optional, Dict, Tuple, List
from sqlalchemy.orm import Session
from app.models.category import Category


_cache: Optional[Dict[int, Tuple[str, List[str]]]] = None


def _load_cache(db: Session) -> Dict[int, Tuple[str, List[str]]]:
    global _cache
    if _cache is None:
        cats = db.query(Category).all()
        _cache = {c.id: (c.name, c.get_keywords()) for c in cats}
    return _cache


def invalidate_cache() -> None:
    global _cache
    _cache = None


def categorize(description: str, db: Session) -> Optional[int]:
    desc_lower = description.lower()
    cache = _load_cache(db)
    for cat_id, (name, keywords) in cache.items():
        for kw in keywords:
            if kw.lower() in desc_lower:
                return cat_id
    return None
