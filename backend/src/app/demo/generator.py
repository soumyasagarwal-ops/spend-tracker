import random
import math
import uuid
from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.models.transaction import Transaction
from app.categorization.engine import categorize
from app.utils.dedup import row_hash as compute_row_hash

DEMO_MERCHANTS: dict[str, list[tuple[str, float, float]]] = {
    # (merchant_name, mean_amount, std_dev)
    "Food & Dining": [
        ("Zomato Order", 350, 150),
        ("Swiggy Delivery", 280, 120),
        ("Cafe Coffee Day", 180, 60),
        ("Dominos Pizza", 420, 100),
        ("KFC Bangalore", 320, 80),
    ],
    "Transport": [
        ("Uber Ride", 120, 60),
        ("Ola Cab", 100, 50),
        ("Rapido Bike", 50, 20),
        ("BMTC Bus Pass", 500, 0),
        ("IRCTC Train Ticket", 650, 300),
    ],
    "Groceries": [
        ("BigBasket Order", 1400, 500),
        ("Zepto Quick Delivery", 600, 200),
        ("Blinkit Groceries", 800, 300),
        ("DMart Store", 1800, 600),
    ],
    "Shopping": [
        ("Amazon Purchase", 1200, 800),
        ("Flipkart Order", 900, 600),
        ("Myntra Fashion", 1500, 700),
        ("Nykaa Beauty", 700, 300),
    ],
    "Utilities": [
        ("Airtel Prepaid Recharge", 599, 0),
        ("BESCOM Electricity Bill", 900, 300),
        ("JIO Fiber Plan", 999, 0),
    ],
    "Entertainment": [
        ("Netflix Subscription", 649, 0),
        ("Spotify Premium", 119, 0),
        ("BookMyShow Movie", 450, 150),
        ("Hotstar Subscription", 299, 0),
    ],
    "Health": [
        ("PharmEasy Order", 450, 200),
        ("Apollo Pharmacy", 350, 150),
        ("Cult.fit Membership", 2000, 0),
        ("Diagnostic Labs", 800, 300),
    ],
    "Finance": [
        ("Zerodha SIP", 5000, 0),
        ("LIC Premium", 3000, 0),
        ("Groww Investment", 2000, 1000),
    ],
    "Personal Care": [
        ("Naturals Salon", 600, 200),
        ("UrbanCompany Service", 800, 300),
    ],
    "Education": [
        ("Udemy Course", 499, 200),
        ("Coursera Subscription", 2500, 0),
        ("Bookstore Purchase", 350, 150),
    ],
}

# How many transactions per category in 4-week period
CATEGORY_FREQUENCY: dict[str, int] = {
    "Food & Dining": 16,
    "Transport": 20,
    "Groceries": 6,
    "Shopping": 4,
    "Utilities": 2,
    "Entertainment": 3,
    "Health": 2,
    "Finance": 2,
    "Personal Care": 2,
    "Education": 1,
}


def _lognormal_amount(mean: float, std: float) -> float:
    if std == 0:
        return mean
    # Convert to lognormal parameters
    sigma2 = math.log(1 + (std / mean) ** 2)
    mu = math.log(mean) - sigma2 / 2
    return max(10.0, round(random.lognormvariate(mu, math.sqrt(sigma2)), 2))


def generate_demo_data(db: Session) -> int:
    """Generate 13 months of synthetic demo transactions. Idempotent."""
    existing_count = db.query(Transaction).filter(Transaction.data_mode == "demo").count()
    if existing_count > 0:
        return existing_count

    today = date.today()
    start_date = today.replace(day=1) - timedelta(days=365 + 30)
    total_days = (today - start_date).days

    inserted = 0

    for cat_name, merchants in DEMO_MERCHANTS.items():
        freq_per_4_weeks = CATEGORY_FREQUENCY.get(cat_name, 2)
        total_txns = int(freq_per_4_weeks * total_days / 28)

        for _ in range(total_txns):
            merchant, mean_amt, std_amt = random.choice(merchants)
            amount = _lognormal_amount(mean_amt, std_amt)

            # Random date within the range, weighted toward recent
            days_offset = int(random.triangular(0, total_days, total_days))
            txn_date = start_date + timedelta(days=days_offset)

            description = merchant
            # Add unique salt so each demo transaction gets a distinct row_hash
            rh = compute_row_hash(str(txn_date), amount, description + "_demo_" + uuid.uuid4().hex[:8])
            existing = db.query(Transaction).filter(Transaction.row_hash == rh).first()
            if existing:
                continue

            category_id = categorize(description, db)

            txn = Transaction(
                date=txn_date,
                amount=amount,
                transaction_type="debit",
                description=description,
                raw_description=description,
                category_id=category_id,
                source="demo",
                data_mode="demo",
                file_hash=None,
                row_hash=rh,
            )
            db.add(txn)
            inserted += 1

    db.commit()
    return inserted
