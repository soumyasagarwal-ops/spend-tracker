import csv
from datetime import datetime
from app.ingestion.base import BaseParser, RawTransaction


class IciciCsvParser(BaseParser):
    SOURCE_NAME = "icici_csv"

    _DATE_COL = "Transaction Date"
    _REMARKS_COL = "Transaction Remarks"
    _DEBIT_COL = "Debit Amount"
    _CREDIT_COL = "Credit Amount"

    def can_parse(self, filepath: str, headers: list[str]) -> bool:
        required = {self._DATE_COL, self._REMARKS_COL, self._DEBIT_COL}
        return required.issubset(set(headers))

    def parse(self, filepath: str) -> list[RawTransaction]:
        rows: list[RawTransaction] = []
        with open(filepath, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    txn_date = self._parse_date(row[self._DATE_COL].strip())
                    if txn_date is None:
                        continue

                    debit_raw = row.get(self._DEBIT_COL, "").strip().replace(",", "")
                    credit_raw = row.get(self._CREDIT_COL, "").strip().replace(",", "")

                    if debit_raw and float(debit_raw) > 0:
                        amount = float(debit_raw)
                        txn_type = "debit"
                    elif credit_raw and float(credit_raw) > 0:
                        amount = float(credit_raw)
                        txn_type = "credit"
                    else:
                        continue

                    description = row.get(self._REMARKS_COL, "").strip()
                    if not description:
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

    def _parse_date(self, raw: str):
        for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y", "%Y-%m-%d"):
            try:
                return datetime.strptime(raw, fmt).date()
            except ValueError:
                continue
        return None
