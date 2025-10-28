#!/usr/bin/env python3
"""
WHY: Format CLI output for analysis, build, and test results
RESPONSIBILITY: Convert data structures to human-readable or JSON output
PATTERNS: Visitor (data formatting), Template Method (output templates)

Formatters provide clean separation between data and presentation.
"""

import json
from typing import Any


def print_analysis(analysis: Any, as_json: bool = False) -> None:
    """
    Print formatted analysis results.

    WHY: Single place for analysis output formatting (DRY).

    Args:
        analysis: JavaEcosystemAnalysis object
        as_json: Whether to output as JSON
    """
    # Early return for JSON output (avoid nesting)
    if as_json:
        print(json.dumps(analysis.summary, indent=2))
        return

    # Default formatted table output
    _print_table("Java Ecosystem Analysis", analysis.summary)


def print_build_result(result: Any, skip_tests: bool) -> None:
    """
    Print formatted build results.

    WHY: Single place for build output formatting (DRY).

    Args:
        result: Build result object
        skip_tests: Whether tests were skipped
    """
    status = "SUCCESS" if result.success else "FAILURE"

    data = {
        "Build Result": status,
        "Duration": f"{result.duration:.2f}s",
        "Exit Code": result.exit_code
    }

    # Add test results if not skipped and available
    if not skip_tests and hasattr(result, 'tests_run'):
        data["Tests"] = f"{result.tests_passed}/{result.tests_run} passed"

    _print_table(f"Build Result: {status}", data)


def print_test_result(result: Any) -> None:
    """
    Print formatted test results.

    WHY: Single place for test output formatting (DRY).

    Args:
        result: Test result object
    """
    status = "SUCCESS" if result.success else "FAILURE"

    data = {
        "Tests Run": result.tests_run,
        "Passed": result.tests_passed,
        "Failed": result.tests_failed,
        "Duration": f"{result.duration:.2f}s"
    }

    _print_table(f"Test Result: {status}", data)


def _print_table(title: str, data: dict) -> None:
    """
    Print a formatted table with title and data.

    WHY: DRY - single table formatting template.

    Args:
        title: Table title
        data: Dictionary of key-value pairs to display
    """
    separator = "=" * 60

    print(f"\n{separator}")
    print(title)
    print(separator)

    for key, value in data.items():
        # Handle both string keys and pre-formatted keys
        if isinstance(key, str) and isinstance(value, (str, int, float)):
            print(f"{key:25} {value}")
        else:
            print(f"{key} {value}")

    print(f"{separator}\n")
