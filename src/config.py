from dataclasses import dataclass


@dataclass(frozen=True)
class BacktestConfig:
    """Core assumptions for portfolio formation and evaluation."""

    rebalance_frequency: str = "M"
    top_quantile: float = 0.20
    transaction_cost_bps: float = 10.0
    annualization_factor: int = 12
    min_observations: int = 24
    winsor_lower: float = 0.01
    winsor_upper: float = 0.99

    def validate(self) -> None:
        if not 0 < self.top_quantile <= 1:
            raise ValueError("top_quantile must be in (0, 1].")
        if self.transaction_cost_bps < 0:
            raise ValueError("transaction_cost_bps cannot be negative.")
        if not 0 <= self.winsor_lower < self.winsor_upper <= 1:
            raise ValueError("winsorization bounds must satisfy 0 <= lower < upper <= 1.")
