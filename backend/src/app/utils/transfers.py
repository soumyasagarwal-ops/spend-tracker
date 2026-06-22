"""Detect internal / self transfers — money moved between the account holder's
own accounts. These are not real income or spend and must be excluded from
analytics, otherwise they inflate income and savings figures.

Heuristic: a transaction is an internal transfer when the counterparty named in
the description is the account holder themselves, appearing immediately after a
bank-transfer reference (IMPS/NEFT/FT/MMT + reference number).

Example that SHOULD match (self transfer):
    IMPS-000000000000-YOURNAME-UTIB-XXXXXXXXXXX0000-IM

Example that should NOT match (incoming payment where the holder is only the
beneficiary, not the originator — i.e. real income):
    NEFT CR-XXXX0000000-EXAMPLE CORP NOV 2025-YOURNAM
"""
from __future__ import annotations
import re
from app.config import settings

_TRANSFER_PREFIX = r"(?:IMPS|NEFT|IFT|FT|MMT|RTGS|TPT|ACH)"
# any bank-transfer marker present anywhere in the (normalized) description
_HAS_TRANSFER = re.compile(_TRANSFER_PREFIX)


def _normalize(text: str) -> str:
    """Uppercase and strip to alphanumerics so hyphen/space variations don't matter."""
    return re.sub(r"[^A-Z0-9]", "", (text or "").upper())


def is_internal_transfer(description: str, names: list[str] | None = None) -> bool:
    """True if the description looks like a transfer involving the holder's own name.

    Two patterns are matched:
    1. `<PREFIX><digits><NAME>` — name right after a transfer ref
       (e.g. IMPS-000000000000-YOURNAME-UTIB-…)
    2. The holder's full name appears anywhere in a transfer-type line
       (e.g. NEFT DR-XXXX0000000-YOURNAME-NETBANK, MUM).
    Requiring the *full* name token avoids false positives like an MF redemption
    where only a truncated beneficiary name appears (…MUTUAL FUND-SHUB).
    """
    names = names if names is not None else settings.account_holder_names
    if not names:
        return False
    norm = _normalize(description)
    for name in names:
        token = _normalize(name)
        if not token:
            continue
        if re.search(rf"{_TRANSFER_PREFIX}\d+{token}", norm):
            return True
        if token in norm and _HAS_TRANSFER.search(norm):
            return True
    return False
