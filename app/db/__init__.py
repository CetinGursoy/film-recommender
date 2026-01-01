from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

import os

# Get DATABASE_URL from env, default to SQLite for local dev
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app/movies.db")

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# ✔ ROUTER'LARIN KULLANACAĞI DOĞRU get_db FONKSİYONU

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
