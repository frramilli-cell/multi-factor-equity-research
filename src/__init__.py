"""Multi-factor equity research package."""

from .backtest import run_backtest
from .factors import build_factor_scores
from .metrics import performance_summary
from .portfolio import form_portfolio_weights

__all__ = [
    "build_factor_scores",
    "form_portfolio_weights",
    "run_backtest",
    "performance_summary",
]
