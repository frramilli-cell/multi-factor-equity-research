# Multi-Factor Equity Strategy — Research Note

## Executive Summary

This project tests whether a sector-relative, rules-based multi-factor stock-selection model can outperform the S&P 500. The model combines Value, Quality, Financial Strength, and Momentum signals and forms an equal-weight portfolio of the highest-ranked stocks.

The most important result is methodological rather than promotional. An early version of the backtest appeared unusually strong. Auditing the result showed that using today's S&P 500 membership in earlier periods introduced survivorship bias and future information into the investment universe. The backtest was therefore rebuilt using historical index membership while leaving the factor logic unchanged.

**After the point-in-time universe correction, the strategy did not outperform SPY over the full sample.**

That corrected result is retained as the principal finding because it demonstrates why universe construction, information timing, and research controls matter as much as factor selection itself.

## Research Design

- **Sample:** April 2020 to April 2026
- **Benchmark:** SPY
- **Portfolio:** Top 20 securities, equal weighted
- **Rebalancing:** Annual in the original research notebook
- **Factors:** Value, Quality, Financial Strength, Momentum
- **Fundamental source:** SEC EDGAR / XBRL company facts
- **Market data:** Historical adjusted market prices
- **Universe:** Historical S&P 500 membership in the corrected specification

## Investment Hypothesis

The strategy tests whether securities that simultaneously look inexpensive, profitable, financially resilient, and positively trending can deliver superior subsequent returns. Combining signals is intended to reduce dependence on any single anomaly and produce a more balanced stock-selection framework.

## Factor Logic

### Value

Value rewards securities trading at more attractive valuations. The research notebook uses valuation information reconstructed with point-in-time accounting data where possible.

### Quality

Quality captures profitability and operating efficiency. Typical inputs include return on equity and operating profitability measures.

### Financial Strength

Financial Strength favors firms with healthier balance sheets and lower leverage. Financial-sector firms require special treatment because leverage has a different economic meaning for banks and other financial institutions.

### Momentum

Momentum captures persistence in relative price performance before each rebalance date. The modular research engine implements a conventional 12–1 momentum signal.

## The Survivorship-Bias Audit

A current-constituent S&P 500 list cannot be safely projected backward through history. Companies that failed, were acquired, or were removed from the index disappear from the current list, while later successful additions are incorrectly treated as if they had always been eligible.

That makes a historical strategy look better informed than an investor could actually have been at the time.

The corrected research therefore uses point-in-time membership snapshots and separates formation-date information from subsequent holding-period returns. Fundamental observations are mapped according to public filing availability rather than fiscal-period end dates.

## Interpretation of the Result

The corrected strategy's failure to beat SPY over the full sample is not treated as a failed project. It is evidence that the apparent excess return in the earlier specification was not robust to a fundamental data-quality correction.

For investment research, this is the more useful conclusion: a plausible model can appear successful because of subtle information leakage, and robust research requires actively trying to disprove attractive results.

## What the Repository Adds Beyond the Notebook

The original notebook documents the research journey and empirical experiment. The `src/` package extracts the reusable research logic into tested modules for:

- input validation and point-in-time universe filtering;
- SEC Company Facts ingestion;
- price and fundamental signal construction;
- cross-sectional winsorization and standardization;
- factor and composite scoring;
- portfolio formation and turnover;
- transaction-cost-aware backtesting;
- performance measurement and reporting.

Automated tests run in GitHub Actions to protect against regressions in the research code.

## Limitations

The sample is relatively short and includes unusual market regimes. Results remain sensitive to factor definitions, constituent-history quality, corporate-action handling, reporting lags, transaction costs, rebalance frequency, sector treatment, delistings, and the availability of historical fundamentals. No backtest should be interpreted as evidence of future investment performance.

## Conclusion

The project began as a search for multi-factor outperformance and became a stronger demonstration of empirical research discipline. The corrected model did not outperform its benchmark, but the audit identified and removed a material survivorship-bias problem. The resulting repository emphasizes reproducibility, point-in-time data handling, transparent assumptions, and honest interpretation over headline performance.
