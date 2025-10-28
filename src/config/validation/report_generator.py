#!/usr/bin/env python3
"""
Report Generator - Validation report generation and printing

WHY: Generates comprehensive validation reports and provides human-readable
     output for validation results.

RESPONSIBILITY: Generate validation reports and format output.

PATTERNS: Strategy pattern for status messages, pure functions for report generation.
"""

from typing import List, Tuple, Dict
from config.validation.models import ValidationResult, ValidationReport


class ReportGenerator:
    """
    Generates validation reports from results.

    WHY: Aggregates validation results into comprehensive report.
    RESPONSIBILITY: Generate ValidationReport from results only.
    PATTERNS: Pure functions for report generation, list comprehensions for filtering.
    """

    @staticmethod
    def generate(results: List[ValidationResult]) -> ValidationReport:
        """
        Generate validation report from results.

        WHY: Aggregates all validation results into comprehensive report.
        PERFORMANCE: O(n) where n is number of results, using list comprehensions.

        Args:
            results: List of ValidationResults to aggregate

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


class ReportPrinter:
    """
    Prints validation reports and individual results.

    WHY: Provides human-readable output for validation results.
    RESPONSIBILITY: Format and print validation output only.
    PATTERNS: Strategy pattern for status messages, guard clauses.
    """

    # Strategy pattern: Status message mapping
    # WHY: Avoids if/elif chain, makes it easy to add new status types
    STATUS_MESSAGES: Dict[str, Tuple[str, str]] = {
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

    @staticmethod
    def print_result(result: ValidationResult) -> None:
        """
        Print a single validation result.

        WHY: Provides immediate feedback during validation.
        PERFORMANCE: O(1) string formatting and printing.

        Args:
            result: ValidationResult to print
        """
        # Determine symbol based on result
        symbol = "[PASS]" if result.passed else (
            "[WARN]" if result.severity == "warning" else "[FAIL]"
        )

        print(f"{symbol} {result.check_name}: {result.message}")

        # Print fix suggestion if validation failed
        if not result.passed and result.fix_suggestion:
            print(f"   Fix: {result.fix_suggestion}")

    @staticmethod
    def print_header() -> None:
        """
        Print validation header.

        WHY: Provides clear visual separation for validation output.
        PERFORMANCE: O(1) string printing.
        """
        print("\n" + "=" * 70)
        print("ARTEMIS CONFIGURATION VALIDATION")
        print("=" * 70 + "\n")

    @staticmethod
    def print_report(report: ValidationReport) -> None:
        """
        Print validation report summary.

        WHY: Provides human-readable summary of validation results.
        PERFORMANCE: O(1) - simple string formatting.

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

        # Get status messages using strategy pattern
        messages = ReportPrinter.STATUS_MESSAGES.get(
            report.overall_status,
            ("Unknown status", "")
        )

        for message in messages:
            print(message)

        print("\n" + "=" * 70 + "\n")
