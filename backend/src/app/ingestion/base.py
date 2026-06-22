from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date


@dataclass
class RawTransaction:
    date: date
    amount: float
    transaction_type: str  # 'debit' | 'credit'
    description: str
    source: str


class BaseParser(ABC):
    SOURCE_NAME: str = "unknown"

    @abstractmethod
    def can_parse(self, filepath: str, headers: list[str]) -> bool:
        """Return True if this parser recognizes the file."""
        ...

    @abstractmethod
    def parse(self, filepath: str) -> list[RawTransaction]:
        """Parse the file and return a list of RawTransaction objects."""
        ...
