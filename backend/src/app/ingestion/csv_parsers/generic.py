from __future__ import annotations
import csv
from datetime import datetime
from typing import Optional, List
from app.ingestion.base import BaseParser, RawTransaction

_DATE_CANDIDATES = ["date", "txn date", "transaction date", "value date", "posting date"]
_DESC_CANDIDATES = ["narration", "description", "remarks", "transaction remarks", "particulars", "details"]
_DEBIT_CANDIDATES = ["debit", "debit amount", "withdrawal", "withdrawal amt.", "dr amount", "dr"]
_CREDIT_CANDIDATES = ["credit", "credit amount", "deposit", "deposit amt.", "cr amount", "cr"]
_AMOUNT_CANDIDATES = ["amount", "txn amount", "transaction amount"]


def _find_col(headers: List[str], candidates: List[str]) -> Optional[str]:
    headers_lower = [h.lower().strip() for h in headers]
    for candidate in candidates:
        if candidate.lower() in headers_lower:
            return headers[headers_lower.index(candidate.lower())]
    return None


class GenericCsvParser(BaseParser):
    SOURCE_NAME = "generic_csv"

    def can_parse(self, filepath: str, headers: List[str]) -> bool:
        return True

    def parse(self, filepath: str) -> List[RawTransaction]:
        rows: List[RawTransaction] = []
        with open(filepath, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                return rows
            headers = list(reader.fieldnames)

            date_col = _find_col(headers, _DATE_CANDIDATES)
            desc_col = _find_col(headers, _DESC_CANDIDATES)
            debit_col = _find_col(headers, _DEBIT_CANDIDATES)
            credit_col = _find_col(headers, _CREDIT_CANDIDATES)
            amount_col = _find_col(headers, _AMOUNT_CANDIDATES)

            if not date_col or not desc_col:
                return rows

            for row in reader:
                try:
                    txn_date = self._parse_date(row[date_col].strip())
                    if txn_date is None:
                        continue

                    description = row.get(desc_col, "").strip()
                    if not description:
                        continue

                    txn_type = "debit"
                    amount = 0.0

                    if debit_col and row.get(debit_col, "").strip().replace(",", ""):
                        raw = row[debit_col].strip().replace(",", "")
                        if raw:
                            try:
                                v = float(raw)
                                if v > 0:
                                    amount = v
                                    txn_type = "debit"
                            except ValueError:
                                pass
                    if amount == 0.0 and credit_col and row.get(credit_col, "").strip().replace(",", ""):
                        raw = row[credit_col].strip().replace(",", "")
                        if raw:
                            try:
                                v = float(raw)
                                if v > 0:
                                    amount = v
                                    txn_type = "credit"
                            except ValueError:
                                pass
                    if amount == 0.0 and amount_col and row.get(amount_col, "").strip().replace(",", ""):
                        raw = row[amount_col].strip().replace(",", "").lstrip("-")
                        if raw:
                            try:
                                amount = abs(float(raw))
                            except ValueError:
                                pass

                    if amount == 0.0:
                        continue

                    rows.append(RawTransaction(
                        date=txn_date,
                        amount=amount,
                        transaction_type=txn_type,
                        description=description,
                        source=self.SOURCE_NAME,
                    ))
                except (ValueError, KeyError):
                    continue
        return rows

    def _parse_date(self, raw: str) -> Optional[object]:
        for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y", "%Y-%m-%d", "%d %b %Y", "%d %B %Y"):
            try:
                return datetime.strptime(raw, fmt).date()
            except ValueError:
                continue
        return None
