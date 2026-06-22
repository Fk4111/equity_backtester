import numpy as np
import pandas as pd


def calculate_total_return(initial_value: float, final_value: float) -> float:
    """
    Total return = (final - initial) / initial * 100
    Returns percentage, e.g. 45.3 means 45.3% return.
    """
    if initial_value <= 0:
        return 0.0
    return round(((final_value - initial_value) / initial_value) * 100, 2)


def calculate_cagr(initial_value: float, final_value: float, years: float) -> float:
    """
    CAGR = (final/initial)^(1/years) - 1
    Returns percentage. Example: 12.5 means 12.5% annual growth.
    """
    if initial_value <= 0 or years <= 0:
        return 0.0

    cagr = ((final_value / initial_value) ** (1 / years) - 1) * 100
    return round(cagr, 2)


def calculate_max_drawdown(equity_values: list) -> float:
    """
    Max Drawdown = worst peak-to-trough decline in the equity curve.
    Returns percentage. Example: -35.2 means portfolio fell 35.2% from its peak.
    """
    if not equity_values or len(equity_values) < 2:
        return 0.0

    portfolio_values = np.array(equity_values)

    # Running maximum (peak at each point)
    running_max = np.maximum.accumulate(portfolio_values)

    # Drawdown at each point = (current - peak) / peak
    drawdowns = (portfolio_values - running_max) / running_max * 100

    max_dd = float(np.min(drawdowns))  # Most negative value = worst drawdown
    return round(max_dd, 2)


def calculate_sharpe_ratio(returns: list, risk_free_rate: float = 6.0) -> float:
    """
    Sharpe Ratio = (average return - risk free rate) / standard deviation of returns
    
    risk_free_rate is annual %, default 6% (approximate India 10yr bond yield)
    returns should be a list of period returns (%).
    
    A ratio > 1 is generally considered good.
    """
    if not returns or len(returns) < 2:
        return 0.0

    returns_array = np.array(returns)
    mean_return = np.mean(returns_array)
    std_return = np.std(returns_array)

    if std_return == 0:
        return 0.0

    # Adjust risk free rate to match period frequency
    # Assuming monthly returns, annualize by multiplying by 12
    period_risk_free = risk_free_rate / 12

    sharpe = (mean_return - period_risk_free) / std_return

    # Annualize the Sharpe ratio (multiply by sqrt of periods per year)
    annualized_sharpe = sharpe * np.sqrt(12)

    return round(float(annualized_sharpe), 2)


def calculate_drawdown_series(equity_curve: list) -> list:
    """
    Returns drawdown at each point in time for the equity curve.
    Used to draw the drawdown chart on the frontend.
    
    equity_curve: list of {"date": ..., "value": ...}
    Returns: list of {"date": ..., "drawdown": ...}
    """
    if not equity_curve:
        return []

    values = [point["value"] for point in equity_curve]
    dates = [point["date"] for point in equity_curve]

    values_array = np.array(values)
    running_max = np.maximum.accumulate(values_array)

    # Avoid division by zero
    drawdowns = np.where(
        running_max > 0,
        (values_array - running_max) / running_max * 100,
        0
    )

    return [
        {"date": dates[i], "drawdown": round(float(drawdowns[i]), 2)}
        for i in range(len(dates))
    ]
