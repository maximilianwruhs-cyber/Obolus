"""
Obolus — Electricity price resolution
Offline-first: default uses OBULUS_ELECTRICITY_C_KWH.
Optional live source: aWATTar AT spot (OBULUS_PRICE_SOURCE=awattar).
"""
from __future__ import annotations

from datetime import datetime, timezone

import requests

import config

AWATTAR_URL = "https://api.awattar.at/v1/marketdata"


def get_current_price_c_kwh() -> float | None:
    """
    Fetch current electricity spot price in ¢/kWh from AWattar AT.
    Returns None if API is unreachable.
    """
    try:
        resp = requests.get(AWATTAR_URL, timeout=5)
        data = resp.json()
        now_ms = datetime.now(timezone.utc).timestamp() * 1000

        for entry in data.get("data", []):
            if entry["start_timestamp"] <= now_ms <= entry["end_timestamp"]:
                # API returns €/MWh → convert to ¢/kWh
                return entry["marketprice"] / 10.0

        # No matching period — return the latest entry
        entries = data.get("data", [])
        if entries:
            return entries[-1]["marketprice"] / 10.0

    except Exception:
        pass
    return None


def resolve_price(default_c_kwh: float | None = None) -> tuple[float, bool]:
    """
    Resolve electricity price.

    Returns (price_c_kwh, price_is_live).
    Offline (default): configured ¢/kWh, never hits the network.
    awattar: live spot when reachable, else default with price_is_live=False.
    """
    default = config.ELECTRICITY_C_KWH if default_c_kwh is None else default_c_kwh
    if config.PRICE_SOURCE == "awattar":
        live = get_current_price_c_kwh()
        if live is not None:
            return live, True
        return default, False
    return default, False


def get_price_or_default(default_c_kwh: float | None = None) -> float:
    """Convenience wrapper — returns price only (respects OBULUS_PRICE_SOURCE)."""
    price, _ = resolve_price(default_c_kwh)
    return price
