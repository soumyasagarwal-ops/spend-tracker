"""Detect credit-card bill payments — money settling a card (CRED, direct card
payment, etc.). The actual consumption already happened *on the card*, so these
lump settlements should not be counted as fresh category spend. They are shown
separately as "card bills".
"""
from __future__ import annotations
from app.config import settings


def is_card_payment(description: str, keywords: list[str] | None = None) -> bool:
    keywords = keywords if keywords is not None else settings.card_payment_keywords
    if not description:
        return False
    up = description.upper()
    return any(k.upper() in up for k in keywords)
