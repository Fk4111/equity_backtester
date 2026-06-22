from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Stock(Base):
    """Stores basic info about each stock."""
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), unique=True, index=True, nullable=False)
    company_name = Column(String(200), nullable=True)
    sector = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships to other tables
    prices = relationship("StockPrice", back_populates="stock")
    fundamentals = relationship("Fundamental", back_populates="stock")


class StockPrice(Base):
    """Stores daily OHLCV price data for each stock."""
    __tablename__ = "stock_prices"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    open = Column(Float, nullable=True)
    high = Column(Float, nullable=True)
    low = Column(Float, nullable=True)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=True)

    stock = relationship("Stock", back_populates="prices")


class Fundamental(Base):
    """Stores fundamental financial data for each stock."""
    __tablename__ = "fundamentals"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)

    # Valuation
    market_cap = Column(Float, nullable=True)   # In Crores (INR)
    pe_ratio = Column(Float, nullable=True)     # Price-to-Earnings ratio

    # Profitability
    roe = Column(Float, nullable=True)          # Return on Equity (%)
    roce = Column(Float, nullable=True)         # Return on Capital Employed (%)
    pat = Column(Float, nullable=True)          # Profit After Tax (in Crores)

    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    stock = relationship("Stock", back_populates="fundamentals")


class Backtest(Base):
    """Stores backtest configuration and summary results."""
    __tablename__ = "backtests"

    id = Column(Integer, primary_key=True, index=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    capital = Column(Float, nullable=False)
    rebalance_frequency = Column(String(20), nullable=False)  # monthly, quarterly, yearly
    portfolio_size = Column(Integer, nullable=False)

    # Filter settings (stored as JSON strings for simplicity)
    min_market_cap = Column(Float, nullable=True)
    max_market_cap = Column(Float, nullable=True)
    min_roce = Column(Float, nullable=True)
    pat_positive = Column(Integer, default=1)   # 1 = filter for positive PAT

    # Results summary
    final_value = Column(Float, nullable=True)
    cagr = Column(Float, nullable=True)
    total_return = Column(Float, nullable=True)
    sharpe_ratio = Column(Float, nullable=True)
    max_drawdown = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to portfolio logs
    logs = relationship("PortfolioLog", back_populates="backtest")


class PortfolioLog(Base):
    """Stores stock-level portfolio details for each rebalance period."""
    __tablename__ = "portfolio_logs"

    id = Column(Integer, primary_key=True, index=True)
    backtest_id = Column(Integer, ForeignKey("backtests.id"), nullable=False)
    rebalance_date = Column(Date, nullable=True)
    symbol = Column(String(20), nullable=False)
    weight = Column(Float, nullable=True)           # % of portfolio
    return_percent = Column(Float, nullable=True)   # Return during this period

    backtest = relationship("Backtest", back_populates="logs")
