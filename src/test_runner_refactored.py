#!/usr/bin/env python3
"""
BACKWARD COMPATIBILITY WRAPPER

WHY: Maintain compatibility with refactored version
RESPONSIBILITY: Re-export all components from modular testing package
PATTERNS: Facade Pattern, Adapter Pattern

This file maintains backward compatibility by re-exporting all components
from the new modular testing package (stages.testing).

DEPRECATED: This module is deprecated in favor of stages.testing
New code should import directly from stages.testing

Migration path:
    OLD: from test_runner_refactored import TestRunner, TestResult
    NEW: from stages.testing import TestRunner, TestResult
"""

import sys
import json
import logging

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
from stages.testing.base import BaseFrameworkRunner, FrameworkRunner
from stages.testing.cli import print_json_results as _print_json_results
from stages.testing.cli import print_text_results as _print_text_results


# CLI entry point maintained for backward compatibility
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Universal Test Runner - Supports multiple test frameworks"
    )
    parser.add_argument(
        "--framework",
        choices=[f.value for f in TestFramework],
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

    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    try:
        # Run tests
        runner = TestRunner(
            framework=args.framework,
            verbose=args.verbose,
            timeout=args.timeout
        )

        result = runner.run_tests(args.path)

        # Output results
        if args.json:
            _print_json_results(result)
        else:
            _print_text_results(result, args.verbose)

        # Exit with test result code
        sys.exit(result.exit_code)

    except TestRunnerError as e:
        logging.error(f"Test runner error: {e}")
        if args.json:
            print(json.dumps({"error": str(e), "type": type(e).__name__}, indent=2))
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error: {e}", exc_info=True)
        if args.json:
            print(json.dumps({"error": str(e), "type": "UnexpectedError"}, indent=2))
        sys.exit(1)
