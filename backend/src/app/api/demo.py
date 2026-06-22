from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.transaction import Transaction
from app.demo.generator import generate_demo_data

router = APIRouter(prefix="/demo", tags=["demo"])


@router.post("/generate")
def generate(db: Session = Depends(get_db)):
    count = generate_demo_data(db)
    return {"message": f"Demo data ready", "transaction_count": count}


@router.delete("/clear", status_code=204)
def clear_demo(db: Session = Depends(get_db)):
    db.query(Transaction).filter(Transaction.data_mode == "demo").delete()
    db.commit()
