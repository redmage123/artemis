#!/usr/bin/env python3
"""
BACKWARD COMPATIBILITY WRAPPER

WHY: Maintain compatibility with existing code
RESPONSIBILITY: Re-export all components from modular testing package
PATTERNS: Facade Pattern, Adapter Pattern

This file maintains backward compatibility by re-exporting all components
from the new modular testing package (stages.testing).

DEPRECATED: This module is deprecated in favor of stages.testing
New code should import directly from stages.testing

Migration path:
    OLD: from test_runner import TestRunner, TestResult
    NEW: from stages.testing import TestRunner, TestResult
"""

import sys
from pathlib import Path

# Re-export all components from modular package
from stages.testing import (
    TestRunner,
    TestResult,
    TestFramework,
    TestRunnerError,
    TestPathNotFoundError,
    TestFrameworkNotFoundError,
    TestExecutionError,
    TestTimeoutError,
    TestOutputParsingError,
    FrameworkRunnerFactory,
    FrameworkDetector
)
from stages.testing.cli import print_test_results as _print_test_results

# Maintain backward compatibility for CLI helper functions
_print_json_results = lambda result: _print_test_results(result, as_json=True)
_print_formatted_results = lambda result: _print_test_results(result, as_json=False, verbose=False)
_print_verbose_output = lambda result: print("Test Output:") or print(result.output)


def _print_text_results(result: TestResult, verbose: bool = False) -> None:
    """Backward compatibility wrapper for text results"""
    _print_test_results(result, as_json=False, verbose=verbose)


# CLI entry point maintained for backward compatibility
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Universal Test Runner - Supports pytest, unittest, gtest, junit"
    )
    parser.add_argument(
        "--framework",
        choices=["pytest", "unittest", "gtest", "junit", "jest", "robot", "hypothesis", "jmeter", "playwright", "appium", "selenium"],
        help="Test framework to use (auto-detected if not specified)"
    )
    parser.add_argument(
        "--path",
        required=True,
        help="Path to test directory or file"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="Test execution timeout in seconds (default: 120)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    args = parser.parse_args()

    # Run tests
    runner = TestRunner(
        framework=args.framework,
        verbose=args.verbose,
        timeout=args.timeout
    )

    result = runner.run_tests(args.path)

    # Output results
    _print_test_results(result, as_json=args.json, verbose=args.verbose)

    # Exit with test result code
    exit(result.exit_code)

