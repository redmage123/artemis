#!/usr/bin/env python3
"""
Configuration Validation Report Generator

WHY: Handles generating and printing validation reports

RESPONSIBILITY: Aggregate validation results and format reports

PATTERNS: Pure functions for report generation
"""

from typing import List
from .models import ValidationResult, ValidationReport


def generate_report(results: List[ValidationResult]) -> ValidationReport:
    """
    Generate validation report from results

    WHY: Aggregates all validation results into comprehensive report
    PERFORMANCE: O(n) where n is number of results, using list comprehensions

    Args:
        results: List of validation results

    Returns:
        ValidationReport with aggregated statistics
    """
    # Use list comprehensions for performance (faster than loops)
    errors = [r for r in results if not r.passed and r.severity == "error"]
    warnings = [r for r in results if not r.passed and r.severity == "warning"]
    passed = [r for r in results if r.passed]

    # Guard clause: Determine overall status with early returns
    # WHY: More readable than nested if/else
    if errors:
        overall_status = "fail"
    elif warnings:
        overall_status = "warning"
    else:
        overall_status = "pass"

    return ValidationReport(
        overall_status=overall_status,
        total_checks=len(results),
        passed=len(passed),
        warnings=len(warnings),
        errors=len(errors),
        results=results
    )


def print_report(report: ValidationReport) -> None:
    """
    Print validation report

    WHY: Provides human-readable summary of validation results
    PATTERNS: Strategy pattern for status messages
    PERFORMANCE: O(1) - simple string formatting

    Args:
        report: ValidationReport to print
    """
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)

    print(f"\nTotal checks: {report.total_checks}")
    print(f"  Passed: {report.passed}")
    if report.warnings > 0:
        print(f"  Warnings: {report.warnings}")
    if report.errors > 0:
        print(f"  Errors: {report.errors}")

    # Strategy pattern: Dictionary mapping for status messages
    # WHY: Avoids if/elif chain, makes it easy to add new status types
    status_messages = {
        "pass": (
            "\nAll validation checks passed!",
            "Artemis is ready to run."
        ),
        "warning": (
            "\nValidation completed with warnings",
            "Artemis can run but some features may not work."
        ),
        "fail": (
            "\nValidation failed!",
            "Fix errors before running Artemis."
        )
    }

    messages = status_messages.get(report.overall_status, ("Unknown status", ""))
    for message in messages:
        print(message)

    print("\n" + "=" * 70 + "\n")


def print_result(result: ValidationResult) -> None:
    """
    Print a single validation result

    WHY: Provides formatted output for individual validation checks

    Args:
        result: ValidationResult to print
    """
    # Print result with appropriate symbol (avoid emojis per claude.md)
    symbol = "[PASS]" if result.passed else ("[WARN]" if result.severity == "warning" else "[FAIL]")
    print(f"{symbol} {result.check_name}: {result.message}")

    # Print fix suggestion if validation failed
    if not result.passed and result.fix_suggestion:
        print(f"   Fix: {result.fix_suggestion}")
