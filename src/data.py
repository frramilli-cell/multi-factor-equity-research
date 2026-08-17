from __future__ import annotations

from pathlib import Path

import pandas as pd


PRICE_COLUMNS = {"date", "ticker", "adj_close"}
CONSTITUENT_COLUMNS = {"date", "ticker"}


def _read_table(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix in {".parquet", ".pq"}:
        return pd.read_parquet(path)
    raise ValueError(f"Unsupported file type: {suffix}. Use CSV or Parquet.")


def load_prices(path: str | Path) -> pd.DataFrame:
    """Load and validate long-form adjusted-close price data."""
    frame = _read_table(path)
    missing = PRICE_COLUMNS.difference(frame.columns)
    if missing:
        raise ValueError(f"Price data missing columns: {sorted(missing)}")

    out = frame.copy()
    out["date"] = pd.to_datetime(out["date"], errors="raise")
    out["ticker"] = out["ticker"].astype(str).str.upper().str.strip()
    out["adj_close"] = pd.to_numeric(out["adj_close"], errors="coerce")
    out = out.dropna(subset=["date", "ticker", "adj_close"])
    out = out.sort_values(["ticker", "date"]).drop_duplicates(["ticker", "date"], keep="last")
    if (out["adj_close"] <= 0).any():
        raise ValueError("Adjusted-close prices must be strictly positive.")
    return out.reset_index(drop=True)


def load_constituents(path: str | Path) -> pd.DataFrame:
    """Load historical point-in-time index membership snapshots."""
    frame = _read_table(path)
    missing = CONSTITUENT_COLUMNS.difference(frame.columns)
    if missing:
        raise ValueError(f"Constituent data missing columns: {sorted(missing)}")

    out = frame.copy()
    out["date"] = pd.to_datetime(out["date"], errors="raise")
    out["ticker"] = out["ticker"].astype(str).str.upper().str.strip()
    out = out.dropna(subset=["date", "ticker"])
    return out.sort_values(["date", "ticker"]).drop_duplicates().reset_index(drop=True)


def monthly_prices(prices: pd.DataFrame) -> pd.DataFrame:
    """Convert daily/irregular prices to month-end observations per security."""
    missing = PRICE_COLUMNS.difference(prices.columns)
    if missing:
        raise ValueError(f"Price data missing columns: {sorted(missing)}")

    out = prices.copy().sort_values(["ticker", "date"])
    out["month"] = out["date"].dt.to_period("M")
    month_end = out.groupby(["ticker", "month"], as_index=False).tail(1).copy()
    return month_end.drop(columns="month").sort_values(["date", "ticker"]).reset_index(drop=True)


def build_forward_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Build one-period forward returns indexed by portfolio formation date."""
    monthly = monthly_prices(prices).sort_values(["ticker", "date"]).copy()
    monthly["forward_return"] = monthly.groupby("ticker")["adj_close"].shift(-1) / monthly["adj_close"] - 1.0
    return monthly[["date", "ticker", "forward_return"]].dropna().reset_index(drop=True)


def filter_point_in_time_universe(frame: pd.DataFrame, constituents: pd.DataFrame) -> pd.DataFrame:
    """Restrict observations to securities belonging to the universe on each date."""
    required = {"date", "ticker"}
    if missing := required.difference(frame.columns):
        raise ValueError(f"Input data missing columns: {sorted(missing)}")
    if missing := required.difference(constituents.columns):
        raise ValueError(f"Constituent data missing columns: {sorted(missing)}")
    return frame.merge(
        constituents[["date", "ticker"]].drop_duplicates(),
        on=["date", "ticker"],
        how="inner",
        validate="many_to_one",
    )
