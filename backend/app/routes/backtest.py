from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Backtest, PortfolioLog
from app.schemas import BacktestRequest, BacktestResult
from app.services.backtest_service import run_backtest
import io
import csv

router = APIRouter()


@router.post("/run", response_model=BacktestResult)
def run_backtest_endpoint(request: BacktestRequest, db: Session = Depends(get_db)):
    """
    Main endpoint to run a backtest.
    Accepts backtest configuration from the frontend form.
    Returns equity curve, metrics, and portfolio logs.
    """
    try:
        result = run_backtest(db, request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backtest failed: {str(e)}")


@router.get("/{backtest_id}", response_model=BacktestResult)
def get_backtest_result(backtest_id: int, db: Session = Depends(get_db)):
    """
    Fetch a previously run backtest by its ID.
    Useful for retrieving saved results without re-running.
    """
    backtest = db.query(Backtest).filter(Backtest.id == backtest_id).first()
    if not backtest:
        raise HTTPException(status_code=404, detail="Backtest not found")

    logs = (
        db.query(PortfolioLog)
        .filter(PortfolioLog.backtest_id == backtest_id)
        .all()
    )

    # We don't store equity_curve in the DB (would be too large),
    # so we return an empty list here. The frontend should store the result
    # from the initial /run call.
    return {
        "backtest_id": backtest.id,
        "start_date": backtest.start_date,
        "end_date": backtest.end_date,
        "initial_capital": backtest.capital,
        "final_value": backtest.final_value,
        "cagr": backtest.cagr,
        "total_return": backtest.total_return,
        "sharpe_ratio": backtest.sharpe_ratio,
        "max_drawdown": backtest.max_drawdown,
        "equity_curve": [],
        "drawdown_series": [],
        "top_winners": [],
        "top_losers": [],
        "portfolio_logs": [
            {
                "symbol": log.symbol,
                "rebalance_date": log.rebalance_date,
                "weight": log.weight,
                "return_percent": log.return_percent,
            }
            for log in logs
        ],
    }


@router.get("/{backtest_id}/export/csv")
def export_backtest_csv(backtest_id: int, db: Session = Depends(get_db)):
    """
    Export portfolio logs for a backtest as a CSV file.
    The frontend download button calls this endpoint.
    """
    backtest = db.query(Backtest).filter(Backtest.id == backtest_id).first()
    if not backtest:
        raise HTTPException(status_code=404, detail="Backtest not found")

    logs = (
        db.query(PortfolioLog)
        .filter(PortfolioLog.backtest_id == backtest_id)
        .order_by(PortfolioLog.rebalance_date)
        .all()
    )

    # Build CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header row
    writer.writerow(["Backtest ID", "Symbol", "Rebalance Date", "Weight (%)", "Return (%)"])

    # Write data rows
    for log in logs:
        writer.writerow([
            backtest_id,
            log.symbol,
            log.rebalance_date,
            log.weight,
            log.return_percent,
        ])

    output.seek(0)

    # Return as downloadable file
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=backtest_{backtest_id}_logs.csv"}
    )


@router.get("/history/all")
def get_all_backtests(db: Session = Depends(get_db)):
    """
    Returns a list of all backtests that have been run.
    Useful for a history page or to re-load previous runs.
    """
    backtests = (
        db.query(Backtest)
        .order_by(Backtest.created_at.desc())
        .limit(50)
        .all()
    )

    return [
        {
            "id": bt.id,
            "start_date": bt.start_date,
            "end_date": bt.end_date,
            "capital": bt.capital,
            "rebalance_frequency": bt.rebalance_frequency,
            "portfolio_size": bt.portfolio_size,
            "cagr": bt.cagr,
            "total_return": bt.total_return,
            "max_drawdown": bt.max_drawdown,
            "created_at": bt.created_at,
        }
        for bt in backtests
    ]
