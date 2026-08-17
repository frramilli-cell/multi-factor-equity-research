from __future__ import annotations

import os
import time
from typing import Iterable

import pandas as pd
import requests


SEC_BASE = "https://data.sec.gov/api/xbrl/companyfacts"


def sec_headers(user_agent: str | None = None) -> dict[str, str]:
    """Build SEC-compliant request headers.

    Set ``SEC_USER_AGENT`` to a descriptive string such as
    ``Your Name your.email@example.com`` before making automated requests.
    """
    value = user_agent or os.getenv("SEC_USER_AGENT")
    if not value:
        raise ValueError(
            "SEC_USER_AGENT is required. Set it to a descriptive contact string before downloading SEC data."
        )
    return {"User-Agent": value, "Accept-Encoding": "gzip, deflate"}


def normalize_cik(cik: str | int) -> str:
    digits = "".join(ch for ch in str(cik) if ch.isdigit())
    if not digits:
        raise ValueError("CIK must contain digits.")
    return digits.zfill(10)


def fetch_company_facts(
    cik: str | int,
    user_agent: str | None = None,
    timeout: float = 30.0,
) -> dict:
    """Fetch one issuer's SEC Company Facts JSON payload."""
    cik10 = normalize_cik(cik)
    response = requests.get(
        f"{SEC_BASE}/CIK{cik10}.json",
        headers=sec_headers(user_agent),
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()


def extract_company_concept(
    payload: dict,
    tag: str,
    taxonomy: str = "us-gaap",
    preferred_units: Iterable[str] = ("USD", "shares", "USD/shares", "pure"),
) -> pd.DataFrame:
    """Flatten a standard SEC XBRL concept into filing-level observations."""
    facts = payload.get("facts", {}).get(taxonomy, {}).get(tag)
    if not facts:
        return pd.DataFrame(
            columns=["cik", "entity", "tag", "unit", "value", "start", "end", "filed", "form", "fy", "fp", "accn"]
        )

    units = facts.get("units", {})
    chosen_unit = next((unit for unit in preferred_units if unit in units), None)
    if chosen_unit is None and units:
        chosen_unit = next(iter(units))
    if chosen_unit is None:
        return pd.DataFrame()

    rows = []
    for item in units[chosen_unit]:
        rows.append(
            {
                "cik": str(payload.get("cik", "")).zfill(10),
                "entity": payload.get("entityName"),
                "tag": tag,
                "unit": chosen_unit,
                "value": item.get("val"),
                "start": item.get("start"),
                "end": item.get("end"),
                "filed": item.get("filed"),
                "form": item.get("form"),
                "fy": item.get("fy"),
                "fp": item.get("fp"),
                "accn": item.get("accn"),
            }
        )

    out = pd.DataFrame(rows)
    for col in ("start", "end", "filed"):
        if col in out:
            out[col] = pd.to_datetime(out[col], errors="coerce")
    return out.sort_values(["filed", "end"], na_position="last").reset_index(drop=True)


def latest_available_facts(
    facts: pd.DataFrame,
    formation_dates: pd.Series,
    reporting_lag_days: int = 1,
) -> pd.DataFrame:
    """Map each formation date to the latest fact filed before it.

    Using ``filed`` rather than fiscal-period end prevents a financial statement
    from entering the strategy before it was publicly available. An optional
    additional reporting lag can be imposed conservatively.
    """
    if facts.empty:
        return pd.DataFrame(columns=["date", "value", "filed", "end"])
    required = {"filed", "value"}
    if missing := required.difference(facts.columns):
        raise ValueError(f"Facts missing columns: {sorted(missing)}")

    right = facts.dropna(subset=["filed", "value"]).copy().sort_values("filed")
    right["available_date"] = right["filed"] + pd.to_timedelta(reporting_lag_days, unit="D")
    left = pd.DataFrame({"date": pd.to_datetime(formation_dates)}).drop_duplicates().sort_values("date")

    mapped = pd.merge_asof(
        left,
        right,
        left_on="date",
        right_on="available_date",
        direction="backward",
    )
    return mapped


def download_company_facts_batch(
    ciks: Iterable[str | int],
    user_agent: str | None = None,
    delay_seconds: float = 0.12,
) -> dict[str, dict]:
    """Download Company Facts sequentially with a conservative request delay."""
    result: dict[str, dict] = {}
    for cik in ciks:
        cik10 = normalize_cik(cik)
        result[cik10] = fetch_company_facts(cik10, user_agent=user_agent)
        if delay_seconds > 0:
            time.sleep(delay_seconds)
    return result
