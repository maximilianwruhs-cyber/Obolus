"""
Integration test: end-to-end bench → recommend pipeline.
Tests the full flow without requiring Ollama (uses mocked inference).
"""
import sys
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.benchmark.evaluator import score_math, score_factual
from src.benchmark.fitness_scorer import TrialResult, ScoringConfig, evaluate_mutation
from src.benchmark.recommender import project_costs, cloud_equivalent, recommend
from src.benchmark.task_suite import get_suite, list_suites, SUITES


def test_suite_sizes():
    """Verify task suite sizes are substantial enough."""
    sizes = list_suites()
    assert sizes["math"] == 15
    assert sizes["math_hard"] == 15
    assert sizes["code"] >= 10
    assert sizes["code_hard"] >= 10
    assert sizes["factual"] >= 15
    assert sizes["reasoning"] >= 10
    assert sizes["reasoning_hard"] >= 10
    assert sizes["standard"] == sizes["math"] + sizes["code"] + sizes["factual"] + sizes["reasoning"]
    assert sizes["hard"] == sizes["math_hard"] + sizes["code_hard"] + sizes["reasoning_hard"]
    assert sizes["full"] == sizes["standard"] + sizes["hard"]
    print(f"  ✅ PASS: suite sizes (full={sizes['full']} tasks)")


def test_all_math_tasks_have_answers():
    """Every math task must have an answer field."""
    for task in get_suite("math") + get_suite("math_hard"):
        assert "answer" in task, f"Task {task['id']} missing answer"
        assert task["answer"].strip(), f"Task {task['id']} has empty answer"
    print("  ✅ PASS: all math tasks have answers")


def test_all_code_tasks_have_tests():
    """Every code task must have a test field."""
    for task in get_suite("code") + get_suite("code_hard"):
        assert "test" in task, f"Task {task['id']} missing test"
        assert "PASS" in task["test"], f"Task {task['id']} test doesn't check for PASS"
    print("  ✅ PASS: all code tasks have tests")


def test_all_reasoning_tasks_have_rubrics():
    """Every reasoning task must have a rubric field."""
    for task in get_suite("reasoning") + get_suite("reasoning_hard"):
        assert "rubric" in task, f"Task {task['id']} missing rubric"
        assert "Must" in task["rubric"], f"Task {task['id']} rubric should have 'Must' criteria"
    print("  ✅ PASS: all reasoning tasks have rubrics")


def test_pipeline_bench_to_fitness():
    """Simulate: run tasks → score → fitness evaluation."""
    tasks = get_suite("math")[:5]

    # Simulate model outputs (some correct, some wrong)
    mock_outputs = {
        tasks[0]["id"]: tasks[0]["answer"],  # correct
        tasks[1]["id"]: tasks[1]["answer"],  # correct
        tasks[2]["id"]: "wrong answer",       # wrong
        tasks[3]["id"]: tasks[3]["answer"],  # correct
        tasks[4]["id"]: tasks[4]["answer"],  # correct
    }

    scores = []
    for task in tasks:
        output = mock_outputs[task["id"]]
        score = score_math(output, task["answer"])
        scores.append(score)

    # 4/5 correct = 0.8 quality
    avg_score = sum(scores) / len(scores)
    assert avg_score == 0.8

    # Feed into fitness scorer
    trials = [
        TrialResult(passed=(s > 0), execution_time_ms=100, output_similarity=s)
        for s in scores
    ]
    config = ScoringConfig(baseline_time_ms=200, baseline_energy_joules=50)
    fitness = evaluate_mutation(trials=trials, energy_joules=30, config=config)

    assert fitness.quality > 0
    assert fitness.efficiency > 1.0  # 30J < 50J baseline
    assert fitness.z_score > 0
    assert fitness.approved  # Should pass default thresholds
    print(f"  ✅ PASS: bench → fitness pipeline (z={fitness.z_score:.4f})")


def test_pipeline_fitness_to_recommend():
    """Simulate: fitness results → recommendation."""
    # Create synthetic benchmark results
    results = [
        {
            "model": "fast-model:1.5b",
            "z_score": 0.8,
            "avg_quality": 0.75,
            "total_joules": 20.0,
            "total_tokens": 200,
            "total_tasks": 10,
            "scores_by_type": {"math": {"avg_score": 0.75}},
        },
        {
            "model": "smart-model:7b",
            "z_score": 0.3,
            "avg_quality": 0.95,
            "total_joules": 80.0,
            "total_tokens": 600,
            "total_tasks": 10,
            "scores_by_type": {"math": {"avg_score": 0.95}},
        },
    ]

    rec = recommend(results=results)
    assert rec is not None

    # Fast model should win overall (higher z)
    assert rec["best_overall"]["model"] == "fast-model:1.5b"
    assert rec["best_overall"]["z_score"] == 0.8

    # Cost projections should exist for all scales
    for scale in ["personal", "team", "enterprise"]:
        assert scale in rec["cost_projections"]
        c = rec["cost_projections"][scale]
        assert c["eur_per_month"] >= 0
        assert c["eur_per_year"] >= 0

    # Cloud comparison should show savings
    for provider in ["gpt-4o", "claude-3.5"]:
        assert provider in rec["cloud_comparison"]

    print("  ✅ PASS: fitness → recommend pipeline")


def test_task_ids_unique():
    """All task IDs across all suites must be unique."""
    all_ids = set()
    for task in get_suite("full"):
        assert task["id"] not in all_ids, f"Duplicate ID: {task['id']}"
        all_ids.add(task["id"])
    print(f"  ✅ PASS: all {len(all_ids)} task IDs unique")


if __name__ == "__main__":
    print("\n=== Obolus Integration Tests ===\n")
    test_suite_sizes()
    test_all_math_tasks_have_answers()
    test_all_code_tasks_have_tests()
    test_all_reasoning_tasks_have_rubrics()
    test_pipeline_bench_to_fitness()
    test_pipeline_fitness_to_recommend()
    test_task_ids_unique()
    print("\n=== All integration tests passed! ===\n")
