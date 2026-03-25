"""
Tests for Obolus aWATTar Bridge — price parsing, fallback, negative prices.
Uses mocked HTTP responses (no API calls).
"""
import sys
import json
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.benchmark.awattar import get_current_price_c_kwh, get_price_or_default


def _mock_awattar_response(market_price_eur_mwh, now_ms=None):
    """Create a mock aWATTar API response."""
    now_ms = now_ms or (time.time() * 1000)
    mock = MagicMock()
    mock.status_code = 200
    mock.json.return_value = {
        "data": [
            {
                "start_timestamp": now_ms - 3_600_000,
                "end_timestamp": now_ms + 3_600_000,
                "marketprice": market_price_eur_mwh,
            }
        ]
    }
    return mock


def test_normal_price():
    """Normal positive price conversion: €/MWh → ¢/kWh."""
    # 50 €/MWh = 5.0 ¢/kWh
    with patch("src.benchmark.awattar.requests.get", return_value=_mock_awattar_response(50.0)):
        price = get_current_price_c_kwh()
    assert price == 5.0
    print("  ✅ PASS: normal price (50 €/MWh = 5.0 ¢/kWh)")


def test_expensive_price():
    """High price."""
    # 250 €/MWh = 25.0 ¢/kWh
    with patch("src.benchmark.awattar.requests.get", return_value=_mock_awattar_response(250.0)):
        price = get_current_price_c_kwh()
    assert price == 25.0
    print("  ✅ PASS: expensive price (250 €/MWh = 25.0 ¢/kWh)")


def test_negative_price():
    """Negative prices happen when grid has excess renewable supply."""
    # -20 €/MWh = -2.0 ¢/kWh
    with patch("src.benchmark.awattar.requests.get", return_value=_mock_awattar_response(-20.0)):
        price = get_current_price_c_kwh()
    assert price == -2.0
    print("  ✅ PASS: negative price (-20 €/MWh = -2.0 ¢/kWh)")


def test_zero_price():
    """Zero price."""
    with patch("src.benchmark.awattar.requests.get", return_value=_mock_awattar_response(0.0)):
        price = get_current_price_c_kwh()
    assert price == 0.0
    print("  ✅ PASS: zero price")


def test_api_failure_returns_none():
    """Should return None when API is unreachable."""
    with patch("src.benchmark.awattar.requests.get", side_effect=Exception("Timeout")):
        price = get_current_price_c_kwh()
    assert price is None
    print("  ✅ PASS: API failure returns None")


def test_get_price_or_default_uses_live():
    """Should use live price when available."""
    with patch("src.benchmark.awattar.requests.get", return_value=_mock_awattar_response(46.0)):
        price = get_price_or_default(default_c_kwh=25.0)
    assert price == 4.6
    print("  ✅ PASS: get_price_or_default uses live")


def test_get_price_or_default_fallback():
    """Should use default when API fails."""
    with patch("src.benchmark.awattar.requests.get", side_effect=Exception("Error")):
        price = get_price_or_default(default_c_kwh=25.0)
    assert price == 25.0
    print("  ✅ PASS: get_price_or_default fallback")


def test_empty_data():
    """Should handle empty data array."""
    mock = MagicMock()
    mock.json.return_value = {"data": []}
    with patch("src.benchmark.awattar.requests.get", return_value=mock):
        price = get_current_price_c_kwh()
    assert price is None
    print("  ✅ PASS: empty data array")


def test_no_matching_period():
    """Should return latest entry when no period matches current time."""
    mock = MagicMock()
    mock.json.return_value = {
        "data": [
            {"start_timestamp": 0, "end_timestamp": 1000, "marketprice": 100.0},
            {"start_timestamp": 1000, "end_timestamp": 2000, "marketprice": 150.0},
        ]
    }
    with patch("src.benchmark.awattar.requests.get", return_value=mock):
        price = get_current_price_c_kwh()
    # Should fall back to latest entry: 150 €/MWh = 15.0 ¢/kWh
    assert price == 15.0
    print("  ✅ PASS: no matching period — uses latest")


if __name__ == "__main__":
    print("\n=== Obolus aWATTar Tests ===\n")
    test_normal_price()
    test_expensive_price()
    test_negative_price()
    test_zero_price()
    test_api_failure_returns_none()
    test_get_price_or_default_uses_live()
    test_get_price_or_default_fallback()
    test_empty_data()
    test_no_matching_period()
    print("\n=== All aWATTar tests passed! ===\n")
