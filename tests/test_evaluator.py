"""
Tests for Obolus Evaluator — scoring logic for math, factual, code, reasoning.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.benchmark.evaluator import (
    score_math, score_factual, _normalize, _extract_number,
    _heuristic_reasoning_score, score_task,
)


# ─── Math scoring ────────────────────────────────────────────────────────────

def test_math_exact():
    assert score_math("42", "42") == 1.0
    assert score_math("9801", "9801") == 1.0
    print("  ✅ PASS: math exact match")


def test_math_with_text():
    """Should extract number from verbose output."""
    assert score_math("The answer is 42.", "42") == 1.0
    assert score_math("I think it's 9801 because...", "9801") == 1.0
    print("  ✅ PASS: math with surrounding text")


def test_math_wrong():
    assert score_math("43", "42") == 0.0
    assert score_math("The answer is 100", "42") == 0.0
    print("  ✅ PASS: math wrong answer")


def test_math_no_number():
    """No number in output."""
    assert score_math("I don't know", "42") == 0.0
    assert score_math("", "42") == 0.0
    print("  ✅ PASS: math no number")


def test_math_float_comparison():
    """Float answers should work."""
    assert score_math("3.14", "3.14") == 1.0
    assert score_math("3.14159", "3.14") == 0.0  # Not exact
    print("  ✅ PASS: math float comparison")


def test_math_negative():
    """Negative numbers."""
    assert score_math("-5", "-5") == 1.0
    assert score_math("The answer is -42", "-42") == 1.0
    print("  ✅ PASS: math negative numbers")


# ─── Factual scoring ─────────────────────────────────────────────────────────

def test_factual_exact():
    assert score_factual("Au", "Au") == 1.0
    assert score_factual("Mercury", "Mercury") == 1.0
    print("  ✅ PASS: factual exact")


def test_factual_case_insensitive():
    assert score_factual("au", "Au") == 1.0
    assert score_factual("MERCURY", "Mercury") == 1.0
    print("  ✅ PASS: factual case insensitive")


def test_factual_contained():
    """Answer should be found within verbose output."""
    assert score_factual("The chemical symbol for gold is Au.", "Au") == 1.0
    assert score_factual("I believe it's Shakespeare who wrote it.", "Shakespeare") == 1.0
    print("  ✅ PASS: factual contained in text")


def test_factual_wrong():
    assert score_factual("Ag", "Au") == 0.0
    assert score_factual("I don't know", "Au") == 0.0
    print("  ✅ PASS: factual wrong")


# ─── Heuristic reasoning scoring ─────────────────────────────────────────────

def test_heuristic_reasoning_empty():
    """Too short responses score 0."""
    assert _heuristic_reasoning_score("ok", "Must mention complexity") == 0.0
    print("  ✅ PASS: heuristic reasoning empty")


def test_heuristic_reasoning_keywords():
    """Should score based on rubric keyword coverage."""
    rubric = "Must mention time complexity, O(n²), nested comparisons"
    good_output = "Bubble sort has O(n²) time complexity due to nested comparisons making it slow."
    bad_output = "Bubble sort is a sorting algorithm that works with elements."

    good_score = _heuristic_reasoning_score(good_output, rubric)
    bad_score = _heuristic_reasoning_score(bad_output, rubric)
    assert good_score > bad_score, f"Good ({good_score}) should beat bad ({bad_score})"
    print("  ✅ PASS: heuristic reasoning keyword scoring")


# ─── score_task dispatcher ────────────────────────────────────────────────────

def test_score_task_math():
    task = {"type": "math", "answer": "42"}
    assert score_task(task, "42") == 1.0
    assert score_task(task, "wrong") == 0.0
    print("  ✅ PASS: score_task math dispatch")


def test_score_task_factual():
    task = {"type": "factual", "answer": "Au"}
    assert score_task(task, "Au") == 1.0
    assert score_task(task, "Ag") == 0.0
    print("  ✅ PASS: score_task factual dispatch")


def test_score_task_unknown_type():
    task = {"type": "unknown_type"}
    assert score_task(task, "anything") == 0.0
    print("  ✅ PASS: score_task unknown type")


if __name__ == "__main__":
    print("\n=== Obolus Evaluator Tests ===\n")
    test_math_exact()
    test_math_with_text()
    test_math_wrong()
    test_math_no_number()
    test_math_float_comparison()
    test_math_negative()
    test_factual_exact()
    test_factual_case_insensitive()
    test_factual_contained()
    test_factual_wrong()
    test_heuristic_reasoning_empty()
    test_heuristic_reasoning_keywords()
    test_score_task_math()
    test_score_task_factual()
    test_score_task_unknown_type()
    print("\n=== All evaluator tests passed! ===\n")
