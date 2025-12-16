"""
Database utility module for setting up SQLAlchemy engine and session.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.app.utils.config import settings

DATABASE_URL = settings.DATABASE_URL

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the configuration.")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

def get_db():
    """
    Use this dependency in FastAPI routes to get a database session.
    Yields a SQLAlchemy session and ensures it is closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

