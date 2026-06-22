from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Stock, Fundamental
from app.schemas import StockOut, StockWithFundamentals
from app.services.data_fetcher import fetch_and_save_all_stocks
from typing import List

router = APIRouter()


@router.get("/", response_model=List[StockWithFundamentals])
def get_all_stocks(db: Session = Depends(get_db)):
    """
    Returns all stocks in the database along with their fundamental data.
    """
    stocks = db.query(Stock).all()
    return stocks


@router.get("/{symbol}", response_model=StockWithFundamentals)
def get_stock(symbol: str, db: Session = Depends(get_db)):
    """
    Returns a single stock with its fundamental data.
    """
    stock = db.query(Stock).filter(Stock.symbol == symbol.upper()).first()
    if not stock:
        raise HTTPException(status_code=404, detail=f"Stock '{symbol}' not found")
    return stock


@router.post("/fetch")
def trigger_data_fetch(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Triggers a background job to fetch all Indian stock data from Yahoo Finance.
    This can take several minutes - it runs in the background.
    """
    fetch_and_save_all_stocks(db)
    return {
        "message": "Data fetch started in the background. This will take a few minutes.",
        "note": "Check your terminal logs to see progress."
    }


@router.get("/count/total")
def get_stock_count(db: Session = Depends(get_db)):
    """Returns how many stocks are in the database."""
    count = db.query(Stock).count()
    return {"total_stocks": count}
