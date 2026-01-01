import os
import sys
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ---------------------------
# PYTHONPATH FIX
# ---------------------------
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.main import app
from app.database import Base, get_db


# ---------------------------
# TEST DATABASE
# ---------------------------
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ---------------------------
# HER TEST ÖNCESİ SIFIR TABLO
# ---------------------------
@pytest.fixture(autouse=True)
def reset_tables():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


# ---------------------------
# OVERRIDE get_db
# ---------------------------
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# ⭐ override burada yapılıyor
app.dependency_overrides[get_db] = override_get_db
