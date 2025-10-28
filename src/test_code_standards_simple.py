#!/usr/bin/env python3
"""
Simple Code Standards Integration Test

WHY: Verify code standards validator integrates correctly (isolated test)
RESPONSIBILITY: Test without full pipeline imports
PATTERNS: Unit testing
"""

import tempfile
import sys
from pathlib import Path

# Direct imports to avoid circular dependencies
sys.path.insert(0, '/home/bbrelin/src/repos/artemis/src')

from coding_standards.validation import CodeStandardsValidator


def test_code_standards_validator_directly():
    """Test code standards validator directly without pipeline"""
    print("\n=== Direct Code Standards Validator Test ===")

    # Create temp directory with code that has violations
    with tempfile.TemporaryDirectory() as temp_dir:
        # Write code with nested ifs
        test_file = Path(temp_dir) / "test_code.py"
        test_file.write_text("""
def bad_function():
    '''Function with nested ifs'''
    if condition1:
        if condition2:
            if condition3:
                return True
    return False
""")

        # Create validator
        validator = CodeStandardsValidator(verbose=True)

        # Run validation
        result = validator.validate_code_standards(
            code_dir=temp_dir,
            severity_threshold="warning"
        )

        # Check results
        print(f"\n✓ Files scanned: {result.files_scanned}")
        print(f"✓ Is valid: {result.is_valid}")
        print(f"✓ Violation count: {result.violation_count}")

        if result.violations:
            print("\nViolations found:")
            for v in result.violations:
                print(f"  - {v['file']}:{v['line']} [{v['severity']}] {v['message']}")

        assert result.files_scanned == 1
        assert result.is_valid is False  # Should have violations
        assert result.violation_count > 0  # Should detect nested ifs

        print("\n✅ Test PASSED: Code standards validator works correctly")


def test_code_standards_validator_clean_code():
    """Test with clean code"""
    print("\n=== Clean Code Test ===")

    with tempfile.TemporaryDirectory() as temp_dir:
        # Write clean code
        test_file = Path(temp_dir) / "clean.py"
        test_file.write_text("""
def good_function(data):
    '''Clean function with guard clauses'''
    # Guard: No data
    if not data:
        return None

    # Process data
    return process(data)

def process(data):
    return data * 2
""")

        validator = CodeStandardsValidator(verbose=False)
        result = validator.validate_code_standards(
            code_dir=temp_dir,
            severity_threshold="warning"
        )

        print(f"\n✓ Files scanned: {result.files_scanned}")
        print(f"✓ Is valid: {result.is_valid}")
        print(f"✓ Violation count: {result.violation_count}")

        assert result.files_scanned == 1
        assert result.is_valid is True  # Should be valid
        assert result.violation_count == 0  # No violations

        print("\n✅ Test PASSED: Clean code validated correctly")


def test_standalone_script_still_works():
    """Verify standalone code_standards_validator.py still works"""
    print("\n=== Standalone Script Test ===")

    # Import the backward compatibility wrapper
    from code_standards_validator import CodeStandardsValidator, ValidationResult

    print("✓ Successfully imported from code_standards_validator")

    # Create a simple test
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = Path(temp_dir) / "test.py"
        test_file.write_text("def hello():\n    pass\n")

        validator = CodeStandardsValidator()
        result = validator.validate_code_standards(temp_dir, "warning")

        assert isinstance(result, ValidationResult)
        assert result.files_scanned >= 1

        print("✓ Standalone validator works correctly")
        print("\n✅ Test PASSED: Backward compatibility maintained")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Code Standards Integration Tests (Isolated)")
    print("="*60)

    try:
        test_code_standards_validator_directly()
        test_code_standards_validator_clean_code()
        test_standalone_script_still_works()

        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED")
        print("="*60)
        print("\nThe code standards validator:")
        print("  ✓ Detects violations correctly")
        print("  ✓ Validates clean code correctly")
        print("  ✓ Maintains backward compatibility")
        print("  ✓ Ready for pipeline integration")

    except AssertionError as e:
        print("\n" + "="*60)
        print(f"❌ TEST FAILED: {e}")
        print("="*60)
        raise

    except Exception as e:
        print("\n" + "="*60)
        print(f"❌ TEST ERROR: {e}")
        print("="*60)
        import traceback
        traceback.print_exc()
        raise
