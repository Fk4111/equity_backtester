from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os

# Read database URL from environment variable, fallback to local default
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres123@localhost:5432/equity_backtester"
)

# Create the database engine
engine = create_engine(DATABASE_URL)

# Session factory - used to get a database session in routes
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models
class Base(DeclarativeBase):
    pass



url = "postgresql+psycopg2://postgres:postgres123@localhost:5432/equity_backtester"
test_engine = create_engine(url)

from sqlalchemy import text
with test_engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
    print(result)
    
def get_db():
    """
    Dependency function that yields a database session.
    FastAPI calls this automatically for routes that need 'db'.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        