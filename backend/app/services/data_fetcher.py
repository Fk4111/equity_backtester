
import yfinance as yf
import pandas as pd
from sqlalchemy.orm import Session
from app.models import Stock, StockPrice, Fundamental
import time

# Keep only a few stocks for demo/testing
INDIAN_STOCKS = [
    "RELIANCE.NS",
    "TCS.NS",
    "HDFCBANK.NS",
    "INFY.NS",
    "HINDUNILVR.NS",
]


def fetch_and_save_all_stocks(db: Session):
    """
    Fetch stock price history from Yahoo Finance
    and store it in PostgreSQL.
    """

    print(f"Starting data fetch for {len(INDIAN_STOCKS)} stocks...")

    success_count = 0
    fail_count = 0

    for symbol in INDIAN_STOCKS:
        try:
            print(f"Fetching: {symbol}")

            clean_symbol = symbol.replace(".NS", "")

            # Check if stock already exists
            stock = (
                db.query(Stock)
                .filter(Stock.symbol == clean_symbol)
                .first()
            )

            if not stock:
                stock = Stock(
                    symbol=clean_symbol,
                    company_name=clean_symbol,
                    sector="Unknown"
                )
                db.add(stock)
                db.flush()

            # Download historical data
            hist = yf.download(
                symbol,
                period="5y",
                progress=False,
                auto_adjust=True,
                threads=False
            )

            if hist.empty:
                print(f"No price data found for {symbol}")
                fail_count += 1
                continue

            # Remove old prices
            db.query(StockPrice).filter(
                StockPrice.stock_id == stock.id
            ).delete()

            # Save price history
            for date_idx, row in hist.iterrows():

                price = StockPrice(
                    stock_id=stock.id,
                    date=date_idx.date(),
                    open=float(row["Open"]) if not pd.isna(row["Open"]) else None,
                    high=float(row["High"]) if not pd.isna(row["High"]) else None,
                    low=float(row["Low"]) if not pd.isna(row["Low"]) else None,
                    close=float(row["Close"]) if not pd.isna(row["Close"]) else None,
                    volume=float(row["Volume"]) if not pd.isna(row["Volume"]) else None,
                )

                db.add(price)

            # Remove old fundamentals
            db.query(Fundamental).filter(
                Fundamental.stock_id == stock.id
            ).delete()

            # Dummy fundamentals
            fundamental = Fundamental(
                stock_id=stock.id,
                market_cap=None,
                pe_ratio=None,
                roe=None,
                roce=None,
                pat=None,
            )

            db.add(fundamental)

            # Commit after every stock
            db.commit()

            success_count += 1

            print(f"Saved: {symbol}")

            # Prevent Yahoo rate limiting
            time.sleep(2)

        except Exception as e:
            db.rollback()
            fail_count += 1
            print(f"Error fetching {symbol}: {e}")

    print(
        f"Done! Success: {success_count}, Failed: {fail_count}"
    )

    return {
        "success": success_count,
        "failed": fail_count
    }


def get_stock_prices_df(db: Session, symbol: str, start_date, end_date):
    """
    Return stock prices as pandas DataFrame
    for backtesting.
    """

    stock = (
        db.query(Stock)
        .filter(Stock.symbol == symbol)
        .first()
    )

    if not stock:
        return pd.DataFrame()

    prices = (
        db.query(StockPrice)
        .filter(
            StockPrice.stock_id == stock.id,
            StockPrice.date >= start_date,
            StockPrice.date <= end_date,
        )
        .order_by(StockPrice.date)
        .all()
    )

    if not prices:
        return pd.DataFrame()

    data = [
        {
            "date": p.date,
            "open": p.open,
            "high": p.high,
            "low": p.low,
            "close": p.close,
            "volume": p.volume,
        }
        for p in prices
    ]

    df = pd.DataFrame(data)
    df.set_index("date", inplace=True)

    return df

