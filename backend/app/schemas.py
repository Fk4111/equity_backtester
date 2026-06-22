from pydantic import BaseModel
from typing import Optional, List
from datetime import date


# ---- Stock Schemas ----

class StockBase(BaseModel):
    symbol: str
    company_name: Optional[str] = None
    sector: Optional[str] = None


class StockOut(StockBase):
    id: int

    class Config:
        from_attributes = True


class FundamentalOut(BaseModel):
    market_cap: Optional[float]
    pe_ratio: Optional[float]
    roe: Optional[float]
    roce: Optional[float]
    pat: Optional[float]

    class Config:
        from_attributes = True


class StockWithFundamentals(StockOut):
    fundamentals: List[FundamentalOut] = []


# ---- Backtest Schemas ----

class BacktestRequest(BaseModel):
    """This is the payload the user sends from the frontend form."""
    start_date: date
    end_date: date
    capital: float                          # Starting capital in INR
    portfolio_size: int                     # Number of stocks to hold
    rebalance_frequency: str                # "monthly", "quarterly", "yearly"

    # Optional filters
    min_market_cap: Optional[float] = None  # In Crores
    max_market_cap: Optional[float] = None
    min_roce: Optional[float] = None
    pat_positive: bool = True               # Only include stocks with PAT > 0


class PortfolioLogOut(BaseModel):
    symbol: str
    rebalance_date: Optional[date]
    weight: Optional[float]
    return_percent: Optional[float]

    class Config:
        from_attributes = True


class BacktestResult(BaseModel):
    """This is what we send back to the frontend after running the backtest."""
    backtest_id: int
    start_date: date
    end_date: date
    initial_capital: float
    final_value: float
    cagr: float
    total_return: float
    sharpe_ratio: float
    max_drawdown: float

    # Equity curve: list of {date, value} points
    equity_curve: List[dict]

    # Drawdown series: list of {date, drawdown} points
    drawdown_series: List[dict]

    # Top performing and worst performing stocks
    top_winners: List[dict]
    top_losers: List[dict]

    # Full rebalance logs
    portfolio_logs: List[PortfolioLogOut]
