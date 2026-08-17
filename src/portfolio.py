from __future__ import annotations

import numpy as np
import pandas as pd


def form_portfolio_weights(
    scores: pd.DataFrame,
    score_column: str = "composite_score",
    top_quantile: float = 0.20,
) -> pd.DataFrame:
    """Form equal-weight long-only portfolios from the highest-ranked stocks.

    The function operates independently at each rebalance date. Securities with
    missing scores are excluded. The selected names receive equal weights that
    sum to one on each date.
    """
    required = {"date", "ticker", score_column}
    missing = required.difference(scores.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    if not 0 < top_quantile <= 1:
        raise ValueError("top_quantile must be in (0, 1].")

    rows: list[pd.DataFrame] = []
    for date, group in scores.groupby("date", sort=True):
        eligible = group.dropna(subset=[score_column]).copy()
        if eligible.empty:
            continue

        n_select = max(1, int(np.ceil(len(eligible) * top_quantile)))
        selected = eligible.nlargest(n_select, score_column).copy()
        selected["weight"] = 1.0 / n_select
        selected["rank"] = selected[score_column].rank(method="first", ascending=False)
        rows.append(selected[["date", "ticker", score_column, "rank", "weight"]])

    if not rows:
        return pd.DataFrame(columns=["date", "ticker", score_column, "rank", "weight"])

    return pd.concat(rows, ignore_index=True)


def calculate_turnover(weights: pd.DataFrame) -> pd.Series:
    """Calculate one-way portfolio turnover at each rebalance date.

    Turnover is defined as one half of the absolute change in portfolio weights,
    including entries and exits.
    """
    if weights.empty:
        return pd.Series(dtype=float, name="turnover")

    matrix = (
        weights.pivot_table(index="date", columns="ticker", values="weight", fill_value=0.0)
        .sort_index()
    )
    turnover = 0.5 * matrix.diff().abs().sum(axis=1)
    turnover.iloc[0] = 0.5 * matrix.iloc[0].abs().sum()
    turnover.name = "turnover"
    return turnover
