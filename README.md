# 📈 Equity Backtester

A full-stack backtesting platform for fundamental equity strategies on Indian (NSE) stocks.

Built with **FastAPI + PostgreSQL** on the backend and **React + Tailwind + Recharts** on the frontend.

---

## 🚀 Features

- Filter stocks by Market Cap, ROCE, and PAT
- Rank stocks by ROE (descending) and PE Ratio (ascending) using composite ranking
- Equal-weight portfolio allocation
- Monthly / Quarterly / Yearly rebalancing
- No future data leakage (prices are fetched strictly up to each rebalance date)
- Metrics: CAGR, Total Return, Sharpe Ratio, Max Drawdown
- Interactive equity curve and drawdown charts
- Portfolio logs table per rebalance period
- CSV export of portfolio logs
- 100+ Indian NSE stocks via Yahoo Finance

---

## 🗂️ Project Structure

```
equity-backtester/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── database.py          # SQLAlchemy engine and session
│   │   ├── models.py            # ORM table definitions
│   │   ├── schemas.py           # Pydantic request/response models
│   │   ├── services/
│   │   │   ├── data_fetcher.py  # Fetches data from Yahoo Finance
│   │   │   ├── backtest_service.py  # Core backtest engine
│   │   │   └── metrics.py       # CAGR, Sharpe, Drawdown calculations
│   │   └── routes/
│   │       ├── stocks.py        # Stock-related API endpoints
│   │       └── backtest.py      # Backtest run + result endpoints
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── HomePage.jsx
│   │   │   ├── BacktestPage.jsx   # Strategy configuration form
│   │   │   ├── ResultsPage.jsx    # Charts + metrics + logs
│   │   │   └── StocksPage.jsx     # Browse stocks, trigger fetch
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   ├── MetricCard.jsx
│   │   │   ├── EquityChart.jsx
│   │   │   ├── DrawdownChart.jsx
│   │   │   └── PortfolioLogsTable.jsx
│   │   ├── services/
│   │   │   └── api.js            # Axios API calls
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
├── docker-compose.yml
└── README.md
```

---

## ⚙️ Setup Instructions

### Option 1: Using Docker (Recommended)

**Prerequisites:** Docker and Docker Compose installed.

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd equity-backtester

# 2. Start PostgreSQL and backend
docker-compose up -d

# 3. Install and run the frontend
cd frontend
npm install
npm run dev
```

The app will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

### Option 2: Manual Setup

**Prerequisites:** Python 3.10+, Node.js 18+, PostgreSQL running locally.

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set your database URL
cp .env.example .env
# Edit .env with your PostgreSQL credentials

# Run the server
uvicorn app.main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## 📦 Fetching Stock Data

Once the backend is running, go to **Stocks** page in the UI and click **"Fetch Fresh Data"**.

Or call the API directly:

```bash
curl -X POST http://localhost:8000/api/stocks/fetch
```

This will fetch OHLCV and fundamental data for 100+ NSE stocks from Yahoo Finance.
**It runs in the background and takes about 5–10 minutes.**

---

## 🔌 API Documentation

### Stocks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/stocks/` | List all stocks with fundamentals |
| GET | `/api/stocks/{symbol}` | Get single stock |
| POST | `/api/stocks/fetch` | Trigger background data fetch |
| GET | `/api/stocks/count/total` | Total stocks in DB |

### Backtest

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/backtest/run` | Run a new backtest |
| GET | `/api/backtest/{id}` | Get saved backtest by ID |
| GET | `/api/backtest/{id}/export/csv` | Download portfolio logs as CSV |
| GET | `/api/backtest/history/all` | List all past backtests |

### Sample Backtest Request

```json
POST /api/backtest/run
{
  "start_date": "2020-01-01",
  "end_date": "2024-01-01",
  "capital": 1000000,
  "portfolio_size": 20,
  "rebalance_frequency": "quarterly",
  "min_market_cap": 1000,
  "max_market_cap": null,
  "min_roce": 15,
  "pat_positive": true
}
```

---

## 🗄️ Database Schema

### `stocks`
| Column | Type | Description |
|--------|------|-------------|
| id | int (PK) | Auto-incremented ID |
| symbol | varchar | NSE symbol e.g. RELIANCE |
| company_name | varchar | Full company name |
| sector | varchar | Sector from Yahoo Finance |

### `stock_prices`
| Column | Type | Description |
|--------|------|-------------|
| id | int (PK) | |
| stock_id | int (FK) | References stocks.id |
| date | date | Trading date |
| open, high, low, close | float | Price data |
| volume | float | Trading volume |

### `fundamentals`
| Column | Type | Description |
|--------|------|-------------|
| id | int (PK) | |
| stock_id | int (FK) | References stocks.id |
| market_cap | float | In ₹ Crores |
| pe_ratio | float | Price-to-Earnings |
| roe | float | Return on Equity (%) |
| roce | float | Return on Capital Employed (%) |
| pat | float | Profit After Tax (₹ Cr) |

### `backtests`
| Column | Type | Description |
|--------|------|-------------|
| id | int (PK) | |
| start_date, end_date | date | Backtest period |
| capital | float | Starting capital |
| rebalance_frequency | varchar | monthly / quarterly / yearly |
| portfolio_size | int | # of stocks |
| cagr, total_return | float | Results |
| sharpe_ratio | float | |
| max_drawdown | float | |

### `portfolio_logs`
| Column | Type | Description |
|--------|------|-------------|
| id | int (PK) | |
| backtest_id | int (FK) | References backtests.id |
| rebalance_date | date | When this rebalance happened |
| symbol | varchar | Stock symbol |
| weight | float | Allocation % |
| return_percent | float | Return during this period |

---

## 📐 Assumptions

1. **ROCE from Yahoo Finance** — Yahoo Finance doesn't expose ROCE directly. We use `returnOnAssets` as a proxy. For production use, Screener.in or Ticker API would give more accurate ROCE.

2. **Fundamental data is static** — All stocks are filtered and ranked using the most recent fundamental snapshot. We don't simulate how fundamentals looked in the past (point-in-time fundamentals). This is a simplification.

3. **No transaction costs** — Brokerage, STT, and slippage are not modeled.

4. **Equal weight only** — Market-cap and metric-weighted sizing are not implemented in this version.

5. **Holiday handling** — If a rebalance date falls on a weekend or holiday, we use the next available trading day's price.

6. **Data availability** — Some stocks may have incomplete data from Yahoo Finance. Those are skipped during the backtest.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 (Vite), Tailwind CSS, Recharts, Axios |
| Backend | FastAPI, Python 3.11 |
| Database | PostgreSQL 15, SQLAlchemy 2 |
| Data Source | Yahoo Finance via `yfinance` |
| Charts | Recharts |

---

## 📝 Optional Improvements (Bonus Ideas)

- Add Nifty 50 benchmark comparison on the equity chart
- Add more position sizing methods (market cap weighted, metric weighted)
- Add point-in-time fundamental data to avoid lookahead bias in filtering
- Add strategy comparison (run two backtests and overlay charts)
- Add more ranking metrics (ROCE rank, PAT growth rank)
- Deploy with Render / Railway / Vercel
