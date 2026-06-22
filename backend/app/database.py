from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os

# Read database URL from environment variable
# Uses local PostgreSQL when running on your machine
# Uses Render PostgreSQL when deployed
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres123@localhost:5432/equity_backtester"
)

# Create database engine
engine = create_engine(DATABASE_URL)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for all models
class Base(DeclarativeBase):
    pass


def get_db():
    """
    FastAPI dependency that provides a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()