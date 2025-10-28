#!/usr/bin/env python3
"""
Enhanced Function Signature Validator for Artemis (Backward Compatibility Wrapper)

WHY: Maintains backward compatibility while delegating to modular implementation
RESPONSIBILITY: Provide legacy API that delegates to signature_validation package
PATTERNS: Facade pattern, delegation pattern

This is a backward compatibility wrapper. New code should use:
    from signature_validation import EnhancedSignatureValidator

USAGE:
    from enhanced_signature_validator import EnhancedSignatureValidator

    validator = EnhancedSignatureValidator()
    result = validator.validate_file("src/my_module.py")

    for issue in result:
        print(f"{issue.file_path}:{issue.line_number} - {issue.message}")
"""

from pathlib import Path
from typing import List, Set, Optional
import sys

# Import from modular package
from signature_validation import (
    EnhancedSignatureValidator,
    SignatureIssue,
    FunctionInfo,
    TypeChecker,
)

# Re-export for backward compatibility
__all__ = [
    'EnhancedSignatureValidator',
    'SignatureIssue',
    'FunctionInfo',
    'TypeChecker',
]


def _print_issue(issue: SignatureIssue) -> None:
    """
    Print a single issue with optional suggestion

    WHY: Formatted output for CLI usage
    RESPONSIBILITY: Display single validation issue
    PATTERNS: Simple formatting helper
    """
    print(f"   {issue.file_path}:{issue.line_number}")
    print(f"   {issue.message}")
    if issue.suggestion:
        print(f"   💡 {issue.suggestion}")
    print()


def _print_issues_by_severity(
    issues: List[SignatureIssue],
    severity: str,
    label: str
) -> None:
    """
    Print issues of a specific severity

    WHY: Group issues by severity for better readability
    RESPONSIBILITY: Filter and display issues by severity
    PATTERNS: Filter and iterate

    Args:
        issues: List of all issues
        severity: Severity level to filter
        label: Display label for section
    """
    filtered = [i for i in issues if i.severity == severity]

    # Guard clause: no issues of this severity
    if not filtered:
        return

    print(f"{label} ({len(filtered)}):\n")
    for issue in filtered:
        _print_issue(issue)


def _run_validation(
    target: str,
    validator: EnhancedSignatureValidator
) -> List[SignatureIssue]:
    """
    Run validation on file or directory

    WHY: Unified entry point for file or directory validation
    RESPONSIBILITY: Determine validation target type
    PATTERNS: Strategy pattern based on target type

    Args:
        target: File or directory path
        validator: Validator instance

    Returns:
        List of validation issues
    """
    if Path(target).is_file():
        return validator.validate_file(target)
    return validator.validate_directory(target)


def _print_results(issues: List[SignatureIssue]) -> None:
    """
    Print validation results

    WHY: Formatted output of all validation results
    RESPONSIBILITY: Display all issues grouped by severity
    PATTERNS: Template method for output

    Args:
        issues: List of all validation issues
    """
    # Guard clause: no issues found
    if not issues:
        print("✅ No signature or type issues found!")
        return

    print(f"\n🔍 Found {len(issues)} signature/type issues:\n")
    _print_issues_by_severity(issues, 'critical', '🚨 CRITICAL')
    _print_issues_by_severity(issues, 'warning', '⚠️  WARNINGS')


def _get_exit_code(issues: List[SignatureIssue]) -> int:
    """
    Determine exit code based on issues

    WHY: Standard exit codes for CLI integration
    RESPONSIBILITY: Calculate appropriate exit code
    PATTERNS: Guard clauses

    Args:
        issues: List of all validation issues

    Returns:
        0 for success, 1 for critical issues
    """
    # Guard clause: no issues
    if not issues:
        return 0

    critical = [i for i in issues if i.severity == 'critical']
    return 1 if critical else 0


# Example usage and CLI
if __name__ == "__main__":
    # Guard clause: check arguments
    if len(sys.argv) <= 1:
        print("Usage: python3 enhanced_signature_validator.py <file_or_directory>")
        sys.exit(1)

    validator = EnhancedSignatureValidator(verbose=True)
    target = sys.argv[1]

    issues = _run_validation(target, validator)
    _print_results(issues)
    sys.exit(_get_exit_code(issues))
