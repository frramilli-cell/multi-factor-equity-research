from __future__ import annotations

import numpy as np
import pandas as pd


def max_drawdown(returns: pd.Series) -> float:
    wealth = (1.0 + returns.fillna(0.0)).cumprod()
    running_peak = wealth.cummax()
    drawdown = wealth / running_peak - 1.0
    return float(drawdown.min()) if not drawdown.empty else np.nan


def performance_summary(
    returns: pd.Series,
    annualization_factor: int = 12,
    risk_free_rate: float = 0.0,
) -> pd.Series:
    """Return a compact set of standard portfolio performance statistics."""
    clean = returns.dropna().astype(float)
    if clean.empty:
        return pd.Series(dtype=float)

    periods = len(clean)
    total_return = (1.0 + clean).prod() - 1.0
    annualized_return = (1.0 + total_return) ** (annualization_factor / periods) - 1.0
    annualized_volatility = clean.std(ddof=1) * np.sqrt(annualization_factor)

    periodic_rf = risk_free_rate / annualization_factor
    excess = clean - periodic_rf
    sharpe = np.nan
    if excess.std(ddof=1) > 0:
        sharpe = excess.mean() / excess.std(ddof=1) * np.sqrt(annualization_factor)

    return pd.Series(
        {
            "observations": periods,
            "total_return": total_return,
            "annualized_return": annualized_return,
            "annualized_volatility": annualized_volatility,
            "sharpe_ratio": sharpe,
            "max_drawdown": max_drawdown(clean),
            "hit_rate": float((clean > 0).mean()),
            "best_period": float(clean.max()),
            "worst_period": float(clean.min()),
        }
    )


def add_wealth_index(backtest: pd.DataFrame, return_column: str = "net_return") -> pd.DataFrame:
    """Append a cumulative wealth index starting from 1.0."""
    if return_column not in backtest.columns:
        raise ValueError(f"Column {return_column!r} not found.")
    out = backtest.sort_values("date").copy()
    out["wealth_index"] = (1.0 + out[return_column].fillna(0.0)).cumprod()
    return out
