"""
Tests for Obolus Evolutionary Fitness Scorer.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.benchmark.fitness_scorer import (
    TrialResult, ScoringConfig, FitnessResult,
    compute_quality, compute_efficiency, compute_variance_penalty,
    compute_z_score, approve, evaluate_mutation,
    InvalidMeasurementError,
)


def test_example_from_spec():
    """Test the exact example from the Final Idea document."""
    config = ScoringConfig(
        baseline_time_ms=100,
        baseline_energy_joules=50
    )

    trials = [
        TrialResult(True, 90, 0.95),
        TrialResult(True, 110, 0.90),
        TrialResult(True, 100, 0.92),
    ]

    result = evaluate_mutation(
        trials=trials,
        energy_joules=42,
        config=config
    )

    print(f"  z_score:  {result.z_score}")
    print(f"  quality:  {result.quality}")
    print(f"  efficiency: {result.efficiency}")
    print(f"  variance: {result.variance_penalty}")
    print(f"  approved: {result.approved}")
    print(f"  reason:   {result.reason}")

    assert result.quality > 0, "Quality should be positive"
    assert result.efficiency > 1.0, "Efficiency should be > 1 (better than baseline)"
    assert result.z_score > 0, "z-score should be positive"
    assert result.approved, f"Should be approved, got reason: {result.reason}"
    print("  ✅ PASS: Example from spec")


def test_zero_energy():
    """Zero energy should return invalid measurement result."""
    config = ScoringConfig(baseline_time_ms=100, baseline_energy_joules=50)
    trials = [TrialResult(True, 100, 0.9)]

    result = evaluate_mutation(trials=trials, energy_joules=0, config=config)

    assert not result.approved
    assert result.reason == "invalid_energy_measurement"
    assert result.efficiency == 0.0
    print("  ✅ PASS: Zero energy")


def test_negative_energy():
    """Negative energy should return invalid measurement result."""
    config = ScoringConfig(baseline_time_ms=100, baseline_energy_joules=50)
    trials = [TrialResult(True, 100, 0.9)]

    result = evaluate_mutation(trials=trials, energy_joules=-5, config=config)

    assert not result.approved
    assert result.reason == "invalid_energy_measurement"
    print("  ✅ PASS: Negative energy")


def test_no_trials():
    """No trials should result in zero quality and rejection."""
    config = ScoringConfig(baseline_time_ms=100, baseline_energy_joules=50)

    result = evaluate_mutation(trials=[], energy_joules=42, config=config)

    assert result.quality == 0.0
    assert not result.approved
    print("  ✅ PASS: No trials")


def test_all_failed_trials():
    """All failed trials should result in zero quality."""
    config = ScoringConfig(baseline_time_ms=100, baseline_energy_joules=50)
    trials = [
        TrialResult(False, 200, 0.1),
        TrialResult(False, 300, 0.05),
    ]

    result = evaluate_mutation(trials=trials, energy_joules=42, config=config)

    assert result.quality == 0.0
    assert not result.approved
    print("  ✅ PASS: All failed trials")


def test_single_trial_variance_fallback():
    """With < min_trials_for_variance, should use variance_fallback."""
    config = ScoringConfig(
        baseline_time_ms=100,
        baseline_energy_joules=50,
        min_trials_for_variance=2,
        variance_fallback=0.3
    )
    trials = [TrialResult(True, 80, 0.95)]

    result = evaluate_mutation(trials=trials, energy_joules=42, config=config)

    assert result.variance_penalty == 0.3, f"Expected 0.3, got {result.variance_penalty}"
    print("  ✅ PASS: Single trial variance fallback")


def test_low_quality_rejection():
    """Trials with low scores should be rejected for low quality."""
    config = ScoringConfig(
        baseline_time_ms=100,
        baseline_energy_joules=50,
        min_quality=0.75
    )
    trials = [
        TrialResult(True, 100, 0.2),
        TrialResult(False, 200, 0.1),
    ]

    result = evaluate_mutation(trials=trials, energy_joules=42, config=config)

    assert not result.approved
    assert result.reason and "low_quality" in result.reason
    print("  ✅ PASS: Low quality rejection")


def test_inefficient_rejection():
    """Using more energy than baseline should be rejected."""
    config = ScoringConfig(
        baseline_time_ms=100,
        baseline_energy_joules=50,
        min_efficiency=1.01
    )
    trials = [
        TrialResult(True, 80, 0.95),
        TrialResult(True, 90, 0.92),
        TrialResult(True, 85, 0.93),
    ]

    # 100J >> 50J baseline → efficiency < 1.0
    result = evaluate_mutation(trials=trials, energy_joules=100, config=config)

    assert result.efficiency < 1.0
    assert not result.approved
    assert result.reason and "no_efficiency_gain" in result.reason
    print("  ✅ PASS: Inefficient rejection")


def test_compute_z_score():
    """Test the z-score formula: (Q × E) × (1 − V)."""
    z = compute_z_score(Q=0.9, E=1.2, V=0.1)
    expected = round((0.9 * 1.2) * (1 - 0.1), 4)
    assert z == expected, f"Expected {expected}, got {z}"
    print("  ✅ PASS: z-score formula")


if __name__ == "__main__":
    print("\n=== Obolus Fitness Scorer Tests ===\n")

    test_example_from_spec()
    test_zero_energy()
    test_negative_energy()
    test_no_trials()
    test_all_failed_trials()
    test_single_trial_variance_fallback()
    test_low_quality_rejection()
    test_inefficient_rejection()
    test_compute_z_score()

    print("\n=== All tests passed! ===\n")
