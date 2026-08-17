import numpy as np
import pandas as pd

from src.backtest import run_backtest
from src.factors import build_factor_scores
from src.metrics import performance_summary
from src.portfolio import form_portfolio_weights


def _toy_signals() -> pd.DataFrame:
    dates = pd.to_datetime(["2024-01-31"] * 5 + ["2024-02-29"] * 5)
    tickers = list("ABCDE") * 2
    return pd.DataFrame(
        {
            "date": dates,
            "ticker": tickers,
            "earnings_yield": [1, 2, 3, 4, 5, 2, 3, 4, 5, 6],
            "momentum_12_1": [5, 4, 3, 2, 1, 1, 2, 3, 4, 5],
            "roe": [1, 2, 4, 3, 5, 2, 4, 3, 5, 6],
            "neg_volatility_12m": [1, 3, 2, 5, 4, 2, 3, 4, 5, 6],
        }
    )


def test_factor_scores_are_created():
    signals = _toy_signals()
    scored = build_factor_scores(
        signals,
        {
            "value": ["earnings_yield"],
            "momentum": ["momentum_12_1"],
            "quality": ["roe"],
            "low_volatility": ["neg_volatility_12m"],
        },
        winsor_lower=0.0,
        winsor_upper=1.0,
    )

    assert "composite_score" in scored.columns
    assert scored.groupby("date")["value_score"].mean().abs().max() < 1e-12


def test_portfolio_weights_sum_to_one():
    scored = build_factor_scores(
        _toy_signals(),
        {"value": ["earnings_yield"], "quality": ["roe"]},
        winsor_lower=0.0,
        winsor_upper=1.0,
    )
    weights = form_portfolio_weights(scored, top_quantile=0.4)
    sums = weights.groupby("date")["weight"].sum()
    assert np.allclose(sums.values, 1.0)


def test_backtest_applies_transaction_costs():
    dates = pd.to_datetime(["2024-01-31", "2024-02-29"])
    weights = pd.DataFrame(
        {
            "date": [dates[0], dates[0], dates[1], dates[1]],
            "ticker": ["A", "B", "A", "C"],
            "weight": [0.5, 0.5, 0.5, 0.5],
        }
    )
    returns = pd.DataFrame(
        {
            "date": [dates[0], dates[0], dates[1], dates[1]],
            "ticker": ["A", "B", "A", "C"],
            "forward_return": [0.10, 0.00, 0.02, 0.04],
        }
    )

    result = run_backtest(weights, returns, transaction_cost_bps=10.0)
    assert np.all(result["net_return"] <= result["gross_return"])
    assert np.all(result["transaction_cost"] >= 0)


def test_performance_summary_fields():
    summary = performance_summary(pd.Series([0.02, -0.01, 0.03, 0.01]))
    expected = {
        "observations",
        "total_return",
        "annualized_return",
        "annualized_volatility",
        "sharpe_ratio",
        "max_drawdown",
    }
    assert expected.issubset(summary.index)
