#!/usr/bin/env python3
"""
Test Phase 3 Anti-Hallucination Validation

WHY: Verify symbolic execution and formal spec matching work correctly
RESPONSIBILITY: Test all Phase 3 validation features
PATTERNS: Guard clauses, test categorization

Tests:
1. Symbolic execution validator
2. Formal specification matcher
3. Advanced validation reviewer integration
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from artemis_logger import get_logger
from validation import (
    SymbolicExecutionValidator,
    SymbolicExecutionResult,
    VerificationStatus,
    FormalSpecificationMatcher,
    FormalMatchingResult,
    SpecificationType,
)
from stages.code_review_stage.advanced_validation_reviewer import AdvancedValidationReviewer


def test_symbolic_execution_validator():
    """
    Test symbolic execution validator.

    WHY: Verify symbolic execution works correctly
    RESPONSIBILITY: Test path analysis, error detection
    """
    print("\n=== Test 1: Symbolic Execution Validator ===")

    logger = get_logger("test")
    validator = SymbolicExecutionValidator(logger=logger)

    # Test code with multiple paths
    code = """
def calculate_discount(price: float, is_member: bool) -> float:
    '''Calculate discount based on membership.'''
    # Guard: Invalid price
    if price <= 0:
        return 0.0

    # Calculate discount
    if is_member:
        discount = price * 0.2
    else:
        discount = price * 0.1

    return price - discount
"""

    # Run symbolic execution
    result = validator.validate_function(code, "calculate_discount")

    # Verify result structure
    assert isinstance(result, SymbolicExecutionResult), "Should return SymbolicExecutionResult"
    assert result.function_name == "calculate_discount", "Should identify correct function"
    assert result.paths_explored > 0, "Should explore at least one path"
    assert result.verification_time_ms >= 0, "Should have timing info"

    print(f"  ✓ Function: {result.function_name}")
    print(f"  ✓ Status: {result.status.value}")
    print(f"  ✓ Paths explored: {result.paths_explored}")
    print(f"  ✓ Reachable paths: {result.reachable_paths}")
    print(f"  ✓ Verification time: {result.verification_time_ms:.2f}ms")

    return True


def test_symbolic_execution_error_detection():
    """
    Test symbolic execution error detection.

    WHY: Verify error detection works
    RESPONSIBILITY: Test division by zero, array bounds
    """
    print("\n=== Test 2: Symbolic Execution Error Detection ===")

    logger = get_logger("test")
    validator = SymbolicExecutionValidator(logger=logger)

    # Test code with potential errors
    code = """
def risky_calculation(x: int, values: list) -> float:
    '''Potentially risky calculation.'''
    result = 100 / x  # Potential division by zero
    value = values[0]  # Potential index out of bounds
    return result + value
"""

    # Run symbolic execution
    result = validator.validate_function(code, "risky_calculation")

    # Verify error detection
    assert len(result.potential_errors) > 0, "Should detect potential errors"

    print(f"  ✓ Detected {len(result.potential_errors)} potential error(s)")
    for error in result.potential_errors[:3]:
        print(f"    - {error}")

    return True


def test_formal_specification_matcher():
    """
    Test formal specification matcher.

    WHY: Verify spec extraction and matching works
    RESPONSIBILITY: Test docstring, type hint, requirement parsing
    """
    print("\n=== Test 3: Formal Specification Matcher ===")

    logger = get_logger("test")
    matcher = FormalSpecificationMatcher(logger=logger)

    # Test code with formal specifications
    code = """
def calculate_square(n: int) -> int:
    '''
    Calculate the square of a number.

    Requires: n is an integer
    Ensures: result >= 0
    Ensures: result is non-negative
    '''
    return n * n
