#!/usr/bin/env python3
"""
PHPUnit Test Runner

WHY: Isolated test execution and statistics extraction logic
RESPONSIBILITY: Run PHPUnit tests and parse results
PATTERNS:
- Single Responsibility: Only handles test execution
- Strategy pattern: Different test execution strategies
- Regex parsing: Extract test statistics from output
"""

from pathlib import Path
from typing import Optional, Callable, Dict
import logging
import re

from artemis_exceptions import wrap_exception
from build_system_exceptions import TestExecutionError
from build_manager_base import BuildResult


class TestRunner:
    """
    Runs PHPUnit tests via Composer.

    WHY: Separate test execution logic from main manager
    RESPONSIBILITY: Execute tests and extract statistics
    """

    def __init__(
        self,
        project_dir: Path,
        execute_command: Callable,
        parser: 'ComposerParser',
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize test runner.

        Args:
            project_dir: Project directory
            execute_command: Command execution function from parent manager
            parser: Composer parser for checking test scripts
            logger: Logger instance
        """
        self.project_dir = project_dir
        self._execute_command = execute_command
        self.parser = parser
        self.logger = logger or logging.getLogger(__name__)

    @wrap_exception(TestExecutionError, "Tests failed")
    def run_tests(
        self,
        test_path: Optional[str] = None,
        verbose: bool = False
    ) -> BuildResult:
        """
        Run tests with PHPUnit via composer.

        WHY: Execute test suite with flexible configuration
        RESPONSIBILITY: Build test command and execute with statistics extraction

        Args:
            test_path: Specific test file or directory to run
            verbose: Enable verbose test output

        Returns:
            BuildResult with test statistics

        Raises:
            TestExecutionError: If tests fail to execute

        Example:
            result = runner.run_tests(verbose=True)
        """
        cmd = self._build_test_command(test_path, verbose)

        result = self._execute_command(
            cmd,
            timeout=300,
            error_type=TestExecutionError,
            error_message="Test execution failed"
        )

        # Extract test statistics from output
        stats = self._extract_test_stats(result.output)
        result.tests_run = stats['tests_run']
        result.tests_passed = stats['tests_passed']
        result.tests_failed = stats['tests_failed']
        result.tests_skipped = stats['tests_skipped']

        return result

    def _build_test_command(
        self,
        test_path: Optional[str],
        verbose: bool
    ) -> list[str]:
        """
        Build test command array.

        WHY: Separate command construction from execution
        RESPONSIBILITY: Choose between composer test script and direct PHPUnit

        Args:
            test_path: Optional specific test path
            verbose: Verbose output flag

        Returns:
            Command array for test execution
        """
        # Check if there's a test script defined in composer.json
        if self.parser.has_script("test"):
            cmd = ["composer", "test"]
        else:
            # Fall back to direct PHPUnit call
            cmd = ["./vendor/bin/phpunit"]

        if verbose:
            cmd.append("--verbose")

        if test_path:
            cmd.append(test_path)

        return cmd

    def _extract_test_stats(self, output: str) -> Dict[str, int]:
        """
        Extract test statistics from PHPUnit output.

        WHY: Parse test results for reporting and validation
        RESPONSIBILITY: Use regex to extract test counts from output

        Args:
            output: PHPUnit command output

        Returns:
            Dictionary with test counts:
            - tests_run: Total tests executed
            - tests_passed: Successfully passed tests
            - tests_failed: Failed tests
            - tests_skipped: Skipped or incomplete tests

        Example PHPUnit output formats:
            "Tests: 15, Assertions: 42, Failures: 2, Skipped: 1"
            "OK (15 tests, 42 assertions)"
        """
        stats = {
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'tests_skipped': 0
        }

        # Try to match detailed format first
        stats_match = self._parse_detailed_format(output)
        if stats_match:
            return stats_match

        # Try to match OK format
        stats_match = self._parse_ok_format(output)
        if stats_match:
            return stats_match

        return stats

    def _parse_detailed_format(self, output: str) -> Optional[Dict[str, int]]:
        """
        Parse detailed PHPUnit format.

        WHY: Extract statistics from verbose test output
        RESPONSIBILITY: Parse "Tests: X, Assertions: Y, Failures: Z" format

        Args:
            output: PHPUnit output

        Returns:
            Statistics dict or None if format not matched

        Example:
            "Tests: 15, Assertions: 42, Failures: 2, Skipped: 1"
        """
        summary_match = re.search(
            r'Tests:\s+(\d+),\s+Assertions:\s+\d+(?:,\s+Failures:\s+(\d+))?(?:,\s+(?:Skipped|Incomplete):\s+(\d+))?',
            output
        )

        if not summary_match:
            return None

        total = int(summary_match.group(1))
        failures = int(summary_match.group(2) or 0)
        skipped = int(summary_match.group(3) or 0)

        return {
            'tests_run': total - skipped,
            'tests_failed': failures,
            'tests_passed': total - failures - skipped,
            'tests_skipped': skipped
        }

    def _parse_ok_format(self, output: str) -> Optional[Dict[str, int]]:
        """
        Parse OK format PHPUnit output.

        WHY: Extract statistics from success-only output
        RESPONSIBILITY: Parse "OK (X tests, Y assertions)" format

        Args:
            output: PHPUnit output

        Returns:
            Statistics dict or None if format not matched

        Example:
            "OK (15 tests, 42 assertions)"
        """
        ok_match = re.search(r'OK\s+\((\d+)\s+tests?,', output)

        if not ok_match:
            return None

        total = int(ok_match.group(1))

        return {
            'tests_run': total,
            'tests_passed': total,
            'tests_failed': 0,
            'tests_skipped': 0
        }
