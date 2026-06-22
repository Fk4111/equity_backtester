import time
import yfinance as yf
import pandas as pd
from sqlalchemy.orm import Session

from app.models import Stock, StockPrice, Fundamental


INDIAN_STOCKS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS",
    "ICICIBANK.NS", "HDFCLIFE.NS", "KOTAKBANK.NS", "BHARTIARTL.NS", "ITC.NS",
    "AXISBANK.NS", "SBIN.NS", "LT.NS", "MARUTI.NS", "HCLTECH.NS",
    "SUNPHARMA.NS", "WIPRO.NS", "ULTRACEMCO.NS", "TITAN.NS", "ASIANPAINT.NS",
    "TECHM.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "NTPC.NS", "POWERGRID.NS",
    "M&M.NS", "TATAMTRDVR.NS", "ONGC.NS", "TATASTEEL.NS", "JSWSTEEL.NS",
    "COALINDIA.NS", "NESTLEIND.NS", "DIVISLAB.NS", "DRREDDY.NS", "CIPLA.NS",
    "ADANIENT.NS", "ADANIPORTS.NS", "ADANIGREEN.NS", "HDFCLIFE.NS", "SBILIFE.NS",
    "GRASIM.NS", "INDUSINDBK.NS", "PIDILITIND.NS", "DMART.NS", "HEROMOTOCO.NS",
    "EICHERMOT.NS", "BPCL.NS", "IOC.NS", "HINDALCO.NS", "VEDL.NS",
    "TATACONSUM.NS", "BRITANNIA.NS", "UPL.NS", "SHREECEM.NS", "AMBUJACEM.NS",
    "BALKRISIND.NS", "HAVELLS.NS", "LUPIN.NS", "AUROPHARMA.NS", "TORNTPHARM.NS",
    "MUTHOOTFIN.NS", "BAJAJ-AUTO.NS", "TVSMOTOR.NS", "CHOLAFIN.NS", "MOTHERSON.NS",
    "MARICO.NS", "DABUR.NS", "GODREJCP.NS", "COLPAL.NS", "EMAMILTD.NS",
    "VOLTAS.NS", "WHIRLPOOL.NS", "BERGEPAINT.NS", "KANSAINER.NS", "AKZOINDIA.NS",
    "ABB.NS", "SIEMENS.NS", "HONAUT.NS", "CUMMINSIND.NS", "THERMAX.NS",
    "MPHASIS.NS", "LTTS.NS", "COFORGE.NS", "PERSISTENT.NS", "OFSS.NS",
    "NAUKRI.NS", "JUSTDIAL.NS", "IRCTC.NS", "ZOMATO.NS", "POLICYBZR.NS",
    "NYKAA.NS", "PAYTM.NS", "DELHIVERY.NS", "CARTRADE.NS", "NAZARA.NS",
    "GMRINFRA.NS", "IRB.NS", "ASHOKLEY.NS", "TATAPOWER.NS", "CESC.NS",
    "PFC.NS", "RECLTD.NS", "IRFC.NS", "BANKINDIA.NS", "CANBK.NS",
    "UNIONBANK.NS", "FEDERALBNK.NS", "IDFCFIRSTB.NS", "BANDHANBNK.NS", "RBLBANK.NS",
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

            # Handle MultiIndex returned by newer yfinance versions
            if isinstance(hist.columns, pd.MultiIndex):
                hist.columns = hist.columns.get_level_values(0)

            # Remove old prices
            db.query(StockPrice).filter(
                StockPrice.stock_id == stock.id
            ).delete()

            # Save price history
            for date_idx, row in hist.iterrows():
                price = StockPrice(
                    stock_id=stock.id,
                    date=date_idx.date(),
                    open=float(row["Open"]) if pd.notna(row["Open"]) else None,
                    high=float(row["High"]) if pd.notna(row["High"]) else None,
                    low=float(row["Low"]) if pd.notna(row["Low"]) else None,
                    close=float(row["Close"]) if pd.notna(row["Close"]) else None,
                    volume=float(row["Volume"]) if pd.notna(row["Volume"]) else None,
                )

                db.add(price)

            # Remove old fundamentals
            db.query(Fundamental).filter(
                Fundamental.stock_id == stock.id
            ).delete()

            # Placeholder fundamentals
            fundamental = Fundamental(
                stock_id=stock.id,
                market_cap=None,
                pe_ratio=None,
                roe=None,
                roce=None,
                pat=None,
            )

            db.add(fundamental)

            db.commit()

            success_count += 1
            print(f"Saved: {symbol}")

            # Avoid Yahoo rate limits
            time.sleep(2)

        except Exception as e:
            db.rollback()
            fail_count += 1
            print(f"Error fetching {symbol}: {e}")

    print(f"Done! Success: {success_count}, Failed: {fail_count}")

    return {
        "success": success_count,
        "failed": fail_count
    }


def get_stock_prices_df(
    db: Session,
    symbol: str,
    start_date,
    end_date
):
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