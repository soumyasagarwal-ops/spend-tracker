from __future__ import annotations
import json
from datetime import datetime
from typing import List
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    color: Mapped[str] = mapped_column(String, nullable=False, default="#6366f1")
    keywords: Mapped[str] = mapped_column(String, nullable=False, default="[]")  # JSON array
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    transactions: Mapped[List] = relationship("Transaction", back_populates="category")

    def get_keywords(self) -> list[str]:
        return json.loads(self.keywords)

    def set_keywords(self, kw: list[str]) -> None:
        self.keywords = json.dumps(kw)
