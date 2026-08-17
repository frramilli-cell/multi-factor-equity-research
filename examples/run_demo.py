"""Deterministic demonstration of the research engine using simulated data.

The demo exists to prove the pipeline runs end to end without implying that the
simulated performance is an empirical investment result.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.config import BacktestConfig
from src.pipeline import run_research_pipeline


def make_demo_data(seed: int = 7) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2020-01-31", periods=48, freq="ME")
    tickers = [f"STK{i:02d}" for i in range(30)]

    rows = []
    return_rows = []
    for date in dates:
        latent_quality = rng.normal(0, 1, len(tickers))
        latent_value = rng.normal(0, 1, len(tickers))
        latent_momentum = rng.normal(0, 1, len(tickers))
        latent_low_vol = rng.normal(0, 1, len(tickers))

        for i, ticker in enumerate(tickers):
            rows.append(
                {
                    "date": date,
                    "ticker": ticker,
                    "earnings_yield": latent_value[i] + rng.normal(0, 0.4),
                    "book_to_market": latent_value[i] + rng.normal(0, 0.4),
                    "momentum_12_1": latent_momentum[i] + rng.normal(0, 0.4),
                    "roe": latent_quality[i] + rng.normal(0, 0.4),
                    "gross_profitability": latent_quality[i] + rng.normal(0, 0.4),
                    "neg_volatility_12m": latent_low_vol[i] + rng.normal(0, 0.4),
                }
            )
            signal = (
                latent_quality[i]
                + latent_value[i]
                + latent_momentum[i]
                + latent_low_vol[i]
            ) / 4
            return_rows.append(
                {
                    "date": date,
                    "ticker": ticker,
                    "forward_return": 0.005 + 0.01 * signal + rng.normal(0, 0.05),
                }
            )

    return pd.DataFrame(rows), pd.DataFrame(return_rows)


def main() -> None:
    signals, forward_returns = make_demo_data()
    outputs = run_research_pipeline(
        signals=signals,
        forward_returns=forward_returns,
        factor_columns={
            "value": ["earnings_yield", "book_to_market"],
            "momentum": ["momentum_12_1"],
            "quality": ["roe", "gross_profitability"],
            "low_volatility": ["neg_volatility_12m"],
        },
        config=BacktestConfig(top_quantile=0.20, transaction_cost_bps=10),
    )

    print("DEMO ONLY — simulated data, not an empirical result")
    print(outputs["summary"].round(4).to_string())


if __name__ == "__main__":
    main()
