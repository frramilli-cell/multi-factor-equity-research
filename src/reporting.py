from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from .metrics import performance_summary


def save_backtest_outputs(
    backtest: pd.DataFrame,
    output_dir: str | Path = "results",
    return_column: str = "net_return",
) -> dict[str, Path]:
    """Persist validated backtest outputs and a compact performance summary."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    backtest_path = output / "backtest_returns.csv"
    summary_path = output / "performance_summary.csv"

    backtest.to_csv(backtest_path, index=False)
    performance_summary(backtest[return_column]).rename("value").to_csv(summary_path, header=True)
    return {"backtest": backtest_path, "summary": summary_path}


def plot_wealth_index(
    backtest: pd.DataFrame,
    output_path: str | Path = "figures/wealth_index.png",
    wealth_column: str = "wealth_index",
) -> Path:
    """Create a publication-ready cumulative wealth chart."""
    if not {"date", wealth_column}.issubset(backtest.columns):
        raise ValueError(f"Backtest must contain 'date' and {wealth_column!r}.")

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(pd.to_datetime(backtest["date"]), backtest[wealth_column])
    ax.set_title("Cumulative Wealth Index")
    ax.set_xlabel("Date")
    ax.set_ylabel("Growth of $1")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return path
