import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models import Category, Transaction, IngestLog
from app.categorization.rules import DEFAULT_CATEGORIES
from app.categorization.engine import invalidate_cache

_tmp_db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp_db_file.close()
TEST_DB_URL = f"sqlite:///{_tmp_db_file.name}"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSession()
    for cat_data in DEFAULT_CATEGORIES:
        if not db.query(Category).filter(Category.name == cat_data["name"]).first():
            cat = Category(name=cat_data["name"], color=cat_data["color"])
            cat.set_keywords(cat_data["keywords"])
            db.add(cat)
    db.commit()
    db.close()
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()
    invalidate_cache()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def seed_transactions():
    from datetime import date
    db = TestingSession()
    for i in range(5):
        txn = Transaction(
            date=date(2025, 5, i + 1),
            amount=100.0 * (i + 1),
            transaction_type="debit",
            description=f"Test Transaction {i}",
            source="test",
            data_mode="real",
            row_hash=f"hash_{i}",
        )
        db.add(txn)
    db.commit()
    db.close()


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_list_categories(client):
    r = client.get("/api/categories")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == len(DEFAULT_CATEGORIES)
    assert all("name" in c and "color" in c and "keywords" in c for c in data)


def test_create_category(client):
    r = client.post("/api/categories", json={"name": "Test Cat", "color": "#ff0000", "keywords": ["testshop"]})
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Test Cat"
    assert "testshop" in data["keywords"]


def test_list_transactions_empty(client):
    r = client.get("/api/transactions?mode=real")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 0
    assert data["items"] == []


def test_list_transactions_with_data(client, seed_transactions):
    r = client.get("/api/transactions?mode=real")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 5
    assert len(data["items"]) == 5


def test_analytics_summary_empty(client):
    r = client.get("/api/analytics/summary?mode=real")
    assert r.status_code == 200
    data = r.json()
    assert data["total_spend"] == 0.0
    assert data["transaction_count"] == 0


def test_analytics_summary_with_data(client, seed_transactions):
    r = client.get("/api/analytics/summary?mode=real")
    assert r.status_code == 200
    data = r.json()
    assert data["total_spend"] == 1500.0  # 100+200+300+400+500
    assert data["transaction_count"] == 5


def test_analytics_by_month(client, seed_transactions):
    r = client.get("/api/analytics/by-month?mode=real")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["label"] == "2025-05"
    assert data[0]["total"] == 1500.0


def test_demo_generate_and_clear(client):
    r = client.post("/api/demo/generate")
    assert r.status_code == 200
    count = r.json()["transaction_count"]
    assert count > 0

    r2 = client.get("/api/transactions?mode=demo&page_size=1")
    assert r2.json()["total"] == count

    r3 = client.delete("/api/demo/clear")
    assert r3.status_code == 204

    r4 = client.get("/api/transactions?mode=demo&page_size=1")
    assert r4.json()["total"] == 0
