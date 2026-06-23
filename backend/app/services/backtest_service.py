import pandas as pd
import numpy as np
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session

from app.models import Stock, StockPrice, Fundamental, Backtest, PortfolioLog
from app.schemas import BacktestRequest
from app.services.metrics import (
    calculate_cagr,
    calculate_total_return,
    calculate_max_drawdown,
    calculate_sharpe_ratio,
    calculate_drawdown_series,
)


def get_rebalance_dates(start_date: date, end_date: date, frequency: str):
    """
    Generate a list of dates when we should rebalance the portfolio.
    
    frequency: "monthly", "quarterly", "yearly"
    """
    rebalance_dates = []
    current = start_date

    while current <= end_date:
        rebalance_dates.append(current)

        if frequency == "monthly":
            current = current + relativedelta(months=1)
        elif frequency == "quarterly":
            current = current + relativedelta(months=3)
        elif frequency == "yearly":
            current = current + relativedelta(years=1)
        else:
            # Default to monthly
            current = current + relativedelta(months=1)

    return rebalance_dates


def get_all_stock_prices(db: Session, symbols: list, start_date: date, end_date: date):
    """
    Fetch all price data for the given symbols in one query.
    Returns a dict: { "RELIANCE": DataFrame, "TCS": DataFrame, ... }
    """
    prices_by_symbol = {}

    for symbol in symbols:
        stock = db.query(Stock).filter(Stock.symbol == symbol).first()
        if not stock:
            continue

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
            continue

        data = [{"date": p.date, "close": p.close} for p in prices]
        df = pd.DataFrame(data).set_index("date")
        df = df[df["close"].notna()]  # Remove rows with missing close price

        if not df.empty:
            prices_by_symbol[symbol] = df

    return prices_by_symbol


def filter_and_rank_stocks(db: Session, request: BacktestRequest):
    """
    Step 1: Filter stocks based on user-defined criteria.
    Step 2: Rank the filtered stocks.
    Step 3: Return the top N symbols.

    We use fundamentals to filter & rank, and apply these same stocks
    for every rebalance period (no lookahead bias in stock selection).
    """

    # Start with all stocks that have fundamental data
    all_stocks = db.query(Stock).all()
    eligible = []

    for stock in all_stocks:
        # Get the most recent fundamental record
        fundamental = (
            db.query(Fundamental)
            .filter(Fundamental.stock_id == stock.id)
            .order_by(Fundamental.updated_at.desc())
            .first()
        )

        if not fundamental:
            continue

        # --- Apply Filters ---

        # Filter: PAT must be positive
        if request.pat_positive and (fundamental.pat is None or fundamental.pat <= 0):
            continue

        # Filter: Market cap range
        if request.min_market_cap is not None and fundamental.market_cap is not None:
            if fundamental.market_cap < request.min_market_cap:
                continue

        if request.max_market_cap is not None and fundamental.market_cap is not None:
            if fundamental.market_cap > request.max_market_cap:
                continue

        # Filter: Minimum ROCE
        if request.min_roce is not None and fundamental.roce is not None:
            if fundamental.roce < request.min_roce:
                continue

        # Passed all filters, add to eligible list
        eligible.append({
            "symbol": stock.symbol,
            "market_cap": fundamental.market_cap,
            "pe_ratio": fundamental.pe_ratio,
            "roe": fundamental.roe,
            "roce": fundamental.roce,
            "pat": fundamental.pat,
        })

    if not eligible:
        return []

    df = pd.DataFrame(eligible)

    # --- Ranking System ---
    # Rank by ROE descending (higher ROE is better, so rank 1 = highest)
    if "roe" in df.columns and df["roe"].notna().any():
        df["roe_rank"] = df["roe"].rank(ascending=False, na_option="bottom")
    else:
        df["roe_rank"] = len(df)

    # Rank by PE ascending (lower PE = cheaper, so rank 1 = lowest PE)
    if "pe_ratio" in df.columns and df["pe_ratio"].notna().any():
        df["pe_rank"] = df["pe_ratio"].rank(ascending=True, na_option="bottom")
    else:
        df["pe_rank"] = len(df)

    # Composite rank = average of individual ranks
    df["composite_rank"] = (df["roe_rank"] + df["pe_rank"]) / 2

    # Sort by composite rank (lower = better)
    df = df.sort_values("composite_rank", ascending=True)

    # Return top N symbols (portfolio size)
    top_n = df.head(request.portfolio_size)
    return top_n["symbol"].tolist()


