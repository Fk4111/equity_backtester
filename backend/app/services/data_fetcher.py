import yfinance as yf
import pandas as pd
from sqlalchemy.orm import Session
from app.models import Stock, StockPrice, Fundamental
import time

# List of 100+ Indian stocks (NSE symbols with .NS suffix for yfinance)
INDIAN_STOCKS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS",
    # "ICICIBANK.NS", "HDFCLIFE.NS", "KOTAKBANK.NS", "BHARTIARTL.NS", "ITC.NS",
    # "AXISBANK.NS", "SBIN.NS", "LT.NS", "MARUTI.NS", "HCLTECH.NS",
    # "SUNPHARMA.NS", "WIPRO.NS", "ULTRACEMCO.NS", "TITAN.NS", "ASIANPAINT.NS",
    # "TECHM.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "NTPC.NS", "POWERGRID.NS",
    # "M&M.NS", "TATAMTRDVR.NS", "ONGC.NS", "TATASTEEL.NS", "JSWSTEEL.NS",
    # "COALINDIA.NS", "NESTLEIND.NS", "DIVISLAB.NS", "DRREDDY.NS", "CIPLA.NS",
    # "ADANIENT.NS", "ADANIPORTS.NS", "ADANIGREEN.NS", "HDFCLIFE.NS", "SBILIFE.NS",
    # "GRASIM.NS", "INDUSINDBK.NS", "PIDILITIND.NS", "DMART.NS", "HEROMOTOCO.NS",
    # "EICHERMOT.NS", "BPCL.NS", "IOC.NS", "HINDALCO.NS", "VEDL.NS",
    # "TATACONSUM.NS", "BRITANNIA.NS", "UPL.NS", "SHREECEM.NS", "AMBUJACEM.NS",
    # "BALKRISIND.NS", "HAVELLS.NS", "LUPIN.NS", "AUROPHARMA.NS", "TORNTPHARM.NS",
    # "MUTHOOTFIN.NS", "BAJAJ-AUTO.NS", "TVSMOTOR.NS", "CHOLAFIN.NS", "MOTHERSON.NS",
    # "MARICO.NS", "DABUR.NS", "GODREJCP.NS", "COLPAL.NS", "EMAMILTD.NS",
    # "VOLTAS.NS", "WHIRLPOOL.NS", "BERGEPAINT.NS", "KANSAINER.NS", "AKZOINDIA.NS",
    # "ABB.NS", "SIEMENS.NS", "HONAUT.NS", "CUMMINSIND.NS", "THERMAX.NS",
    # "MPHASIS.NS", "LTTS.NS", "COFORGE.NS", "PERSISTENT.NS", "OFSS.NS",
    # "NAUKRI.NS", "JUSTDIAL.NS", "IRCTC.NS", "ZOMATO.NS", "POLICYBZR.NS",
    # "NYKAA.NS", "PAYTM.NS", "DELHIVERY.NS", "CARTRADE.NS", "NAZARA.NS",
    # "GMRINFRA.NS", "IRB.NS", "ASHOKLEY.NS", "TATAPOWER.NS", "CESC.NS",
    # "PFC.NS", "RECLTD.NS", "IRFC.NS", "BANKINDIA.NS", "CANBK.NS",
    # "UNIONBANK.NS", "FEDERALBNK.NS", "IDFCFIRSTB.NS", "BANDHANBNK.NS", "RBLBANK.NS",
]


def fetch_and_save_all_stocks(db: Session):
    """
    Main function to fetch stock data from yfinance and save to database.
    Fetches basic info, price history, and fundamental metrics.
    """
    print(f"Starting data fetch for {len(INDIAN_STOCKS)} stocks...")

    success_count = 0
    fail_count = 0

    for symbol in INDIAN_STOCKS:
        try:
            print(f"Fetching: {symbol}")

            # Download ticker info from Yahoo Finance
            ticker = yf.Ticker(symbol)
            info = ticker.info

            # Clean symbol (remove .NS for display)
            clean_symbol = symbol.replace(".NS", "")

            # Check if stock already exists in database
            existing_stock = db.query(Stock).filter(Stock.symbol == clean_symbol).first()

            if existing_stock:
                stock = existing_stock
            else:
                # Create new stock entry
                stock = Stock(
                    symbol=clean_symbol,
                    company_name=info.get("longName", clean_symbol),
                    sector=info.get("sector", "Unknown")
                )
                db.add(stock)
                db.flush()  # Get the stock ID before adding related records

            # Fetch historical price data (last 5 years)
            hist = ticker.history(period="5y")

            if hist.empty:
                print(f"  No price data for {symbol}, skipping...")
                fail_count += 1
                continue

            # Delete old price data for this stock and re-insert
            db.query(StockPrice).filter(StockPrice.stock_id == stock.id).delete()

            # Save each day's OHLCV data
            for date_idx, row in hist.iterrows():
                price_record = StockPrice(
                    stock_id=stock.id,
                    date=date_idx.date(),
                    open=round(float(row["Open"]), 2) if not pd.isna(row["Open"]) else None,
                    high=round(float(row["High"]), 2) if not pd.isna(row["High"]) else None,
                    low=round(float(row["Low"]), 2) if not pd.isna(row["Low"]) else None,
                    close=round(float(row["Close"]), 2) if not pd.isna(row["Close"]) else None,
                    volume=float(row["Volume"]) if not pd.isna(row["Volume"]) else None,
                )
                db.add(price_record)

            # Save fundamental data
            # Market cap from yfinance is in INR, we convert to Crores
            market_cap_raw = info.get("marketCap", None)
            market_cap_crores = round(market_cap_raw / 1e7, 2) if market_cap_raw else None

            # Delete old fundamental data
            db.query(Fundamental).filter(Fundamental.stock_id == stock.id).delete()

            fundamental = Fundamental(
                stock_id=stock.id,
                market_cap=market_cap_crores,
                pe_ratio=info.get("trailingPE", None),
                roe=round(info.get("returnOnEquity", 0) * 100, 2) if info.get("returnOnEquity") else None,
                # ROCE is not directly in yfinance - we approximate from EBIT/Capital Employed
                # Using returnOnAssets as a proxy when ROCE isn't available
                roce=round(info.get("returnOnAssets", 0) * 100, 2) if info.get("returnOnAssets") else None,
                # PAT = net income in Crores
                pat=round(info.get("netIncomeToCommon", 0) / 1e7, 2) if info.get("netIncomeToCommon") else None,
            )
            db.add(fundamental)

            # Commit every 10 stocks to avoid large transactions
            if (success_count + 1) % 10 == 0:
                db.commit()
                print(f"  Committed {success_count + 1} stocks so far...")

            success_count += 1

            # Be polite to Yahoo Finance API - don't hammer it
            time.sleep(0.5)

        except Exception as e:
            print(f"  Error fetching {symbol}: {str(e)}")
            fail_count += 1
            db.rollback()
            continue

    # Final commit
    db.commit()
    print(f"\nDone! Success: {success_count}, Failed: {fail_count}")
    return {"success": success_count, "failed": fail_count}


def get_stock_prices_df(db: Session, symbol: str, start_date, end_date):
    """
    Returns a pandas DataFrame of price data for a given stock and date range.
    This is used by the backtest engine.
    """
    stock = db.query(Stock).filter(Stock.symbol == symbol).first()
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

    # Build a simple DataFrame from the ORM objects
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
