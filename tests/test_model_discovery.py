"""
Tests for Obolus Model Discovery — API parsing, filtering, error handling.
Uses mocked HTTP responses (no Ollama required).
"""
import sys
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.benchmark.model_discovery import discover_models, ModelInfo


def _mock_response(models_data, status_code=200):
    """Create a mock requests.Response."""
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = models_data
    return mock


def test_discover_multiple_models():
    """Should discover and parse multiple models."""
    api_response = {
        "models": [
            {"name": "qwen2.5-coder:7b", "size": 4_500_000_000, "details": {"parameter_size": "7B"}},
            {"name": "qwen2.5-coder:1.5b", "size": 1_200_000_000, "details": {"parameter_size": "1.5B"}},
            {"name": "llama3:8b", "size": 5_000_000_000, "details": {"parameter_size": "8B"}},
        ]
    }
    with patch("src.benchmark.model_discovery.requests.get", return_value=_mock_response(api_response)):
        models = discover_models()

    assert len(models) == 3
    names = [m.name for m in models]
    assert "qwen2.5-coder:7b" in names
    assert "qwen2.5-coder:1.5b" in names
    print("  ✅ PASS: discover multiple models")


def test_filter_embedding_models():
    """Should filter out embedding models."""
    api_response = {
        "models": [
            {"name": "qwen2.5-coder:7b", "size": 4_500_000_000, "details": {"parameter_size": "7B"}},
            {"name": "nomic-embed-text:latest", "size": 300_000_000, "details": {"parameter_size": "137M"}},
            {"name": "mxbai-embed-large:latest", "size": 700_000_000, "details": {"parameter_size": "335M"}},
        ]
    }
    with patch("src.benchmark.model_discovery.requests.get", return_value=_mock_response(api_response)):
        models = discover_models()

    assert len(models) == 1
    assert models[0].name == "qwen2.5-coder:7b"
    print("  ✅ PASS: filter embedding models")


def test_empty_models():
    """Should handle empty model list."""
    api_response = {"models": []}
    with patch("src.benchmark.model_discovery.requests.get", return_value=_mock_response(api_response)):
        models = discover_models()

    assert len(models) == 0
    print("  ✅ PASS: empty models")


def test_api_error():
    """Should handle API errors gracefully."""
    with patch("src.benchmark.model_discovery.requests.get", side_effect=Exception("Connection refused")):
        models = discover_models()

    assert len(models) == 0
    print("  ✅ PASS: API error graceful handling")


def test_model_size_gb():
    """Should correctly convert bytes to GB."""
    api_response = {
        "models": [
            {"name": "test:7b", "size": 4_831_838_208, "details": {"parameter_size": "7B"}},
        ]
    }
    with patch("src.benchmark.model_discovery.requests.get", return_value=_mock_response(api_response)):
        models = discover_models()

    assert len(models) == 1
    assert models[0].size_gb > 4.0
    assert models[0].size_gb < 5.0
    print("  ✅ PASS: model size GB conversion")


def test_missing_details():
    """Should handle models with missing details."""
    api_response = {
        "models": [
            {"name": "test:7b", "size": 4_000_000_000},
        ]
    }
    with patch("src.benchmark.model_discovery.requests.get", return_value=_mock_response(api_response)):
        models = discover_models()

    assert len(models) == 1
    assert models[0].parameter_size == "unknown"
    print("  ✅ PASS: missing details")


if __name__ == "__main__":
    print("\n=== Obolus Model Discovery Tests ===\n")
    test_discover_multiple_models()
    test_filter_embedding_models()
    test_empty_models()
    test_api_error()
    test_model_size_gb()
    test_missing_details()
    print("\n=== All model discovery tests passed! ===\n")
