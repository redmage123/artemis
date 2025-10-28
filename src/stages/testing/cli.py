#!/usr/bin/env python3
"""
WHY: Command-line interface helpers for test runner
RESPONSIBILITY: Format and display test results
PATTERNS: Strategy Pattern for output formats

This module provides functions for formatting and displaying test results
in different formats (JSON, text) suitable for CLI usage.
"""

import json
from typing import Optional

from stages.testing.models import TestResult


def print_test_results(
    result: TestResult,
    as_json: bool = False,
    verbose: bool = False
) -> None:
    """
    WHY: Display test results to console
    RESPONSIBILITY: Choose and apply output format

    Args:
        result: TestResult to display
        as_json: Whether to output as JSON
        verbose: Whether to include verbose output
    """
    if as_json:
        print_json_results(result)
        return

    print_text_results(result, verbose)


def print_json_results(result: TestResult) -> None:
    """
    WHY: Output results in JSON format
    RESPONSIBILITY: Serialize result to JSON

    Args:
        result: TestResult to serialize
    """
    print(json.dumps({
        "framework": result.framework,
        "passed": result.passed,
        "failed": result.failed,
        "skipped": result.skipped,
        "errors": result.errors,
        "total": result.total,
        "pass_rate": result.pass_rate,
        "success": result.success,
        "exit_code": result.exit_code,
        "duration": result.duration
    }, indent=2))


def print_text_results(result: TestResult, verbose: bool = False) -> None:
    """
    WHY: Output results in formatted text
    RESPONSIBILITY: Format result as human-readable table

    Args:
        result: TestResult to format
        verbose: Whether to include test output
    """
    print(f"\n{'='*60}")
    print(f"Test Results ({result.framework})")
    print(f"{'='*60}")
    print(f"Total:     {result.total}")
    print(f"Passed:    {result.passed}")
    print(f"Failed:    {result.failed}")
    print(f"Skipped:   {result.skipped}")
    print(f"Errors:    {result.errors}")
    print(f"Pass Rate: {result.pass_rate}%")
    print(f"Duration:  {result.duration:.2f}s")
    print(f"Status:    {'SUCCESS' if result.success else 'FAILURE'}")
    print(f"{'='*60}\n")

    if verbose:
        print("Test Output:")
        print(result.output)
