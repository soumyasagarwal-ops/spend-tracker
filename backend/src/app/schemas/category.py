from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class CategoryOut(BaseModel):
    id: int
    name: str
    color: str
    keywords: List[str]
    created_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_model(cls, obj) -> CategoryOut:
        return cls(
            id=obj.id,
            name=obj.name,
            color=obj.color,
            keywords=obj.get_keywords(),
            created_at=obj.created_at,
        )


class CategoryCreate(BaseModel):
    name: str
    color: str = "#6366f1"
    keywords: List[str] = []


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None
    keywords: Optional[List[str]] = None
