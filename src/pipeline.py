from __future__ import annotations

import pandas as pd

from .backtest import run_backtest
from .config import BacktestConfig
from .factors import build_factor_scores
from .metrics import add_wealth_index, performance_summary
from .portfolio import form_portfolio_weights


def run_research_pipeline(
    signals: pd.DataFrame,
    forward_returns: pd.DataFrame,
    factor_columns: dict[str, list[str]],
    config: BacktestConfig | None = None,
) -> dict[str, pd.DataFrame | pd.Series]:
    """Run factor scoring, portfolio formation, backtesting, and evaluation."""
    cfg = config or BacktestConfig()
    cfg.validate()

    scores = build_factor_scores(
        signals=signals,
        factor_columns=factor_columns,
        winsor_lower=cfg.winsor_lower,
        winsor_upper=cfg.winsor_upper,
    )

    weights = form_portfolio_weights(
        scores=scores,
        score_column="composite_score",
        top_quantile=cfg.top_quantile,
    )

    backtest = run_backtest(
        weights=weights,
        forward_returns=forward_returns,
        transaction_cost_bps=cfg.transaction_cost_bps,
    )
    backtest = add_wealth_index(backtest, "net_return")

    summary = performance_summary(
        backtest["net_return"],
        annualization_factor=cfg.annualization_factor,
    )

    return {
        "scores": scores,
        "weights": weights,
        "backtest": backtest,
        "summary": summary,
    }
