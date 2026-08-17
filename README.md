# Multi-Factor Equity Research & Backtesting

A point-in-time equity research project testing whether a sector-relative combination of **Value, Quality, Financial Strength, and Momentum** can outperform the S&P 500.

The project began with a strong-looking backtest, but an audit identified a material survivorship-bias problem: using today's S&P 500 constituents in earlier periods leaks future information into the investment universe. I rebuilt the universe historically and reran the model without changing the factor logic.

> **Main finding:** after correcting the investment universe, the strategy did **not** outperform SPY over the full April 2020–April 2026 sample. The correction materially changed the conclusion and became the central result of the project.

That result is intentionally preserved. The goal of this repository is not to advertise a flattering backtest; it is to demonstrate disciplined empirical research, point-in-time data handling, reproducible Python implementation, and transparent interpretation.

## Research Design

| Item | Specification |
|---|---|
| Sample | April 2020 – April 2026 |
| Benchmark | SPY |
| Original portfolio | Top 20 stocks, equal weighted |
| Original rebalance frequency | Annual |
| Factors | Value, Quality, Financial Strength, Momentum |
| Fundamental data | SEC EDGAR / XBRL Company Facts |
| Market data | Historical adjusted prices |
| Corrected universe | Historical S&P 500 membership |

The original research notebook documents the empirical experiment and the survivorship-bias audit. The modular `src/` package extracts the reusable research logic into tested components.

## Why the Universe Correction Matters

A current S&P 500 constituent list cannot be safely projected backward through history. Companies removed from the index disappear from today's list, while later successful additions can be incorrectly treated as if they had always been investable. That creates survivorship bias and makes a historical strategy look better informed than a real investor could have been.

The corrected workflow therefore:

- uses historical point-in-time index membership;
- separates portfolio-formation information from subsequent returns;
- maps accounting data according to public filing availability, not merely fiscal-period end dates;
- applies explicit turnover and transaction-cost logic in the modular engine;
- keeps assumptions visible and testable.

## Factor Framework

| Factor | Economic intuition | Example signals |
|---|---|---|
| Value | Prefer securities priced more attractively relative to fundamentals | Earnings yield, book-to-market, free-cash-flow yield |
| Momentum | Intermediate-horizon winners may exhibit return persistence | 12–1 price momentum |
| Quality | Profitable, efficient firms may compound more consistently | ROE, gross profitability, operating margins |
| Financial Strength / Low Risk | Stronger balance sheets and lower risk may improve resilience | Leverage, realized volatility |

The modular engine winsorizes and standardizes raw signals cross-sectionally, builds factor scores, combines them into a composite score, forms systematic portfolios, measures turnover, and evaluates subsequent performance.

## Repository Structure

```text
multi-factor-equity-research/
├── .github/workflows/tests.yml       # CI validation
├── multifactor_equity_research_github.ipynb
├── README.md
├── LICENSE
├── CITATION.cff
├── pyproject.toml
├── requirements.txt
├── examples/
│   └── run_demo.py                   # simulated end-to-end smoke test
├── src/
│   ├── data.py                       # price/universe ingestion
│   ├── sec.py                        # SEC Company Facts client
│   ├── signals.py                    # price/fundamental signals
│   ├── factors.py                    # winsorization and factor scoring
│   ├── portfolio.py                  # ranking, weights, turnover
│   ├── backtest.py                   # forward-return backtest + costs
│   ├── metrics.py                    # performance statistics
│   ├── reporting.py                  # result exports and figures
│   ├── pipeline.py                   # end-to-end engine
│   └── config.py
├── tests/
│   ├── test_research.py
│   └── test_data.py
├── data/
│   └── README.md                     # provenance and schemas
├── results/
├── figures/
└── report/
    └── research_note.md
```

## Reproducibility

Install the environment:

```bash
pip install -r requirements.txt
```

Run the test suite:

```bash
python -m pytest
```

Run the deterministic simulated-data demonstration:

```bash
python examples/run_demo.py
```

The demo proves the research engine runs end to end; its output is **not** an empirical investment result.

GitHub Actions runs the automated tests on every push and pull request.

## Expected Data Schemas

Historical adjusted prices:

```text
date | ticker | adj_close
```

Historical point-in-time index membership:

```text
date | ticker
```

Canonical point-in-time fundamentals:

```text
date | ticker | market_cap | net_income | book_equity | free_cash_flow |
gross_profit | total_assets | total_debt
```

The SEC ingestion layer uses filing availability dates so that a financial statement cannot enter a portfolio before it was public. A descriptive `SEC_USER_AGENT` environment variable is required for automated SEC requests.

## Core Research Engine

```python
from src.config import BacktestConfig
from src.pipeline import run_research_pipeline

factor_columns = {
    "value": ["earnings_yield", "book_to_market"],
    "momentum": ["momentum_12_1"],
    "quality": ["roe", "gross_profitability"],
    "low_volatility": ["neg_volatility_12m"],
}

outputs = run_research_pipeline(
    signals=signals,
    forward_returns=forward_returns,
    factor_columns=factor_columns,
    config=BacktestConfig(
        top_quantile=0.20,
        transaction_cost_bps=10.0,
        annualization_factor=12,
    ),
)

print(outputs["summary"])
```

## Research Controls

The repository explicitly addresses several common backtesting failures:

- **Survivorship bias:** historical rather than present-day constituent membership.
- **Look-ahead bias:** formation-date signals are separated from subsequent returns.
- **Accounting publication lag:** SEC facts are mapped using filing availability dates.
- **Outliers:** configurable cross-sectional winsorization.
- **Scale differences:** date-level z-score standardization.
- **Trading frictions:** turnover and configurable transaction costs.
- **Reproducibility:** modular code, dependency metadata, tests, CI, and documented schemas.

## Interpretation

The corrected strategy did not beat SPY over the full sample. That is the main research conclusion, not something hidden as an inconvenience. The project shows how an apparently successful model can lose its headline result after a realistic data-quality correction—and why robust investment research requires actively trying to falsify attractive findings.

For the complete narrative, see [`report/research_note.md`](report/research_note.md) and the original notebook.

## Limitations

The sample is relatively short and includes unusual market regimes. Results remain sensitive to factor definitions, constituent-history quality, corporate-action handling, reporting lags, transaction costs, rebalance frequency, sector treatment, delistings, and historical fundamental coverage. Backtested performance is not live investment performance and is not evidence of future returns.

## Author

**Fiona Rramilli**  
MSc Finance — University of Neuchâtel

*Independent academic/portfolio research. For educational and research purposes only; not investment advice.*
