# Data

This directory documents the datasets used by the project. Raw third-party datasets are intentionally not committed when redistribution is restricted.

## Required Inputs

### Historical prices

Long-form CSV or Parquet with:

```text
date | ticker | adj_close
```

Prices should be adjusted for corporate actions and should cover enough history to calculate the intended momentum and volatility windows.

### Historical index membership

Point-in-time membership snapshots with:

```text
date | ticker
```

Using today's S&P 500 members for the entire sample would create survivorship bias. The research pipeline therefore expects historical membership aligned to each portfolio formation date.

### Fundamental data

The project can ingest standardized SEC Company Facts data and map filings to portfolio dates using the public filing date rather than the fiscal-period end date. This prevents accounting information from entering a backtest before it was publicly available.

The SEC client requires a descriptive `SEC_USER_AGENT` environment variable before automated requests are made, for example:

```bash
export SEC_USER_AGENT="Your Name your.email@example.com"
```

The code uses the SEC `data.sec.gov` Company Facts endpoint and downloads issuers sequentially with a conservative delay. For large-scale retrieval, prefer the SEC's published bulk archives rather than issuing many individual requests.

## Canonical Fundamental Panel

After point-in-time alignment, the internal research table uses generic fields such as:

```text
date | ticker | market_cap | net_income | book_equity | free_cash_flow |
gross_profit | total_assets | total_debt
```

This makes the factor engine independent of any one data vendor. SEC XBRL tags or fields from a licensed dataset can be mapped into this canonical schema before signal construction.

## Data Integrity Rules

- use point-in-time constituent membership;
- use adjusted prices;
- use filing/public availability dates for accounting information;
- retain the raw source field/tag mapping in research notes;
- avoid silently forward-filling stale fundamentals without a documented limit;
- document ticker changes, mergers, delistings, and missing observations;
- do not commit proprietary or redistribution-restricted raw data.
