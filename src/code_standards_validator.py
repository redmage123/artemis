#!/usr/bin/env python3
"""
BACKWARD COMPATIBILITY WRAPPER

This module maintains backward compatibility while the codebase migrates
to the new modular structure in coding_standards/validation/.

All functionality has been refactored into:
- coding_standards/validation/models.py - ValidationResult
- coding_standards/validation/severity_filter.py - Severity filtering
- coding_standards/validation/formatter.py - Violation formatting
- coding_standards/validation/validator.py - CodeStandardsValidator

To migrate your code:
    OLD: from code_standards_validator import CodeStandardsValidator, ValidationResult
    NEW: from coding_standards.validation import CodeStandardsValidator, ValidationResult

No breaking changes - all imports remain identical.
"""

# Re-export all public APIs from the modular package
from coding_standards.validation import (
    CodeStandardsValidator,
    ValidationResult,
)

__all__ = [
    'CodeStandardsValidator',
    'ValidationResult',
]

# Example usage
if __name__ == "__main__":
    validator = CodeStandardsValidator(verbose=True)

    # Validate src directory
    result = validator.validate_code_standards(
        code_dir="src",
        severity_threshold="critical"
    )

    print(result.summary)
    print(f"\nFiles scanned: {result.files_scanned}")
    print(f"Violations found: {result.violation_count}")

    # Print sample violations
    if not result.is_valid:
        print("\nViolations:")
        for v in result.violations[:5]:
            print(f"  {v['file']}:{v['line']} - {v['message']}")

        remaining = result.violation_count - 5
        if remaining > 0:
            print(f"  ... and {remaining} more")
