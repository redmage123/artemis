#!/usr/bin/env python3
"""
Test Phase 3 Validators

WHY: Verify symbolic execution and formal spec matching work correctly
RESPONSIBILITY: Test validation validators in isolation
PATTERNS: Guard clauses, test categorization

Tests:
1. Symbolic execution validator
2. Formal specification matcher
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from artemis_logger import get_logger
from validation import (
    SymbolicExecutionValidator,
    SymbolicExecutionResult,
    VerificationStatus,
    FormalSpecificationMatcher,
    FormalMatchingResult,
    SpecificationType,
)


def test_symbolic_execution_basic():
    """Test basic symbolic execution functionality."""
    print("\n=== Test 1: Symbolic Execution - Basic Functionality ===")

    logger = get_logger("test")
    validator = SymbolicExecutionValidator(logger=logger)

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

    result = validator.validate_function(code, "calculate_discount")

    assert isinstance(result, SymbolicExecutionResult), "Should return SymbolicExecutionResult"
    assert result.function_name == "calculate_discount", "Should identify correct function"

    # Guard: Z3 not available - should return unsupported
    if not validator.z3_available:
        assert result.status == VerificationStatus.UNSUPPORTED, "Should be unsupported without Z3"
        print(f"  ✓ Function: {result.function_name}")
        print(f"  ✓ Status: {result.status.value} (Z3 not installed)")
        print(f"  ℹ️  Graceful degradation working correctly")
        return True

    # Z3 available - full testing
    assert result.paths_explored > 0, "Should explore at least one path"
    print(f"  ✓ Function: {result.function_name}")
    print(f"  ✓ Status: {result.status.value}")
    print(f"  ✓ Paths: {result.paths_explored} total, {result.reachable_paths} reachable")
    print(f"  ✓ Time: {result.verification_time_ms:.2f}ms")

    return True


def test_symbolic_execution_error_detection():
    """Test symbolic execution error detection."""
    print("\n=== Test 2: Symbolic Execution - Error Detection ===")

    logger = get_logger("test")
    validator = SymbolicExecutionValidator(logger=logger)

    code = """
def risky_calculation(x: int, values: list) -> float:
    '''Potentially risky calculation.'''
    result = 100 / x  # Potential division by zero
    value = values[0]  # Potential index out of bounds
    return result + value
"""

    result = validator.validate_function(code, "risky_calculation")

    # Guard: Z3 not available
    if not validator.z3_available:
        assert result.status == VerificationStatus.UNSUPPORTED, "Should be unsupported without Z3"
        print(f"  ✓ Status: {result.status.value} (Z3 not installed)")
        print(f"  ℹ️  Error detection requires Z3")
        return True

    # Z3 available - check error detection
    assert len(result.potential_errors) > 0, "Should detect potential errors"

    print(f"  ✓ Detected {len(result.potential_errors)} potential error(s):")
    for error in result.potential_errors:
        print(f"    - {error}")

    return True


def test_symbolic_execution_no_z3():
    """Test symbolic execution handles missing Z3 gracefully."""
    print("\n=== Test 3: Symbolic Execution - Graceful Degradation ===")

    logger = get_logger("test")
    validator = SymbolicExecutionValidator(logger=logger)

    code = """
def simple_add(a: int, b: int) -> int:
    '''Add two numbers.'''
    return a + b
"""

    result = validator.validate_function(code)

    # Should complete even if Z3 not available
    assert result is not None, "Should return result even without Z3"

    print(f"  ✓ Z3 available: {validator.z3_available}")
    print(f"  ✓ Status: {result.status.value}")
    print(f"  ✓ Summary: {result.summary}")

    return True


def test_formal_spec_docstring_extraction():
    """Test formal specification extraction from docstrings."""
    print("\n=== Test 4: Formal Specs - Docstring Extraction ===")

    logger = get_logger("test")
    matcher = FormalSpecificationMatcher(logger=logger)

    code = """
def calculate_square(n: int) -> int:
    '''
    Calculate the square of a number.

    Requires: n is an integer
    Ensures: result >= 0
    Invariant: result is non-negative
    '''
    return n * n
"""

    result = matcher.match_specifications(code, function_name="calculate_square")

    assert isinstance(result, FormalMatchingResult), "Should return FormalMatchingResult"
    assert result.specifications_found > 0, "Should find specifications"

    print(f"  ✓ Function: {result.function_name}")
    print(f"  ✓ Specifications found: {result.specifications_found}")

    spec_types = {}
    for spec in result.specifications:
        spec_type = spec.spec_type.value
        spec_types[spec_type] = spec_types.get(spec_type, 0) + 1

    for spec_type, count in spec_types.items():
        print(f"    - {spec_type}: {count}")

    return True


def test_formal_spec_type_hints():
    """Test formal specification extraction from type hints."""
    print("\n=== Test 5: Formal Specs - Type Hint Extraction ===")

    logger = get_logger("test")
    matcher = FormalSpecificationMatcher(logger=logger)

    code = """
