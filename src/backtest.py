from __future__ import annotations

import pandas as pd

from .portfolio import calculate_turnover


def run_backtest(
    weights: pd.DataFrame,
    forward_returns: pd.DataFrame,
    transaction_cost_bps: float = 10.0,
) -> pd.DataFrame:
    """Apply formation-date weights to subsequent security returns.

    Parameters
    ----------
    weights:
        Long-form table with ``date``, ``ticker``, and ``weight``. ``date`` is
        the portfolio formation date.
    forward_returns:
        Long-form table with ``date``, ``ticker``, and ``forward_return`` where
        the return is realized after the corresponding formation date.
    transaction_cost_bps:
        Cost applied to one-way turnover at each rebalance.

    Returns
    -------
    pandas.DataFrame
        Date-level gross return, turnover, transaction cost, and net return.
    """
    required_w = {"date", "ticker", "weight"}
    required_r = {"date", "ticker", "forward_return"}
    if missing := required_w.difference(weights.columns):
        raise ValueError(f"Weights missing columns: {sorted(missing)}")
    if missing := required_r.difference(forward_returns.columns):
        raise ValueError(f"Returns missing columns: {sorted(missing)}")
    if transaction_cost_bps < 0:
        raise ValueError("transaction_cost_bps cannot be negative.")

    merged = weights.merge(
        forward_returns[["date", "ticker", "forward_return"]],
        on=["date", "ticker"],
        how="left",
        validate="many_to_one",
    )
    if merged["forward_return"].isna().any():
        missing_n = int(merged["forward_return"].isna().sum())
        raise ValueError(f"Missing forward returns for {missing_n} selected holdings.")

    merged["contribution"] = merged["weight"] * merged["forward_return"]
    gross = merged.groupby("date")["contribution"].sum().rename("gross_return")
    turnover = calculate_turnover(weights)

    result = pd.concat([gross, turnover], axis=1).fillna({"turnover": 0.0})
    result["transaction_cost"] = result["turnover"] * transaction_cost_bps / 10_000.0
    result["net_return"] = result["gross_return"] - result["transaction_cost"]
    return result.reset_index()
