"""
Tests for Obolus electricity price resolution — offline-first + optional aWATTar.
Uses mocked HTTP responses (no API calls).
"""
import sys
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

import config
from src.benchmark.awattar import (
    get_current_price_c_kwh,
    get_price_or_default,
    resolve_price,
)


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
    with patch("src.benchmark.awattar.requests.get", return_value=_mock_awattar_response(50.0)):
        price = get_current_price_c_kwh()
    assert price == 5.0


def test_expensive_price():
    with patch("src.benchmark.awattar.requests.get", return_value=_mock_awattar_response(250.0)):
        price = get_current_price_c_kwh()
    assert price == 25.0


def test_negative_price():
    with patch("src.benchmark.awattar.requests.get", return_value=_mock_awattar_response(-20.0)):
        price = get_current_price_c_kwh()
    assert price == -2.0


def test_zero_price():
    with patch("src.benchmark.awattar.requests.get", return_value=_mock_awattar_response(0.0)):
        price = get_current_price_c_kwh()
    assert price == 0.0


def test_api_failure_returns_none():
    with patch("src.benchmark.awattar.requests.get", side_effect=Exception("Timeout")):
        price = get_current_price_c_kwh()
    assert price is None


def test_resolve_offline_default_skips_network():
    """Offline (default) must not call the network."""
    with patch.object(config, "PRICE_SOURCE", "offline"), \
         patch.object(config, "ELECTRICITY_C_KWH", 25.0), \
         patch("src.benchmark.awattar.requests.get") as mock_get:
        price, is_live = resolve_price()
    assert price == 25.0
    assert is_live is False
    mock_get.assert_not_called()


def test_resolve_awattar_uses_live():
    with patch.object(config, "PRICE_SOURCE", "awattar"), \
         patch.object(config, "ELECTRICITY_C_KWH", 25.0), \
         patch("src.benchmark.awattar.requests.get", return_value=_mock_awattar_response(46.0)):
        price, is_live = resolve_price()
    assert price == 4.6
    assert is_live is True


def test_resolve_awattar_fallback():
    with patch.object(config, "PRICE_SOURCE", "awattar"), \
         patch.object(config, "ELECTRICITY_C_KWH", 25.0), \
         patch("src.benchmark.awattar.requests.get", side_effect=Exception("Error")):
        price, is_live = resolve_price()
    assert price == 25.0
    assert is_live is False


def test_get_price_or_default_respects_offline():
    with patch.object(config, "PRICE_SOURCE", "offline"), \
         patch.object(config, "ELECTRICITY_C_KWH", 25.0), \
         patch("src.benchmark.awattar.requests.get") as mock_get:
        price = get_price_or_default()
    assert price == 25.0
    mock_get.assert_not_called()


def test_get_price_or_default_awattar_live():
    with patch.object(config, "PRICE_SOURCE", "awattar"), \
         patch("src.benchmark.awattar.requests.get", return_value=_mock_awattar_response(46.0)):
        price = get_price_or_default(default_c_kwh=25.0)
    assert price == 4.6


def test_empty_data():
    mock = MagicMock()
    mock.json.return_value = {"data": []}
    with patch("src.benchmark.awattar.requests.get", return_value=mock):
        price = get_current_price_c_kwh()
    assert price is None


def test_no_matching_period():
    mock = MagicMock()
    mock.json.return_value = {
        "data": [
            {"start_timestamp": 0, "end_timestamp": 1000, "marketprice": 100.0},
            {"start_timestamp": 1000, "end_timestamp": 2000, "marketprice": 150.0},
        ]
    }
    with patch("src.benchmark.awattar.requests.get", return_value=mock):
        price = get_current_price_c_kwh()
    assert price == 15.0
