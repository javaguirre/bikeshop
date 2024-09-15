import os
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bicycle_shop.db")
SQLALCHEMY_DATABASE_OPTIONS = json.dumps(
    os.getenv("DATABASE_OPTIONS", "{ 'check_same_thread': false }")
)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args=SQLALCHEMY_DATABASE_OPTIONS
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
