# Multi-Factor Equity Research & Backtesting Framework

**Fiona Rramilli**  
MSc Finance, University of Neuchâtel  
August 2026

## Abstract

This project tests a sector-relative equity selection model based on Value, Quality, Financial Strength and Momentum across S&P 500 stocks from April 2020 to April 2026. The first four-factor backtest produced a 24.32% CAGR compared with 19.39% for SPY. I then audited the result, reconstructed historical S&P 500 membership, expanded coverage for former constituents and reran the same model without changing the factor definitions or weights. The corrected model produced a 14.63% CAGR, 38.72% volatility and a 0.49 Sharpe ratio, compared with 19.39%, 24.71% and 0.86 for SPY. The historical-universe correction therefore materially changed the conclusion. Factor diagnostics across 1,759 stock-year observations identified sector-relative Value as the strongest of the four simple signals tested.

## 1. Research design

The model ranks eligible companies relative to others in the same sector. Four percentile scores are combined with equal weights:

| Factor | Construction | Higher score represents |
| --- | --- | --- |
| Value | Historical trailing P/E | Lower valuation |
| Quality | Operating margin and ROE | Higher profitability |
| Financial Strength | Debt-to-equity | Lower leverage |
| Momentum | Trailing 12-month adjusted return | Stronger prior performance |

The primary portfolio consists of the 20 highest-ranked eligible stocks at an annual April rebalance. Holdings are equal weighted and held for approximately one year. SPY is the benchmark. Financials are excluded because conventional operating margin and debt-to-equity are not directly comparable with bank and insurer balance sheets.

Historical accounting data is reconstructed from SEC EDGAR company facts / XBRL filings available by the relevant measurement date. Historical trailing P/E is built from historical diluted EPS and price data, with stock-split treatment where required.

## 2. Initial backtest

The first four-factor result looked strong:

| Metric | Original V2 | SPY |
| --- | ---: | ---: |
| Final value of $1 | $3.692 | $2.896 |
| CAGR | 24.32% | 19.39% |
| Volatility | 43.48% | 24.71% |
| Sharpe ratio | 0.69 | 0.86 |

The return was higher than SPY, but so was volatility, and the model's Sharpe ratio was lower.

### Extreme-return audit

The 2023–2024 portfolio returned 84.17%. SMCI was the largest contributor, returning approximately 820% over the holding period. Raw and adjusted closing prices produced the same result. The company's later 10-for-1 split occurred outside the holding period and did not explain the move.

Removing SMCI reduced the annual portfolio return from 84.17% to 45.43%. The median portfolio holding returned 38.42%. The result was therefore not solely a data error, but it showed that the portfolio was meaningfully influenced by an extreme winner.

## 3. Historical-universe correction

The larger problem was the investment universe. The original test used companies that are members of the S&P 500 today. That is not a valid historical investable universe because index membership changes over time.

Comparing April 2020 membership with the current index showed that 111 2020 constituents were no longer present, 115 current constituents had not yet entered the index and only 388 names were common to both sets.

I therefore reconstructed date-specific S&P 500 membership, expanded the historical price universe, recovered missing sector classifications for former constituents and rebuilt the non-financial investable universe at each rebalance date.

| Rebalance date | Historical members | Price usable | Price coverage |
| --- | ---: | ---: | ---: |
| 2020-04-01 | 499 | 436 | 87.4% |
| 2021-04-01 | 501 | 447 | 89.2% |
| 2022-04-01 | 500 | 457 | 91.4% |
| 2023-04-03 | 498 | 471 | 94.6% |
| 2024-04-01 | 503 | 484 | 96.2% |
| 2025-04-01 | 503 | 489 | 97.2% |

The factor definitions and equal weights were left unchanged after this correction.

## 4. Corrected results

| Period | Historical V2 | SPY | Excess return |
| --- | ---: | ---: | ---: |
| 2020–2021 | 90.12% | 65.36% | +24.76% |
| 2021–2022 | 5.65% | 14.55% | -8.90% |
| 2022–2023 | -12.25% | -7.73% | -4.52% |
| 2023–2024 | 35.49% | 28.90% | +6.59% |
| 2024–2025 | -9.57% | 8.80% | -18.37% |
| 2025–2026 | 5.06% | 18.14% | -13.08% |

| Metric | Historical V2 | SPY |
| --- | ---: | ---: |
| Final value of $1 | $2.269 | $2.896 |
| CAGR | 14.63% | 19.39% |
| Volatility | 38.72% | 24.71% |
| Sharpe ratio | 0.49 | 0.86 |
| Annual periods won | 2 / 6 | 4 / 6 |

The corrected strategy did not outperform SPY over the full sample. The drop from 24.32% CAGR to 14.63% shows that the original headline performance was not robust to a more realistic historical constituent universe.

## 5. Factor diagnostics

Spearman information coefficients were calculated between each factor score and subsequent stock return across 1,759 stock-year observations.

| Factor | Pooled IC | Pooled IC excluding 2020 |
| --- | ---: | ---: |
| Value | +0.034 | +0.012 |
| Quality | +0.003 | +0.014 |
| Momentum | -0.022 | -0.001 |
| Financial Strength | -0.025 | -0.032 |

Value produced the strongest positive relationship with subsequent returns.

### Quintile analysis

| Factor | Q1 | Q2 | Q3 | Q4 | Q5 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Value | 18.11% | 17.98% | 19.21% | 24.56% | 28.68% |
| Quality | 26.45% | 18.72% | 21.95% | 21.34% | 19.98% |
| Financial Strength | 23.48% | 24.71% | 19.25% | 18.64% | 22.47% |
| Momentum | 28.46% | 25.37% | 18.70% | 18.63% | 17.18% |

Value shows the clearest positive pattern, with average forward return increasing from 18.11% in Q1 to 28.68% in Q5. Quality is close to neutral. Financial Strength is weak. Momentum is strongly affected by 2020 and is approximately neutral in the pooled IC test once 2020 is excluded.

## 6. Robustness and limitations

Top 10, Top 20 and Top 30 versions of the original V2 showed a consistent trade-off between concentration and risk. Smaller portfolios produced higher returns and higher volatility. The Top-20 portfolio remained the primary specification rather than selecting the best-performing cutoff after the fact.

The project remains subject to important limitations. The sample contains only six annual holding periods. Historical price and sector coverage is incomplete for some former constituents. Transaction costs, taxes and market impact are not included. The Sharpe ratio is estimated from a small number of annual observations. Historical membership reconstruction materially reduces future-membership bias, but the resulting test is not described as perfectly survivorship-bias-free.

## 7. Conclusion

The project does not support the claim that this four-factor strategy consistently beats the S&P 500. After the historical-universe correction, the model generated a lower CAGR, higher volatility and lower Sharpe ratio than SPY.

The more useful finding is methodological. A backtest that initially looked strong changed materially when historical membership, filing timing, stock splits, missing observations and extreme winners were examined more carefully. Among the four simple signals tested, sector-relative Value showed the strongest cross-sectional relationship with subsequent returns over the sample.

The full implementation is available in the repository notebook.