def get_price_on_or_after(price_df: pd.DataFrame, target_date: date):
    """
    Helper to get the closing price on a given date.
    If that date doesn't have data (holiday, weekend), get the next available date.
    """
    # Filter for dates >= target_date
    df_after = price_df[price_df.index >= target_date]
    if df_after.empty:
        return None
    return float(df_after.iloc[0]["close"])


def run_backtest(db: Session, request: BacktestRequest):
    """
    Main backtest function. This runs the entire simulation.
    
    Steps:
    1. Filter and rank stocks
    2. For each rebalance period:
       a. Get stock prices at rebalance start
       b. Allocate equal capital to each stock
       c. At next rebalance, calculate portfolio value
    3. Build equity curve
    4. Calculate metrics
    """

    # Step 1: Get the list of selected stocks (same for all rebalances)
    selected_symbols = filter_and_rank_stocks(db, request)

    if not selected_symbols:
        raise ValueError("No stocks passed the filters. Try relaxing your filter criteria.")

    print(f"Selected {len(selected_symbols)} stocks: {selected_symbols}")

    # Step 2: Generate rebalance dates
    rebalance_dates = get_rebalance_dates(
        request.start_date, request.end_date, request.rebalance_frequency
    )

    # Step 3: Fetch all price data for selected stocks
    prices_by_symbol = get_all_stock_prices(
        db, selected_symbols, request.start_date, request.end_date
    )

    # Remove symbols that don't have price data
    valid_symbols = [s for s in selected_symbols if s in prices_by_symbol]
    print(f"Symbols with price data: {len(valid_symbols)}")

    if not valid_symbols:
        raise ValueError("Could not find price data for any selected stocks.")

    # Step 4: Run the simulation
    portfolio_value = request.capital  # Starting value
    equity_curve = []                  # Track portfolio value over time
    period_returns = []                # Track each period's return for Sharpe calculation
    all_logs = []                      # Track stock-level logs for the portfolio log table
    stock_total_returns = {}           # Track overall return for each stock

    # We track shares held in each stock
    holdings = {}  # { "RELIANCE": {"shares": X, "buy_price": Y} }

    for i, rebalance_date in enumerate(rebalance_dates):
        # Is there a next rebalance date?
        is_last_period = (i == len(rebalance_dates) - 1)
        next_date = rebalance_dates[i + 1] if not is_last_period else request.end_date

        # Equal weight: each stock gets same fraction
        weight_per_stock = 1.0 / len(valid_symbols)
        amount_per_stock = portfolio_value * weight_per_stock

        period_log = []

        # If we have existing holdings, calculate value before rebalancing
        if holdings:
            current_value = 0
            for sym, holding in holdings.items():
                if sym in prices_by_symbol:
                    price_now = get_price_on_or_after(prices_by_symbol[sym], rebalance_date)
                    if price_now:
                        current_value += holding["shares"] * price_now
            if current_value > 0:
                portfolio_value = current_value

        # Buy new portfolio at this rebalance date
        new_holdings = {}
        for sym in valid_symbols:
            if sym not in prices_by_symbol:
                continue

            buy_price = get_price_on_or_after(prices_by_symbol[sym], rebalance_date)
            if not buy_price or buy_price <= 0:
                continue

            shares = amount_per_stock / buy_price
            new_holdings[sym] = {"shares": shares, "buy_price": buy_price}

        holdings = new_holdings

        # Add equity curve point for this rebalance date
        equity_curve.append({
            "date": rebalance_date.strftime("%Y-%m-%d"),
            "value": round(portfolio_value, 2)
        })

        # Calculate returns for each stock over this period
        for sym, holding in holdings.items():
            if sym not in prices_by_symbol:
                continue

            sell_price = get_price_on_or_after(prices_by_symbol[sym], next_date)
            if not sell_price:
                sell_price = holding["buy_price"]  # No change if no data

            period_return = ((sell_price - holding["buy_price"]) / holding["buy_price"]) * 100

            # Accumulate total return for this stock
            if sym not in stock_total_returns:
                stock_total_returns[sym] = []
            stock_total_returns[sym].append(period_return)

            period_log.append({
                "symbol": sym,
                "rebalance_date": rebalance_date,
                "weight": round(weight_per_stock * 100, 2),
                "return_percent": round(period_return, 2),
            })

        all_logs.extend(period_log)

        # Calculate portfolio return for this period (equal-weighted average)
        if period_log:
            avg_period_return = np.mean([p["return_percent"] for p in period_log])
            period_returns.append(avg_period_return)
            portfolio_value = portfolio_value * (1 + avg_period_return / 100)

    # Step 5: Add final equity curve point
    equity_curve.append({
        "date": request.end_date.strftime("%Y-%m-%d"),
        "value": round(portfolio_value, 2)
    })

    # Step 6: Calculate all performance metrics
    years = (request.end_date - request.start_date).days / 365.25
    equity_values = [point["value"] for point in equity_curve]

    cagr = float(calculate_cagr(request.capital, portfolio_value, years))
    total_return = float(calculate_total_return(request.capital, portfolio_value))
    max_drawdown = float(calculate_max_drawdown(equity_values))
    sharpe = float(calculate_sharpe_ratio(period_returns))
    drawdown_series = calculate_drawdown_series(equity_curve)

    # Step 7: Find top winners and losers
    avg_returns = {
        sym: round(np.mean(returns), 2)
        for sym, returns in stock_total_returns.items()
    }

    sorted_returns = sorted(avg_returns.items(), key=lambda x: x[1], reverse=True)
    top_winners = [{"symbol": s, "return_percent": r} for s, r in sorted_returns[:5]]
    top_losers = [{"symbol": s, "return_percent": r} for s, r in sorted_returns[-5:]]

    portfolio_value = float(portfolio_value)

    print("TYPE CHECK")
    print(type(portfolio_value))
    print(type(cagr))
    print(type(total_return))
    print(type(sharpe))
    print(type(max_drawdown))
      

        
    # Step 8: Save backtest to database
    backtest_record = Backtest(
        start_date=request.start_date,
        end_date=request.end_date,
        capital=request.capital,
        rebalance_frequency=request.rebalance_frequency,
        portfolio_size=request.portfolio_size,
        min_market_cap=request.min_market_cap,
        max_market_cap=request.max_market_cap,
        min_roce=request.min_roce,
        pat_positive=1 if request.pat_positive else 0,
        final_value=round(portfolio_value, 2),
        cagr=cagr,
        total_return=total_return,
        sharpe_ratio=sharpe,
        max_drawdown=max_drawdown,
    )
    db.add(backtest_record)
    db.flush()  # Get the backtest ID

    # Save portfolio logs
    for log in all_logs:
        log_record = PortfolioLog(
            backtest_id=backtest_record.id,
            rebalance_date=log["rebalance_date"],
            symbol=log["symbol"],
            weight=log["weight"],
            return_percent=log["return_percent"],
        )
        db.add(log_record)
        
        print(type(portfolio_value))
        print(type(cagr))
        print(type(total_return))
        print(type(sharpe))
        print(type(max_drawdown))
        print(portfolio_value)
        print(cagr)
        print(total_return)
        print(sharpe)
        print(max_drawdown)

    db.commit()

    # Step 9: Return all results
    return {
        "backtest_id": backtest_record.id,
        "start_date": request.start_date,
        "end_date": request.end_date,
        "initial_capital": request.capital,
        "final_value": round(portfolio_value, 2),
        "cagr": cagr,
        "total_return": total_return,
        "sharpe_ratio": sharpe,
        "max_drawdown": max_drawdown,
        "equity_curve": equity_curve,
        "drawdown_series": drawdown_series,
        "top_winners": top_winners,
        "top_losers": top_losers,
        "portfolio_logs": [
            {
                "symbol": log["symbol"],
                "rebalance_date": log["rebalance_date"],
                "weight": log["weight"],
                "return_percent": log["return_percent"],
            }
            for log in all_logs
        ],
    }
