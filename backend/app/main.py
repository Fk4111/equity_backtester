from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routes import stocks, backtest

# Create all database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Equity Backtester API",
    description="A simple backtesting platform for Indian equity strategies",
    version="1.0.0"
)

# Allow React frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:5173",
    "http://localhost:3000",
    "https://equity-backtester.vercel.app"
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route modules
app.include_router(stocks.router, prefix="/api/stocks", tags=["Stocks"])
app.include_router(backtest.router, prefix="/api/backtest", tags=["Backtest"])


@app.get("/")
def root():
    return {"message": "Equity Backtester API is running!"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
