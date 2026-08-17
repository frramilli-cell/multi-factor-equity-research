# Multi-Factor Equity Research & Backtesting

Systematic equity research using historical S&P 500 constituents and SEC fundamental data to study whether a transparent, rules-based multi-factor framework can identify stocks with stronger risk-adjusted characteristics.

This repository is structured as an end-to-end research workflow: data preparation, factor construction, cross-sectional ranking, portfolio formation, backtesting, performance evaluation, and robustness analysis.

> **Project status:** Research framework and repository structure established. Empirical outputs will be added only after the analysis is completed and validated.

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

Exact definitions, data treatments, and portfolio rules are documented alongside the implementation so the analysis remains reproducible.

## Research Pipeline

1. **Data preparation** — import, clean, align, and validate market and fundamental data.
2. **Factor construction** — calculate raw factor signals while controlling for missing and extreme observations.
3. **Cross-sectional ranking** — normalize signals to make factor scores comparable across the investment universe.
4. **Composite scoring** — combine individual signals into a diversified multi-factor score.
5. **Portfolio formation** — construct systematic portfolios using predefined ranking and rebalancing rules.
6. **Backtesting** — evaluate the strategy through time while avoiding look-ahead bias.
7. **Performance analysis** — measure return, volatility, drawdown, Sharpe ratio, and benchmark-relative behavior.
8. **Robustness testing** — assess whether conclusions survive alternative assumptions and specifications.

## Repository Structure

```text
multi-factor-equity-research/
├── README.md
├── requirements.txt
├── src/
│   └── README.md
├── data/
│   └── README.md
├── results/
│   └── README.md
├── figures/
│   └── README.md
└── report/
    └── README.md
```

## Methodological Principles

The analysis is built around safeguards that matter in empirical investment research:

- no use of future information in portfolio formation;
- explicit treatment of missing observations and outliers;
- consistent rebalancing and holding-period assumptions;
- separation of signal measurement from subsequent return evaluation;
- benchmark-relative as well as absolute performance measurement;
- transparent reporting of assumptions and limitations.

Where feasible, the final backtest will also account for turnover and transaction-cost sensitivity so that statistical performance is not confused with implementable performance.

## Performance Evaluation

The final analysis will report, at minimum:

- annualized return;
- annualized volatility;
- Sharpe ratio;
- maximum drawdown;
- cumulative wealth;
- benchmark-relative return;
- turnover and transaction-cost sensitivity;
- factor-level and composite portfolio results.

Charts and summary tables will be stored in `figures/` and `results/` rather than embedded as unsupported headline claims.

## Reproducibility

The implementation is being organized as modular Python research code rather than a single opaque notebook. Dependencies are recorded in `requirements.txt`, and `data/` documents data provenance and redistribution restrictions.

## Limitations

Historical backtests are sensitive to data quality, universe definition, factor specification, rebalancing assumptions, transaction costs, and treatment of delisted securities. Backtested performance does not represent live investment performance and should not be interpreted as a guarantee of future returns.

## Author

**Fiona Rramilli**  
MSc Finance — University of Neuchâtel

*Independent academic/portfolio research project. For educational and research purposes only; not investment advice.*
