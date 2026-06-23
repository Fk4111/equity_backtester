# Equity Backtester Documentation

## Project Overview

Equity Backtester is a full-stack web application that allows users to fetch stock market data, apply fundamental filters, rank stocks, and run historical backtests on custom investment strategies.

The platform consists of:

* React + Tailwind CSS Frontend
* FastAPI Backend
* PostgreSQL Database
* Yahoo Finance Data Integration

---

# Architecture

Frontend (React)
↓
FastAPI Backend
↓
SQLAlchemy ORM
↓
PostgreSQL Database

External Data Source:
Yahoo Finance (yfinance)

---

# Modules

## 1. Data Collection Module

Purpose:
Fetch historical stock data and store it in the database.

Technology:

* yfinance
* pandas

Features:

* Downloads OHLCV data
* Supports Indian NSE stocks
* Stores historical prices
* Prevents duplicate stock entries

Main File:
app/services/data_fetcher.py

---

## 2. Database Module

Database:
PostgreSQL

Tables:

### stocks

Stores stock master information.

Fields:

* id
* symbol
* company_name
* sector

### stock_prices

Stores daily historical stock prices.

Fields:

* stock_id
* date
* open
* high
* low
* close
* volume

### fundamentals

Stores valuation and profitability metrics.

Fields:

* market_cap
* pe_ratio
* roe
* roce
* pat

### backtests

Stores executed backtests and summary metrics.

Fields:

* start_date
* end_date
* capital
* portfolio_size
* rebalance_frequency
* final_value
* cagr
* sharpe_ratio
* max_drawdown

### portfolio_logs

Stores stock selections for each rebalance period.

---

## 3. Backtesting Engine

Purpose:
Simulate historical investment performance.

Features:

* User-defined date range
* Monthly / Quarterly / Yearly rebalance
* Portfolio size selection
* Fundamental filtering
* Composite ranking
* Capital compounding

Process:

1. Apply filters
2. Rank stocks
3. Select top stocks
4. Calculate portfolio return
5. Rebalance periodically
6. Generate performance metrics

Main File:
app/routes/backtest.py

---

## 4. Ranking Logic

Stocks are ranked using:

* ROE (higher is better)
* PE Ratio (lower is better)

Composite Rank:

Final Rank = Average of Individual Ranks

Top ranked stocks are selected for the portfolio.

---

## 5. Performance Metrics

The application calculates:

### CAGR

Compound Annual Growth Rate

### Total Return

Percentage growth from initial capital

### Sharpe Ratio

Risk-adjusted return metric

### Maximum Drawdown

Largest decline from peak portfolio value

---

## 6. Frontend

Technology:

* React
* React Router
* Axios
* Tailwind CSS

Pages:

### Stocks Page

Features:

* Fetch stock data
* Search stocks
* View fundamentals

### Backtest Page

Features:

* Configure strategy
* Run backtest

### Results Page

Displays:

* Equity Curve
* Performance Metrics
* Winners and Losers
* Portfolio Logs
* CSV Export

---

## API Endpoints

### Stocks

GET /api/stocks/

Returns all stocks.

GET /api/stocks/count/total

Returns total stock count.

POST /api/stocks/fetch

Fetches stock data from Yahoo Finance.

---

### Backtest

POST /api/backtest/run

Runs a backtest strategy.

GET /api/backtest/{id}

Returns saved backtest details.

GET /api/backtest/history/all

Returns backtest history.

GET /api/backtest/{id}/export/csv

Exports results as CSV.

---

## Assumptions

* Yahoo Finance data is used as the primary data source.
* Historical data availability depends on Yahoo Finance.
* Missing fundamental values are ignored during ranking.
* Equal-weight portfolio allocation is used.

---

## Future Improvements

* Nifty 50 benchmark comparison
* Advanced portfolio weighting
* Strategy comparison
* Authentication system
* Scheduled data updates
* Interactive charts
* Excel export support

---

## Tech Stack

Frontend:

* React
* Tailwind CSS
* Axios

Backend:

* FastAPI
* SQLAlchemy
* Pandas
* NumPy

Database:

* PostgreSQL

Data Source:

* Yahoo Finance

Author:
Faiyaz Khan