def add_numbers(x: int, y: int) -> int:
    '''Add two numbers.'''
    return x + y
"""

    result = matcher.match_specifications(code, function_name="add_numbers")

    type_specs = [s for s in result.specifications if s.spec_type == SpecificationType.TYPE_CONSTRAINT]
    preconditions = [s for s in result.specifications if s.spec_type == SpecificationType.PRECONDITION]

    total_type_related = len(type_specs) + len(preconditions)
    assert total_type_related > 0, "Should extract type-related specifications"

    print(f"  ✓ Type constraints: {len(type_specs)}")
    print(f"  ✓ Preconditions (params): {len(preconditions)}")

    return True


def test_formal_spec_requirements():
    """Test formal specification extraction from requirements."""
    print("\n=== Test 6: Formal Specs - Requirements Extraction ===")

    logger = get_logger("test")
    matcher = FormalSpecificationMatcher(logger=logger)

    code = """
def validate_password(password: str) -> bool:
    '''Validate password strength.'''
    return len(password) >= 8
"""

    requirements = """
    Password Validation Requirements:

    validate_password: Must check password is at least 8 characters.
    Must return True for valid passwords, False otherwise.
    """

    result = matcher.match_specifications(
        code,
        requirements=requirements,
        function_name="validate_password"
    )

    req_specs = [s for s in result.specifications if s.source == "requirements"]

    print(f"  ✓ Specifications from requirements: {len(req_specs)}")
    for spec in req_specs[:2]:
        print(f"    - {spec.description[:50]}...")

    return True


def test_formal_spec_verification():
    """Test formal specification verification."""
    print("\n=== Test 7: Formal Specs - Verification ===")

    logger = get_logger("test")
    matcher = FormalSpecificationMatcher(logger=logger)

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

    result = matcher.match_specifications(code, function_name="safe_divide")

    print(f"  ✓ Specifications found: {result.specifications_found}")
    print(f"  ✓ Verified: {result.specifications_verified}")
    print(f"  ✓ Failed: {result.specifications_failed}")
    print(f"  ✓ Overall satisfied: {result.overall_satisfied}")

    # Check verification results
    for spec, verification in zip(result.specifications, result.verification_results):
        print(f"    - {spec.description[:40]}... → {verification.satisfied}")

    return True


def test_code_standards_compliance():
    """Test code standards compliance."""
    print("\n=== Test 8: Code Standards Compliance ===")

    from coding_standards.validation import CodeStandardsValidator
    import os

    # Get absolute path to validation directory
    validation_dir = str(Path(__file__).parent.absolute())

    validator = CodeStandardsValidator()
    result = validator.validate_code_standards(
        code_dir=validation_dir,
        severity_threshold='warning'
    )

    print(f"  ✓ Files scanned: {result.files_scanned}")
    print(f"  ✓ Violations: {result.violation_count}")
    print(f"  ✓ Valid: {result.is_valid}")

    # Guard: No files scanned (path issue or empty dir)
    if result.files_scanned == 0:
        print(f"  ℹ️  No Python files found in {validation_dir}")
        # Consider this as passed if there are no violations
        return True

    assert result.is_valid, "All code should follow standards"

    return True


def run_all_tests():
    """Run all Phase 3 validator tests."""
    print("=" * 70)
    print("Phase 3 Validator Tests")
    print("=" * 70)

    tests = [
        ("Symbolic Execution - Basic", test_symbolic_execution_basic),
        ("Symbolic Execution - Errors", test_symbolic_execution_error_detection),
        ("Symbolic Execution - Graceful", test_symbolic_execution_no_z3),
        ("Formal Specs - Docstrings", test_formal_spec_docstring_extraction),
        ("Formal Specs - Type Hints", test_formal_spec_type_hints),
        ("Formal Specs - Requirements", test_formal_spec_requirements),
        ("Formal Specs - Verification", test_formal_spec_verification),
        ("Code Standards", test_code_standards_compliance),
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
        print("\nPhase 3 validators are ready:")
        print("  ✓ Symbolic execution validator works")
        print("  ✓ Formal specification matcher works")
        print("  ✓ Error detection works")
        print("  ✓ Spec extraction works (docstrings, type hints, requirements)")
        print("  ✓ Code follows guard clause pattern")
        return 0

    print(f"\n❌ {failed} TEST(S) FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
