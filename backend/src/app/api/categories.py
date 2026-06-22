import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.category import Category
from app.schemas.category import CategoryOut, CategoryCreate, CategoryUpdate
from app.categorization.engine import invalidate_cache

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    cats = db.query(Category).order_by(Category.name).all()
    return [CategoryOut.from_orm_model(c) for c in cats]


@router.post("", response_model=CategoryOut, status_code=201)
def create_category(body: CategoryCreate, db: Session = Depends(get_db)):
    cat = Category(name=body.name, color=body.color)
    cat.set_keywords(body.keywords)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    invalidate_cache()
    return CategoryOut.from_orm_model(cat)


@router.patch("/{cat_id}", response_model=CategoryOut)
def update_category(cat_id: int, body: CategoryUpdate, db: Session = Depends(get_db)):
    cat = db.query(Category).filter(Category.id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    if body.name is not None:
        cat.name = body.name
    if body.color is not None:
        cat.color = body.color
    if body.keywords is not None:
        cat.set_keywords(body.keywords)
    db.commit()
    db.refresh(cat)
    invalidate_cache()
    return CategoryOut.from_orm_model(cat)


@router.delete("/{cat_id}", status_code=204)
def delete_category(cat_id: int, db: Session = Depends(get_db)):
    cat = db.query(Category).filter(Category.id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(cat)
    db.commit()
    invalidate_cache()
