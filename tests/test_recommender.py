"""
Tests for Obolus Recommender — cost projections, cloud comparison, live pricing.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.benchmark.recommender import (
    project_costs,
    cloud_equivalent,
    recommend,
    load_organ_hints,
)


def test_project_costs_basic():
    """Basic cost projection at known values."""
    result = project_costs(
        joules_per_run=10.0,
        tokens_per_run=100,
        queries_per_day=1000,
        electricity_c_kwh=25.0
    )
    assert result["queries_per_day"] == 1000
    assert result["joules_per_day"] == 10000.0
    # 10000J / 3600000 = 0.002778 kWh, * 25/100 = 0.000694 EUR/day
    assert result["kwh_per_day"] > 0
    assert result["eur_per_day"] > 0
    assert result["eur_per_month"] > result["eur_per_day"]
    assert result["eur_per_year"] > result["eur_per_month"]
    print("  ✅ PASS: project_costs basic")


def test_project_costs_zero_queries():
    """Zero queries = zero cost."""
    result = project_costs(10.0, 100, 0, 25.0)
    assert result["joules_per_day"] == 0
    assert result["eur_per_day"] == 0
    assert result["eur_per_month"] == 0
    print("  ✅ PASS: project_costs zero queries")


def test_project_costs_free_electricity():
    """Free electricity = zero cost."""
    result = project_costs(10.0, 100, 1000, 0.0)
    assert result["eur_per_day"] == 0
    assert result["eur_per_year"] == 0
    print("  ✅ PASS: project_costs free electricity")


def test_project_costs_negative_price():
    """Negative electricity price (common in renewables)."""
    result = project_costs(10.0, 100, 1000, -5.0)
    assert result["eur_per_day"] < 0  # Grid pays you!
    print("  ✅ PASS: project_costs negative price")


def test_cloud_equivalent():
    """Cloud cost estimation produces reasonable values."""
    result = cloud_equivalent(tokens_per_run=100, queries_per_day=1000)
    assert "gpt-4o" in result
    assert "claude-3.5" in result
    assert "gemini-1.5" in result

    # GPT-4o should be more expensive than GPT-4o-mini
    assert result["gpt-4o"]["usd_per_month"] > result["gpt-4o-mini"]["usd_per_month"]
    # Claude should be most expensive
    assert result["claude-3.5"]["usd_per_month"] > result["gemini-1.5"]["usd_per_month"]

    for provider, cost in result.items():
        assert cost["usd_per_day"] >= 0
        assert cost["usd_per_year"] > cost["usd_per_month"]
    print("  ✅ PASS: cloud_equivalent")


def test_recommend_no_results():
    """Recommend with no results returns None."""
    result = recommend(results=[])
    assert result is None
    print("  ✅ PASS: recommend empty results")


def test_recommend_with_results():
    """Recommend with synthetic results produces valid output."""
    results = [
        {
            "model": "test-model:7b",
            "z_score": 0.5,
            "avg_quality": 0.85,
            "total_joules": 50.0,
            "total_tokens": 500,
            "total_tasks": 10,
            "electricity_c_kwh": 25.0,
            "scores_by_type": {
                "math": {"avg_score": 0.9, "total_tokens": 200},
                "code": {"avg_score": 0.8, "total_tokens": 300},
            },
        },
        {
            "model": "test-model:1.5b",
            "z_score": 0.8,
            "avg_quality": 0.75,
            "total_joules": 20.0,
            "total_tokens": 300,
            "total_tasks": 10,
            "electricity_c_kwh": 25.0,
            "scores_by_type": {
                "math": {"avg_score": 0.7, "total_tokens": 150},
            },
        },
    ]

    rec = recommend(results=results)
    assert rec is not None
    assert rec["best_overall"]["model"] == "test-model:1.5b"  # Higher z
    assert "cost_projections" in rec
    assert "cloud_comparison" in rec
    assert "personal" in rec["cost_projections"]
    assert "team" in rec["cost_projections"]
    assert "enterprise" in rec["cost_projections"]
    print("  ✅ PASS: recommend with results")


def test_recommend_picks_best_per_type():
    """Should pick the best model per task type, not just overall."""
    results = [
        {
            "model": "big-model:7b",
            "z_score": 0.3,
            "avg_quality": 0.95,
            "total_joules": 100.0,
            "total_tokens": 800,
            "total_tasks": 10,
            "scores_by_type": {
                "math": {"avg_score": 0.95},
                "code": {"avg_score": 0.95},
            },
        },
        {
            "model": "small-model:1b",
            "z_score": 0.9,
            "avg_quality": 0.60,
            "total_joules": 10.0,
            "total_tokens": 200,
            "total_tasks": 10,
            "scores_by_type": {
                "math": {"avg_score": 0.60},
            },
        },
    ]
    rec = recommend(results=results)
    # Big model should win math (higher raw quality per joule)
    # Small model wins overall (higher z-score)
    assert rec["best_overall"]["model"] == "small-model:1b"
    print("  ✅ PASS: recommend picks best per type")


def test_load_organ_hints_absent():
    """Missing hints file → None (stranger path unchanged)."""
    assert load_organ_hints(Path("/nonexistent/organ_hints.json")) is None
    print("  ✅ PASS: load_organ_hints absent")


def test_load_organ_hints_valid(tmp_path):
    """Valid Arena export loads tags + z only."""
    path = tmp_path / "organ_hints.json"
    path.write_text(
        '{"version":1,"hints":[{"ollama_tag":"a:1b","z":0.1},'
        '{"ollama_tag":"b:7b","z":0.5}]}'
    )
    hints = load_organ_hints(path)
    assert hints is not None
    assert hints[0]["ollama_tag"] == "b:7b"
    assert hints[0]["z"] == 0.5
    print("  ✅ PASS: load_organ_hints valid")


def test_load_organ_hints_v2_fields(tmp_path):
    """Phase 22 v2 hints keep tag+z and optional role/metric."""
    path = tmp_path / "organ_hints.json"
    path.write_text(
        '{"version":2,"hints":[{"ollama_tag":"obolus-arena-mutator","z":1.0,'
        '"organ_id":"mutator-search-replace","role":"mutator",'
        '"status":"champion","metric":"pass_rate"}]}'
    )
    hints = load_organ_hints(path)
    assert hints is not None
    assert hints[0]["role"] == "mutator"
    assert hints[0]["metric"] == "pass_rate"
    assert hints[0]["z"] == 1.0
    print("  ✅ PASS: load_organ_hints v2 fields")


def test_recommend_without_hints_omits_key(monkeypatch, tmp_path):
    """When hints file missing, recommend dict has no organ_hints key."""
    import config as cfg

    monkeypatch.setattr(cfg, "ORGAN_HINTS_PATH", tmp_path / "missing.json")
    results = [
        {
            "model": "m:1b",
            "z_score": 1.0,
            "avg_quality": 0.9,
            "total_joules": 10.0,
            "total_tokens": 100,
            "total_tasks": 5,
            "scores_by_type": {},
        }
    ]
    rec = recommend(results=results)
    assert "organ_hints" not in rec
    print("  ✅ PASS: recommend omits organ_hints when absent")


def test_recommend_with_hints_includes_key(monkeypatch, tmp_path):
    """When hints present, recommend includes organ_hints without changing best_overall."""
    import config as cfg

    hints_path = tmp_path / "organ_hints.json"
    hints_path.write_text(
        '{"version":1,"hints":[{"ollama_tag":"arena-tag:1.5b","z":0.06}]}'
    )
    monkeypatch.setattr(cfg, "ORGAN_HINTS_PATH", hints_path)
    results = [
        {
            "model": "m:1b",
            "z_score": 1.0,
            "avg_quality": 0.9,
            "total_joules": 10.0,
            "total_tokens": 100,
            "total_tasks": 5,
            "scores_by_type": {},
        }
    ]
    rec = recommend(results=results)
    assert rec["best_overall"]["model"] == "m:1b"
    assert rec["organ_hints"][0]["ollama_tag"] == "arena-tag:1.5b"
    print("  ✅ PASS: recommend includes organ_hints when present")


if __name__ == "__main__":
    print("\n=== Obolus Recommender Tests ===\n")
    test_project_costs_basic()
    test_project_costs_zero_queries()
    test_project_costs_free_electricity()
    test_project_costs_negative_price()
    test_cloud_equivalent()
    test_recommend_no_results()
    test_recommend_with_results()
    test_recommend_picks_best_per_type()
    test_load_organ_hints_absent()
    from pathlib import Path as _P
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        test_load_organ_hints_valid(_P(d))
        test_load_organ_hints_v2_fields(_P(d))
    print("\n=== All recommender tests passed! ===\n")
