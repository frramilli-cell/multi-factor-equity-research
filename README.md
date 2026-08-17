# Multi-Factor Equity Research & Backtesting

Systematic equity research using historical S&P 500 constituents and SEC fundamental data to study whether a transparent, rules-based multi-factor framework can identify stocks with stronger risk-adjusted characteristics.

This repository is structured as an end-to-end research workflow: data preparation, factor construction, cross-sectional ranking, portfolio formation, backtesting, performance evaluation, and robustness analysis.

> **Project status:** Core research engine implemented. Empirical outputs will be added only after source data are loaded, cleaned, and validated.

## Research Objective

The central question is:

**Can a diversified combination of fundamental and market-based equity factors produce persistent risk-adjusted performance relative to a broad benchmark?**

Rather than relying on a single signal, the framework combines economically motivated factors and evaluates both their standalone and joint behavior through time.

## Factor Framework

| Factor | Economic intuition | Illustrative signals |
|---|---|---|
| Value | Relatively inexpensive securities may earn a valuation premium | Earnings yield, book-to-market, free-cash-flow yield |
| Momentum | Recent relative winners may continue to outperform over intermediate horizons | 6–12 month price momentum |
| Quality | Financially robust and profitable firms may compound more consistently | ROE/ROA, margins, leverage, earnings quality |
| Low Volatility | Lower-risk equities may deliver attractive risk-adjusted returns | Realized volatility, downside risk, beta |

The implementation supports multiple raw signals per factor. Signals are winsorized and standardized cross-sectionally at each formation date before being combined into factor scores and an equal-weight composite score.

## Implemented Research Pipeline

1. **Signal cleaning** — date-by-date winsorization of raw signals.
2. **Cross-sectional standardization** — z-score normalization within each formation date.
3. **Factor construction** — aggregation of one or more standardized signals into value, momentum, quality, low-volatility, or custom factor scores.
4. **Composite scoring** — equal-weight combination of available factor scores.
5. **Portfolio formation** — long-only selection of the highest-ranked securities with equal weighting.
6. **Turnover measurement** — one-way turnover including entries and exits.
7. **Backtesting** — formation-date weights applied only to subsequent forward returns.
8. **Transaction costs** — configurable basis-point cost applied to portfolio turnover.
9. **Performance analysis** — cumulative wealth, annualized return, volatility, Sharpe ratio, maximum drawdown, hit rate, and best/worst periods.
10. **Automated validation** — unit tests run through GitHub Actions.

## Repository Structure

```text
multi-factor-equity-research/
├── .github/workflows/tests.yml
├── README.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── factors.py
│   ├── portfolio.py
│   ├── backtest.py
│   ├── metrics.py
│   ├── pipeline.py
│   └── README.md
├── tests/
│   └── test_research.py
├── data/
│   └── README.md
├── results/
│   └── README.md
├── figures/
│   └── README.md
└── report/
    └── README.md
```

## Expected Input Format

The research engine intentionally separates signal construction from subsequent realized returns to reduce look-ahead risk.

`signals` should contain one row per security and formation date:

```text
date | ticker | earnings_yield | momentum_12_1 | roe | neg_volatility_12m | ...
```

`forward_returns` should contain the return realized after that formation date:

```text
date | ticker | forward_return
```

The date in both tables is therefore the **portfolio formation date**, not the end date of the subsequent holding-period return.

## Minimal Usage

```python
from src.config import BacktestConfig
from src.pipeline import run_research_pipeline

factor_columns = {
    "value": ["earnings_yield", "book_to_market"],
    "momentum": ["momentum_12_1"],
    "quality": ["roe", "gross_profitability"],
    "low_volatility": ["neg_volatility_12m"],
}

config = BacktestConfig(
    top_quantile=0.20,
    transaction_cost_bps=10.0,
    annualization_factor=12,
)

outputs = run_research_pipeline(
    signals=signals,
    forward_returns=forward_returns,
    factor_columns=factor_columns,
    config=config,
)

print(outputs["summary"])
```

## Methodological Principles

The analysis is built around safeguards that matter in empirical investment research:

- no use of future information in portfolio formation;
- explicit treatment of missing observations and extreme values;
- consistent rebalancing and holding-period assumptions;
- separation of signal measurement from subsequent return evaluation;
- explicit turnover and transaction-cost treatment;
- benchmark-relative as well as absolute performance measurement;
- transparent reporting of assumptions and limitations.

## Running the Project

Create a Python environment and install dependencies:

```bash
pip install -r requirements.txt
```

Run the automated checks:

```bash
pytest -q
```

GitHub Actions also runs the test suite automatically on pushes and pull requests.

## Performance Evaluation

Once empirical data are validated, the final analysis will report, at minimum:

- annualized return;
- annualized volatility;
- Sharpe ratio;
- maximum drawdown;
- cumulative wealth;
- benchmark-relative return;
- turnover and transaction-cost sensitivity;
- factor-level and composite portfolio results.

Charts and summary tables will be stored in `figures/` and `results/` rather than embedded as unsupported headline claims.

## Data Integrity & Reproducibility

Raw third-party datasets should not be committed when redistribution is restricted. The `data/` directory instead documents provenance, coverage, field definitions, and cleaning rules. Local binary datasets are excluded through `.gitignore`.

The core research logic is modular rather than concentrated in one opaque notebook, making assumptions easier to inspect, test, and change.

## Limitations

Historical backtests are sensitive to data quality, universe definition, survivorship bias, factor specification, rebalancing assumptions, point-in-time availability of accounting information, transaction costs, and treatment of delisted securities. Backtested performance does not represent live investment performance and should not be interpreted as a guarantee of future returns.

## Author

**Fiona Rramilli**  
MSc Finance — University of Neuchâtel

*Independent academic/portfolio research project. For educational and research purposes only; not investment advice.*
