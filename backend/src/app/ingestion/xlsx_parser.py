from __future__ import annotations
from datetime import datetime, date as date_type
from pathlib import Path
from typing import Optional, List
from app.ingestion.base import BaseParser, RawTransaction
from app.ingestion.csv_parsers.generic import (
    _DATE_CANDIDATES,
    _DESC_CANDIDATES,
    _DEBIT_CANDIDATES,
    _CREDIT_CANDIDATES,
    _AMOUNT_CANDIDATES,
)

_ALL_CANDIDATES = set(
    _DATE_CANDIDATES + _DESC_CANDIDATES + _DEBIT_CANDIDATES +
    _CREDIT_CANDIDATES + _AMOUNT_CANDIDATES
)


def _find_col_idx(headers: List[str], candidates: List[str]) -> Optional[int]:
    headers_lower = [str(h).lower().strip() if h else "" for h in headers]
    for candidate in candidates:
        if candidate.lower() in headers_lower:
            return headers_lower.index(candidate.lower())
    return None


def _cell_str(cell) -> str:
    if cell is None:
        return ""
    return str(cell).strip()


def _parse_date_str(raw: str) -> Optional[date_type]:
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y", "%Y-%m-%d", "%d %b %Y", "%d %B %Y",
                "%d/%m/%y", "%d-%m-%y"):
        try:
            return datetime.strptime(raw.strip(), fmt).date()
        except ValueError:
            continue
    return None


def _resolve_amount(row, debit_idx, credit_idx, amount_idx):
    def clean(val) -> Optional[float]:
        if val is None:
            return None
        if isinstance(val, (int, float)):
            return abs(float(val)) if float(val) != 0 else None
        s = str(val).strip().replace(",", "")
        if not s:
            return None
        try:
            return float(s)
        except ValueError:
            return None

    if debit_idx is not None and debit_idx < len(row):
        v = clean(row[debit_idx])
        if v and v > 0:
            return v, "debit"
    if credit_idx is not None and credit_idx < len(row):
        v = clean(row[credit_idx])
        if v and v > 0:
            return v, "credit"
    if amount_idx is not None and amount_idx < len(row):
        v = clean(row[amount_idx])
        if v:
            return v, "debit"
    return None, "debit"


def _find_header_row(sheet_rows: list) -> Optional[int]:
    for i, row in enumerate(sheet_rows[:50]):
        if not row:
            continue
        cells = [str(c).lower().strip() for c in row if c is not None and str(c).strip()]
        if any(c in _ALL_CANDIDATES for c in cells):
            return i
    return None


def _parse_xlsx(filepath: str) -> List[RawTransaction]:
    import openpyxl
    wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)
    rows: List[RawTransaction] = []

    for sheet in wb.worksheets:
        sheet_rows = list(sheet.iter_rows(values_only=True))
        header_idx = _find_header_row(sheet_rows)
        if header_idx is None:
            continue

        headers = [str(c).strip() if c is not None else "" for c in sheet_rows[header_idx]]
        date_idx = _find_col_idx(headers, _DATE_CANDIDATES)
        desc_idx = _find_col_idx(headers, _DESC_CANDIDATES)
        debit_idx = _find_col_idx(headers, _DEBIT_CANDIDATES)
        credit_idx = _find_col_idx(headers, _CREDIT_CANDIDATES)
        amount_idx = _find_col_idx(headers, _AMOUNT_CANDIDATES)

        if date_idx is None or desc_idx is None:
            continue

        for row in sheet_rows[header_idx + 1:]:
            if not row or all(c is None or str(c).strip() == "" for c in row):
                continue
            try:
                raw_date = row[date_idx] if date_idx < len(row) else None
                if isinstance(raw_date, datetime):
                    txn_date = raw_date.date()
                elif isinstance(raw_date, date_type):
                    txn_date = raw_date
                else:
                    txn_date = _parse_date_str(_cell_str(raw_date))
                if txn_date is None:
                    continue

                description = _cell_str(row[desc_idx] if desc_idx < len(row) else None)
                if not description:
                    continue

                amount, txn_type = _resolve_amount(row, debit_idx, credit_idx, amount_idx)
                if amount is None or amount == 0.0:
                    continue

                rows.append(RawTransaction(
                    date=txn_date, amount=amount, transaction_type=txn_type,
                    description=description, source="xlsx",
                ))
            except (ValueError, IndexError, TypeError):
                continue

    wb.close()
    return rows


def _parse_xls(filepath: str) -> List[RawTransaction]:
    import xlrd
    wb = xlrd.open_workbook(filepath)
    rows: List[RawTransaction] = []

    for sheet in wb.sheets():
        sheet_rows = [sheet.row_values(i) for i in range(sheet.nrows)]
        header_idx = _find_header_row(sheet_rows)
        if header_idx is None:
            continue

        headers = [str(c).strip() if c is not None else "" for c in sheet_rows[header_idx]]
        date_idx = _find_col_idx(headers, _DATE_CANDIDATES)
        desc_idx = _find_col_idx(headers, _DESC_CANDIDATES)
        debit_idx = _find_col_idx(headers, _DEBIT_CANDIDATES)
        credit_idx = _find_col_idx(headers, _CREDIT_CANDIDATES)
        amount_idx = _find_col_idx(headers, _AMOUNT_CANDIDATES)

        if date_idx is None or desc_idx is None:
            continue

        for row in sheet_rows[header_idx + 1:]:
            if not row or all(c is None or str(c).strip() == "" for c in row):
                continue
            # Skip separator rows like ****...
            first_cell = str(row[0]).strip() if row[0] is not None else ""
            if first_cell.startswith("*") or first_cell.startswith("-"):
                continue
            try:
                raw_date = row[date_idx] if date_idx < len(row) else None
                txn_date: Optional[date_type] = None

                # xlrd returns dates as floats (Excel serial numbers)
                if isinstance(raw_date, float) and raw_date > 0:
                    try:
                        tup = xlrd.xldate_as_tuple(raw_date, wb.datemode)
                        txn_date = date_type(*tup[:3])
                    except Exception:
                        pass
                if txn_date is None:
                    txn_date = _parse_date_str(_cell_str(raw_date))
                if txn_date is None:
                    continue

                description = _cell_str(row[desc_idx] if desc_idx < len(row) else None)
                if not description:
                    continue

                amount, txn_type = _resolve_amount(row, debit_idx, credit_idx, amount_idx)
                if amount is None or amount == 0.0:
                    continue

                rows.append(RawTransaction(
                    date=txn_date, amount=amount, transaction_type=txn_type,
                    description=description, source="xls",
                ))
            except (ValueError, IndexError, TypeError):
                continue

    return rows


class XlsxParser(BaseParser):
    SOURCE_NAME = "xlsx"

    def can_parse(self, filepath: str, headers: List[str]) -> bool:
        return Path(filepath).suffix.lower() in (".xlsx", ".xls")

    def parse(self, filepath: str) -> List[RawTransaction]:
        ext = Path(filepath).suffix.lower()
        if ext == ".xls":
            return _parse_xls(filepath)
        return _parse_xlsx(filepath)
