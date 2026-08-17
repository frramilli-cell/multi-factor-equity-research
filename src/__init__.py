"""Multi-factor equity research package."""

from .backtest import run_backtest
from .data import build_forward_returns, load_constituents, load_prices
from .factors import build_factor_scores
from .metrics import performance_summary
from .portfolio import form_portfolio_weights
from .signals import add_price_signals, build_fundamental_signals

__all__ = [
    "load_prices",
    "load_constituents",
    "build_forward_returns",
    "add_price_signals",
    "build_fundamental_signals",
    "build_factor_scores",
    "form_portfolio_weights",
    "run_backtest",
    "performance_summary",
]