"""

    # Match specifications
    result = matcher.match_specifications(code, function_name="calculate_square")

    # Verify result structure
    assert isinstance(result, FormalMatchingResult), "Should return FormalMatchingResult"
    assert result.function_name == "calculate_square", "Should identify correct function"
    assert result.specifications_found > 0, "Should find specifications"

    print(f"  ✓ Function: {result.function_name}")
    print(f"  ✓ Specifications found: {result.specifications_found}")
    print(f"  ✓ Verified: {result.specifications_verified}")
    print(f"  ✓ Failed: {result.specifications_failed}")
    print(f"  ✓ Overall satisfied: {result.overall_satisfied}")

    # Verify specification types
    spec_types = {spec.spec_type for spec in result.specifications}
    print(f"  ✓ Specification types found: {', '.join(t.value for t in spec_types)}")

    return True


def test_formal_spec_type_hints():
    """
    Test formal spec extraction from type hints.

    WHY: Verify type hint extraction works
    RESPONSIBILITY: Test parameter and return type extraction
    """
    print("\n=== Test 4: Formal Spec Type Hint Extraction ===")

    logger = get_logger("test")
    matcher = FormalSpecificationMatcher(logger=logger)

    # Test code with type hints
    code = """
def add_numbers(x: int, y: int) -> int:
    '''Add two numbers.'''
    return x + y
"""

    # Match specifications
    result = matcher.match_specifications(code, function_name="add_numbers")

    # Verify type constraints extracted
    type_specs = [s for s in result.specifications if s.spec_type == SpecificationType.TYPE_CONSTRAINT]
    preconditions = [s for s in result.specifications if s.spec_type == SpecificationType.PRECONDITION]

    assert len(type_specs) > 0 or len(preconditions) > 0, "Should extract type specifications"

    print(f"  ✓ Type constraints: {len(type_specs)}")
    print(f"  ✓ Preconditions (from params): {len(preconditions)}")

    return True


def test_formal_spec_requirements_doc():
    """
    Test formal spec extraction from requirements.

    WHY: Verify requirements document parsing works
    RESPONSIBILITY: Test requirement text extraction
    """
    print("\n=== Test 5: Formal Spec Requirements Extraction ===")

    logger = get_logger("test")
    matcher = FormalSpecificationMatcher(logger=logger)

    # Test code
    code = """
def validate_password(password: str) -> bool:
    '''Validate password strength.'''
    return len(password) >= 8
"""

    # Requirements document
    requirements = """
    Password Validation Requirements:

    validate_password: Must check password is at least 8 characters.
    Must return True for valid passwords, False otherwise.
    """

    # Match specifications
    result = matcher.match_specifications(
        code,
        requirements=requirements,
        function_name="validate_password"
    )

    # Verify requirements extracted
    req_specs = [s for s in result.specifications if s.source == "requirements"]

    print(f"  ✓ Specifications from requirements: {len(req_specs)}")
    for spec in req_specs[:2]:
        print(f"    - {spec.description}")

    return True


def test_advanced_validation_reviewer_integration():
    """
    Test advanced validation reviewer with Phase 3 features.

    WHY: Verify integration works end-to-end
    RESPONSIBILITY: Test all validation techniques together
    """
    print("\n=== Test 6: Advanced Validation Reviewer Integration ===")

    logger = get_logger("test")
    reviewer = AdvancedValidationReviewer(
        logger=logger,
        enable_static_analysis=False,  # Focus on Phase 3
        enable_property_tests=False,
        enable_symbolic_execution=True,
        enable_formal_specs=True
    )

    # Test code with specifications
    code = """
def calculate_area(width: float, height: float) -> float:
    '''
    Calculate rectangular area.

    Requires: width > 0
    Requires: height > 0
    Ensures: result > 0
    '''
    # Guard: Invalid dimensions
    if width <= 0 or height <= 0:
        return 0.0

    return width * height
