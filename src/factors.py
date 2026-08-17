from __future__ import annotations

from typing import Mapping

import numpy as np
import pandas as pd


DEFAULT_DIRECTIONS: Mapping[str, int] = {
    "value": 1,
    "momentum": 1,
    "quality": 1,
    "low_volatility": 1,
}


def winsorize_cross_section(
    frame: pd.DataFrame,
    columns: list[str],
    lower: float = 0.01,
    upper: float = 0.99,
) -> pd.DataFrame:
    """Winsorize selected columns independently within each date."""
    out = frame.copy()

    def _clip(group: pd.DataFrame) -> pd.DataFrame:
        g = group.copy()
        for col in columns:
            lo = g[col].quantile(lower)
            hi = g[col].quantile(upper)
            g[col] = g[col].clip(lo, hi)
        return g

    return (
        out.groupby("date", group_keys=False, sort=False)
        .apply(_clip, include_groups=False)
        .reset_index(drop=True)
    )


def zscore_cross_section(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Convert selected signals into date-by-date cross-sectional z-scores."""
    out = frame.copy()
    for col in columns:
        mean = out.groupby("date")[col].transform("mean")
        std = out.groupby("date")[col].transform("std").replace(0, np.nan)
        out[f"{col}_z"] = (out[col] - mean) / std
    return out


def build_factor_scores(
    signals: pd.DataFrame,
    factor_columns: Mapping[str, list[str]],
    directions: Mapping[str, int] | None = None,
    winsor_lower: float = 0.01,
    winsor_upper: float = 0.99,
) -> pd.DataFrame:
    """Build date-level factor and equal-weight composite scores.

    Parameters
    ----------
    signals:
        Long-form table containing at least ``date`` and ``ticker`` plus the
        raw signal columns referenced by ``factor_columns``.
    factor_columns:
        Mapping from factor name to one or more raw signal columns. Example::

            {
                "value": ["earnings_yield", "book_to_market"],
                "momentum": ["momentum_12_1"],
                "quality": ["roe", "gross_profitability"],
                "low_volatility": ["neg_volatility_12m"],
            }

        Raw columns should be oriented so that a larger value is economically
        preferable. Use ``directions`` to reverse a factor when necessary.
    directions:
        Optional mapping with values +1 or -1 applied to factor scores.

    Returns
    -------
    pandas.DataFrame
        Original identifiers plus factor scores and ``composite_score``.
    """
    required = {"date", "ticker"}
    missing = required.difference(signals.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    all_signal_columns = [c for cols in factor_columns.values() for c in cols]
    absent = [c for c in all_signal_columns if c not in signals.columns]
    if absent:
        raise ValueError(f"Missing factor signal columns: {absent}")

    clean = winsorize_cross_section(
        signals,
        all_signal_columns,
        lower=winsor_lower,
        upper=winsor_upper,
    )
    scored = zscore_cross_section(clean, all_signal_columns)

    direction_map = dict(DEFAULT_DIRECTIONS)
    if directions:
        direction_map.update(directions)

    factor_score_names: list[str] = []
    for factor, cols in factor_columns.items():
        direction = direction_map.get(factor, 1)
        if direction not in (-1, 1):
            raise ValueError(f"Direction for {factor!r} must be +1 or -1.")
        zcols = [f"{c}_z" for c in cols]
        score_name = f"{factor}_score"
        scored[score_name] = scored[zcols].mean(axis=1, skipna=True) * direction
        factor_score_names.append(score_name)

    scored["composite_score"] = scored[factor_score_names].mean(axis=1, skipna=True)
    return scored
