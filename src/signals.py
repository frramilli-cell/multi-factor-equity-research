from __future__ import annotations

import numpy as np
import pandas as pd


def add_price_signals(prices: pd.DataFrame) -> pd.DataFrame:
    """Create monthly momentum and low-volatility signals from adjusted prices."""
    required = {"date", "ticker", "adj_close"}
    if missing := required.difference(prices.columns):
        raise ValueError(f"Price data missing columns: {sorted(missing)}")

    out = prices.sort_values(["ticker", "date"]).copy()
    out["return_1m"] = out.groupby("ticker")["adj_close"].pct_change()
    # Standard 12-1 momentum: price at t-1 relative to price at t-12.
    lag1 = out.groupby("ticker")["adj_close"].shift(1)
    lag12 = out.groupby("ticker")["adj_close"].shift(12)
    out["momentum_12_1"] = lag1 / lag12 - 1.0
    # Higher score should be preferable, so volatility is negated.
    vol = (
        out.groupby("ticker")["return_1m"]
        .rolling(window=12, min_periods=6)
        .std()
        .reset_index(level=0, drop=True)
    )
    out["neg_volatility_12m"] = -vol
    return out


def build_fundamental_signals(fundamentals: pd.DataFrame) -> pd.DataFrame:
    """Derive simple value and quality ratios from point-in-time fundamentals.

    Expected columns are intentionally generic so SEC-derived facts or another
    licensed fundamentals dataset can feed the same research engine.
    """
    required = {"date", "ticker", "market_cap"}
    if missing := required.difference(fundamentals.columns):
        raise ValueError(f"Fundamental data missing columns: {sorted(missing)}")

    out = fundamentals.copy()
    market_cap = pd.to_numeric(out["market_cap"], errors="coerce").replace(0, np.nan)

    if "net_income" in out.columns:
        out["earnings_yield"] = pd.to_numeric(out["net_income"], errors="coerce") / market_cap
    if "book_equity" in out.columns:
        out["book_to_market"] = pd.to_numeric(out["book_equity"], errors="coerce") / market_cap
    if "free_cash_flow" in out.columns:
        out["free_cash_flow_yield"] = pd.to_numeric(out["free_cash_flow"], errors="coerce") / market_cap
    if {"net_income", "book_equity"}.issubset(out.columns):
        equity = pd.to_numeric(out["book_equity"], errors="coerce").replace(0, np.nan)
        out["roe"] = pd.to_numeric(out["net_income"], errors="coerce") / equity
    if {"gross_profit", "total_assets"}.issubset(out.columns):
        assets = pd.to_numeric(out["total_assets"], errors="coerce").replace(0, np.nan)
        out["gross_profitability"] = pd.to_numeric(out["gross_profit"], errors="coerce") / assets
    if {"total_debt", "total_assets"}.issubset(out.columns):
        assets = pd.to_numeric(out["total_assets"], errors="coerce").replace(0, np.nan)
        # Negative leverage means a larger factor input is economically preferable.
        out["neg_leverage"] = -pd.to_numeric(out["total_debt"], errors="coerce") / assets

    return out


def assemble_signal_panel(
    price_signals: pd.DataFrame,
    fundamental_signals: pd.DataFrame,
) -> pd.DataFrame:
    """Combine price and fundamental signals by formation date and ticker."""
    required = {"date", "ticker"}
    for name, frame in (("price", price_signals), ("fundamental", fundamental_signals)):
        if missing := required.difference(frame.columns):
            raise ValueError(f"{name.title()} signals missing columns: {sorted(missing)}")

    return price_signals.merge(
        fundamental_signals,
        on=["date", "ticker"],
        how="inner",
        suffixes=("", "_fund"),
        validate="one_to_one",
    )
