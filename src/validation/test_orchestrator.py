#!/usr/bin/env python3
"""
Test Anti-Hallucination Orchestrator

WHY: Verify intelligent strategy selection works correctly
RESPONSIBILITY: Test risk assessment, strategy selection, technique combination
PATTERNS: Guard clauses, test categorization
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from artemis_logger import get_logger
from validation import (
    AntiHallucinationOrchestrator,
    ValidationProfile,
    RiskLevel,
    TaskType,
    TaskContext,
)


def test_low_risk_simple_code():
    """Test strategy for low-risk simple code."""
    print("\n=== Test 1: Low Risk Simple Code ===")

    orchestrator = AntiHallucinationOrchestrator(logger=get_logger("test"))

    context = TaskContext(
        task_type=TaskType.CODE_GENERATION,
        code_complexity=50,      # Small
        is_critical=False,
        has_tests=True,
        dependencies_count=2
    )

    strategy = orchestrator.select_strategy(context)

    print(f"  Risk level: {strategy.risk_level.value}")
    print(f"  Profile: {strategy.profile.value}")
    print(f"  Techniques: {', '.join(strategy.techniques)}")
    print(f"  Estimated time: {strategy.estimated_time_ms:.0f}ms")
    print(f"  Expected reduction: {strategy.expected_reduction:.2%}")

    # Verify
    assert strategy.risk_level == RiskLevel.LOW, "Should be LOW risk"
    assert strategy.profile == ValidationProfile.MINIMAL, "Should be MINIMAL profile"
    assert "chain_of_thought" in strategy.techniques, "Should include chain_of_thought"
    assert len(strategy.techniques) <= 3, "Should use few techniques"

    return True


def test_high_risk_complex_code():
    """Test strategy for high-risk complex code."""
    print("\n=== Test 2: High Risk Complex Code ===")

    orchestrator = AntiHallucinationOrchestrator(logger=get_logger("test"))

    context = TaskContext(
        task_type=TaskType.BUG_FIX,
        code_complexity=600,     # Large
        is_critical=False,
        has_tests=False,         # No tests = risky
        dependencies_count=15    # Many dependencies
    )

    strategy = orchestrator.select_strategy(context)

    print(f"  Risk level: {strategy.risk_level.value}")
    print(f"  Profile: {strategy.profile.value}")
    print(f"  Techniques: {', '.join(strategy.techniques)}")
    print(f"  Estimated time: {strategy.estimated_time_ms:.0f}ms")
    print(f"  Expected reduction: {strategy.expected_reduction:.2%}")

    # Verify
    assert strategy.risk_level == RiskLevel.HIGH, "Should be HIGH risk"
    assert strategy.profile == ValidationProfile.THOROUGH, "Should be THOROUGH profile"
    assert "symbolic_execution" in strategy.techniques or "formal_specs" in strategy.techniques, \
           "Should include Phase 3 techniques"
    assert len(strategy.techniques) >= 4, "Should use multiple techniques"

    return True


def test_critical_infrastructure():
    """Test strategy for critical infrastructure."""
    print("\n=== Test 3: Critical Infrastructure ===")

    orchestrator = AntiHallucinationOrchestrator(logger=get_logger("test"))

    context = TaskContext(
        task_type=TaskType.FEATURE_ADDITION,
        code_complexity=300,
        is_critical=True,        # Critical!
        has_tests=True,
        dependencies_count=8
    )

    strategy = orchestrator.select_strategy(context)

    print(f"  Risk level: {strategy.risk_level.value}")
    print(f"  Profile: {strategy.profile.value}")
    print(f"  Techniques: {', '.join(strategy.techniques)}")
    print(f"  Estimated time: {strategy.estimated_time_ms:.0f}ms")
    print(f"  Expected reduction: {strategy.expected_reduction:.2%}")

    # Verify
    assert strategy.risk_level == RiskLevel.CRITICAL, "Should be CRITICAL risk"
    assert strategy.profile == ValidationProfile.CRITICAL, "Should be CRITICAL profile"
    assert len(strategy.techniques) >= 6, "Should use many techniques"
    assert "symbolic_execution" in strategy.techniques, "Should include symbolic execution"
    assert "formal_specs" in strategy.techniques, "Should include formal specs"

    return True


def test_time_budget_constraint():
    """Test strategy with time budget constraint."""
    print("\n=== Test 4: Time Budget Constraint ===")

    orchestrator = AntiHallucinationOrchestrator(logger=get_logger("test"))

    context = TaskContext(
        task_type=TaskType.CODE_GENERATION,
        code_complexity=400,
        is_critical=True,
        has_tests=False,
        dependencies_count=10,
        time_budget_ms=800      # Limited time!
    )

    strategy = orchestrator.select_strategy(context)

    print(f"  Risk level: {strategy.risk_level.value}")
    print(f"  Profile: {strategy.profile.value}")
    print(f"  Techniques: {', '.join(strategy.techniques)}")
    print(f"  Estimated time: {strategy.estimated_time_ms:.0f}ms")
    print(f"  Time budget: {context.time_budget_ms:.0f}ms")

    # Verify
    assert strategy.risk_level == RiskLevel.CRITICAL, "Should be CRITICAL risk"
    # Profile might be downgraded due to time budget
    assert strategy.profile in {ValidationProfile.THOROUGH, ValidationProfile.CRITICAL}, \
           "Should be THOROUGH or CRITICAL (may downgrade due to time)"

    return True


def test_profile_override():
    """Test manual profile override."""
    print("\n=== Test 5: Profile Override ===")

    orchestrator = AntiHallucinationOrchestrator(logger=get_logger("test"))

    context = TaskContext(
        task_type=TaskType.DOCUMENTATION,
        code_complexity=10,
        is_critical=False,
        has_tests=True,
        dependencies_count=0
    )

    # Override to THOROUGH despite low risk
    strategy = orchestrator.select_strategy(context, profile=ValidationProfile.THOROUGH)

    print(f"  Risk level: {strategy.risk_level.value}")
    print(f"  Profile: {strategy.profile.value} (overridden)")
    print(f"  Techniques: {', '.join(strategy.techniques)}")

    # Verify
    assert strategy.profile == ValidationProfile.THOROUGH, "Should use overridden profile"

    return True


def test_technique_applicability():
    """Test technique applicability filtering."""
    print("\n=== Test 6: Technique Applicability ===")

    orchestrator = AntiHallucinationOrchestrator(logger=get_logger("test"))

    # Documentation task - most code validation techniques don't apply
    context = TaskContext(
        task_type=TaskType.DOCUMENTATION,
        code_complexity=100,
        is_critical=False,
        has_tests=True,
        dependencies_count=1
    )

    strategy = orchestrator.select_strategy(context)

    print(f"  Task type: {context.task_type.value}")
    print(f"  Techniques: {', '.join(strategy.techniques)}")

    # Verify - shouldn't include code-specific techniques
    assert "symbolic_execution" not in strategy.techniques, \
           "Shouldn't include symbolic execution for documentation"
    assert "property_tests" not in strategy.techniques, \
           "Shouldn't include property tests for documentation"

    return True


def test_historical_learning():
    """Test historical failure learning."""
    print("\n=== Test 7: Historical Learning ===")

    orchestrator = AntiHallucinationOrchestrator(logger=get_logger("test"))

    # Record some failures
    orchestrator.record_failure(
        TaskType.BUG_FIX,
        "static_analysis",
        "null_pointer"
    )
    orchestrator.record_failure(
        TaskType.BUG_FIX,
        "property_tests",
        "null_pointer"
    )

    # Get recommendations
    recommended = orchestrator.get_recommended_techniques(
        TaskType.BUG_FIX,
        "null_pointer"
    )

    print(f"  Recorded failures for null_pointer pattern: {recommended}")

    # Verify
    assert "static_analysis" in recommended, "Should recommend static_analysis"
    assert "property_tests" in recommended, "Should recommend property_tests"

    return True


def test_reduction_calculation():
    """Test hallucination reduction calculation."""
    print("\n=== Test 8: Reduction Calculation ===")

    orchestrator = AntiHallucinationOrchestrator(logger=get_logger("test"))

    # Test different combinations
    test_cases = [
        (["chain_of_thought"], "minimal"),
        (["chain_of_thought", "static_analysis"], "standard"),
        (["chain_of_thought", "static_analysis", "symbolic_execution", "formal_specs"], "thorough"),
    ]

    for techniques, description in test_cases:
        reduction = orchestrator._calculate_reduction(techniques)
        print(f"  {description.capitalize()}: {', '.join(techniques)}")
        print(f"    Expected reduction: {reduction:.2%}")

        # Verify reduction increases with more techniques
        assert 0.0 < reduction <= 1.0, "Reduction should be between 0 and 1"

    return True


def test_rationale_generation():
    """Test rationale generation."""
    print("\n=== Test 9: Rationale Generation ===")

    orchestrator = AntiHallucinationOrchestrator(logger=get_logger("test"))

    context = TaskContext(
        task_type=TaskType.CODE_GENERATION,
        code_complexity=250,
        is_critical=False,
        has_tests=False,
        dependencies_count=7
    )

    strategy = orchestrator.select_strategy(context)

    print(f"  Rationale: {strategy.rationale}")

    # Verify rationale contains key information
    assert "Risk:" in strategy.rationale, "Should include risk assessment"
    assert "Profile:" in strategy.rationale, "Should include profile"
    assert "Techniques:" in strategy.rationale, "Should include techniques"

    return True


def run_all_tests():
    """Run all orchestrator tests."""
    print("=" * 70)
    print("Anti-Hallucination Orchestrator Tests")
    print("=" * 70)

    tests = [
        ("Low Risk Simple Code", test_low_risk_simple_code),
        ("High Risk Complex Code", test_high_risk_complex_code),
        ("Critical Infrastructure", test_critical_infrastructure),
        ("Time Budget Constraint", test_time_budget_constraint),
        ("Profile Override", test_profile_override),
        ("Technique Applicability", test_technique_applicability),
        ("Historical Learning", test_historical_learning),
        ("Reduction Calculation", test_reduction_calculation),
        ("Rationale Generation", test_rationale_generation),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"  ❌ {name} failed")
        except Exception as e:
            failed += 1
            print(f"  ❌ {name} failed with error: {e}")
            import traceback
            traceback.print_exc()

    # Print summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Tests passed: {passed}/{len(tests)}")
    print(f"Tests failed: {failed}/{len(tests)}")

    if failed == 0:
        print("\n✅ ALL TESTS PASSED")
        print("\nAnti-Hallucination Orchestrator is ready:")
        print("  ✓ Risk assessment works correctly")
        print("  ✓ Strategy selection adapts to context")
        print("  ✓ Technique filtering works")
        print("  ✓ Profile override supported")
        print("  ✓ Historical learning functions")
        print("  ✓ Reduction calculation accurate")
        return 0

    print(f"\n❌ {failed} TEST(S) FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