"""

    # Run review
    result = reviewer.review_code(code, developer_name="test-dev")

    # Verify result structure
    assert "symbolic_execution" in result, "Should have symbolic execution results"
    assert "formal_specs" in result, "Should have formal specs results"

    # Verify symbolic execution ran
    symbolic_result = result["symbolic_execution"]
    assert symbolic_result is not None, "Symbolic execution should run"
    assert symbolic_result["enabled"], "Symbolic execution should be enabled"
    assert symbolic_result["function_name"] == "calculate_area", "Should analyze correct function"

    # Verify formal specs ran
    formal_result = result["formal_specs"]
    assert formal_result is not None, "Formal specs should run"
    assert formal_result["enabled"], "Formal specs should be enabled"
    assert formal_result["specifications_found"] > 0, "Should find specifications"

    print(f"  ✓ Symbolic execution: {symbolic_result['summary']}")
    print(f"  ✓ Formal specs: {formal_result['summary']}")
    print(f"  ✓ Overall passed: {result['overall_passed']}")

    return True


def test_advanced_validation_report_formatting():
    """
    Test report formatting for Phase 3 features.

    WHY: Verify markdown report generation works
    RESPONSIBILITY: Test report formatting
    """
    print("\n=== Test 7: Report Formatting ===")

    logger = get_logger("test")
    reviewer = AdvancedValidationReviewer(
        logger=logger,
        enable_static_analysis=False,
        enable_property_tests=False,
        enable_symbolic_execution=True,
        enable_formal_specs=True
    )

    # Test code
    code = """
def safe_divide(a: float, b: float) -> float:
    '''
    Safely divide two numbers.

    Requires: b != 0
    Ensures: result is valid
    '''
    if b == 0:
        return 0.0
    return a / b
"""

    # Run review
    result = reviewer.review_code(code, developer_name="test-dev")

    # Format report
    report = reviewer.format_report(result)

    # Verify report structure
    assert "## Advanced Validation Report" in report, "Should have report header"
    assert "### Symbolic Execution" in report, "Should have symbolic execution section"
    assert "### Formal Specifications" in report, "Should have formal specs section"
    assert "### Overall Assessment" in report, "Should have overall assessment"

    print("  ✓ Report formatted successfully")
    print(f"  ✓ Report length: {len(report)} characters")

    # Print sample of report
    lines = report.split('\n')
    print("\n  Sample report (first 15 lines):")
    for line in lines[:15]:
        print(f"    {line}")

    return True


def test_code_standards_compliance():
    """
    Test code standards compliance for Phase 3 code.

    WHY: Verify all new code follows standards
    RESPONSIBILITY: Check guard clauses, no nested ifs
    """
    print("\n=== Test 8: Code Standards Compliance ===")

    from coding_standards.validation import CodeStandardsValidator

    validator = CodeStandardsValidator()
    result = validator.validate_code_standards(
        code_dir='validation',
        severity_threshold='warning'
    )

    print(f"  ✓ Files scanned: {result.files_scanned}")
    print(f"  ✓ Violations: {result.violation_count}")
    print(f"  ✓ Valid: {result.is_valid}")

    # Should have no violations
    assert result.is_valid, "All code should follow standards"

    return True


def run_all_tests():
    """
    Run all Phase 3 validation tests.

    WHY: Execute complete test suite
    RESPONSIBILITY: Run and report test results
    """
    print("=" * 70)
    print("Phase 3 Anti-Hallucination Validation Tests")
    print("=" * 70)

    tests = [
        ("Symbolic Execution Validator", test_symbolic_execution_validator),
        ("Symbolic Execution Error Detection", test_symbolic_execution_error_detection),
        ("Formal Specification Matcher", test_formal_specification_matcher),
        ("Formal Spec Type Hints", test_formal_spec_type_hints),
        ("Formal Spec Requirements", test_formal_spec_requirements_doc),
        ("Advanced Validation Integration", test_advanced_validation_reviewer_integration),
        ("Report Formatting", test_advanced_validation_report_formatting),
        ("Code Standards Compliance", test_code_standards_compliance),
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

    # Guard: All passed
    if failed == 0:
        print("\n✅ ALL TESTS PASSED")
        print("\nPhase 3 anti-hallucination features are ready:")
        print("  ✓ Symbolic execution validator works")
        print("  ✓ Formal specification matcher works")
        print("  ✓ Advanced validation integration works")
        print("  ✓ Report formatting works")
        print("  ✓ Code follows guard clause pattern")
        return 0

    # Has failures
    print(f"\n❌ {failed} TEST(S) FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
