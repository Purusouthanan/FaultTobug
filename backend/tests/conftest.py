"""
Shared pytest configuration for all test modules.

Strategy:
1. Create the in-memory test engine first.
2. Import and patch `backend.app.database.engine` to point at test_engine BEFORE
   importing main.py — this means main.py's module-level `create_all(bind=engine)`
   hits the in-memory DB automatically.
3. Register the DB dependency override immediately.
4. Seed once before any tests run.
"""
import sys
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

# ---------------------------------------------------------------------------
# Step 1 — Build in-memory test engine
# Use a named shared-cache memory URL so that ALL connections in this process
# share the SAME in-memory database (regular :memory: creates a fresh, empty DB
# per connection, so tables created in one connection are invisible in another).
# ---------------------------------------------------------------------------
TEST_DATABASE_URL = "sqlite:///file:testdb?mode=memory&cache=shared&uri=true"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False, "uri": True},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Yield a DB session connected to the in-memory test DB."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Step 2 — Import database module and patch engine before app loads
# ---------------------------------------------------------------------------
import backend.app.database as _db_module
_db_module.engine = test_engine                          # replace file-backed engine
_db_module.SessionLocal = TestingSessionLocal            # replace session factory

# Import models to register them with Base (populates Base.metadata.tables)
import backend.app.models as _models  # noqa: F401

# Create all tables in the in-memory DB
_db_module.Base.metadata.create_all(bind=test_engine)

# ---------------------------------------------------------------------------
# Step 3 — Import app (main.py's create_all now hits test_engine via patched module)
# ---------------------------------------------------------------------------
from backend.app.main import app
from backend.app.database import get_db

# Override FastAPI's DB dependency
app.dependency_overrides[get_db] = override_get_db


# ---------------------------------------------------------------------------
# Step 4 — Seed test data once
# ---------------------------------------------------------------------------
def _seed():
    from datetime import date
    db = TestingSessionLocal()
    try:
        if db.query(_models.User).first():
            return  # already seeded

        db.add_all([
            _models.User(username="admin",     hashed_password="ignored", role="Admin"),
            _models.User(username="dr_smith",  hashed_password="ignored", role="Doctor"),
            _models.User(username="nurse_joy", hashed_password="ignored", role="Nurse"),
        ])
        db.commit()

        p1 = _models.Patient(name="John Doe", dob=date(1980, 5, 15), status="Admitted")
        p2 = _models.Patient(name="Jane Roe", dob=date(1992, 11, 23), status="Discharged")
        db.add_all([p1, p2])
        db.commit()
        db.refresh(p1)
        db.refresh(p2)

        db.add_all([
            _models.Prescription(patient_id=p1.id, medication="Amoxicillin",
                                 instructions="500mg every 8 hours"),
            _models.Prescription(patient_id=p2.id, medication="Ibuprofen",
                                 instructions="400mg as needed"),
        ])
        db.commit()
    finally:
        db.close()


_seed()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def client():
    """Session-scoped TestClient wired to the in-memory test DB."""
    with TestClient(app) as c:
        yield c
