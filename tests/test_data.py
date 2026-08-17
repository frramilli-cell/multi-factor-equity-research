import pandas as pd

from src.data import build_forward_returns, monthly_prices
from src.sec import extract_company_concept, latest_available_facts, normalize_cik
from src.signals import add_price_signals, build_fundamental_signals


def test_normalize_cik():
    assert normalize_cik(320193) == "0000320193"


def test_extract_company_concept():
    payload = {
        "cik": 1234,
        "entityName": "Example Corp",
        "facts": {
            "us-gaap": {
                "NetIncomeLoss": {
                    "units": {
                        "USD": [
                            {
                                "val": 100.0,
                                "start": "2024-01-01",
                                "end": "2024-12-31",
                                "filed": "2025-02-15",
                                "form": "10-K",
                                "fy": 2024,
                                "fp": "FY",
                                "accn": "0001",
                            }
                        ]
                    }
                }
            }
        },
    }
    out = extract_company_concept(payload, "NetIncomeLoss")
    assert len(out) == 1
    assert out.loc[0, "value"] == 100.0
    assert out.loc[0, "cik"] == "0000001234"


def test_latest_available_facts_respects_filing_date():
    facts = pd.DataFrame(
        {
            "filed": pd.to_datetime(["2024-02-15", "2025-02-15"]),
            "end": pd.to_datetime(["2023-12-31", "2024-12-31"]),
            "value": [10.0, 20.0],
        }
    )
    dates = pd.Series(pd.to_datetime(["2024-01-31", "2024-03-31", "2025-03-31"]))
    out = latest_available_facts(facts, dates, reporting_lag_days=1)
    assert pd.isna(out.loc[out["date"] == pd.Timestamp("2024-01-31"), "value"]).all()
    assert out.loc[out["date"] == pd.Timestamp("2024-03-31"), "value"].iloc[0] == 10.0
    assert out.loc[out["date"] == pd.Timestamp("2025-03-31"), "value"].iloc[0] == 20.0


def test_monthly_forward_returns():
    prices = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-30", "2024-01-31", "2024-02-29", "2024-03-28"]),
            "ticker": ["A", "A", "A", "A"],
            "adj_close": [99.0, 100.0, 110.0, 121.0],
        }
    )
    monthly = monthly_prices(prices)
    assert monthly.iloc[0]["adj_close"] == 100.0
    forward = build_forward_returns(prices)
    assert round(forward.iloc[0]["forward_return"], 6) == 0.1


def test_price_and_fundamental_signals():
    dates = pd.date_range("2023-01-31", periods=14, freq="ME")
    prices = pd.DataFrame(
        {"date": dates, "ticker": ["A"] * len(dates), "adj_close": range(100, 114)}
    )
    price_signals = add_price_signals(prices)
    assert "momentum_12_1" in price_signals.columns
    assert "neg_volatility_12m" in price_signals.columns

    fundamentals = pd.DataFrame(
        {
            "date": [pd.Timestamp("2024-01-31")],
            "ticker": ["A"],
            "market_cap": [1000.0],
            "net_income": [100.0],
            "book_equity": [500.0],
            "gross_profit": [300.0],
            "total_assets": [1200.0],
            "total_debt": [200.0],
        }
    )
    signals = build_fundamental_signals(fundamentals)
    assert signals.loc[0, "earnings_yield"] == 0.1
    assert signals.loc[0, "book_to_market"] == 0.5
    assert signals.loc[0, "roe"] == 0.2
