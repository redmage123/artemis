#!/usr/bin/env python3
"""
Bash Manager - Bats Test Runner

WHY: Separate test execution logic from orchestration for Single Responsibility
RESPONSIBILITY: Execute bats tests and parse results
PATTERNS: Command Pattern, Strategy Pattern, Guard Clauses

This module wraps Bats (Bash Automated Testing System), providing structured
test results and metrics extraction.
"""

from pathlib import Path
from typing import List, Callable, Optional
import subprocess
import logging
import re
import time

from .models import TestResult


class BatsTestRunner:
    """
    Bats test execution wrapper.

    WHY: Single Responsibility - only concerned with test execution
    RESPONSIBILITY: Execute bats and parse test output
    PATTERNS: Command Pattern, Guard Clauses, Result Pattern
    """

    # Common test directory names
    DEFAULT_TEST_DIRS = ['test', 'tests', 'spec', 'bats']

    def __init__(
        self,
        project_dir: Path,
        execute_command: Callable[[List[str]], subprocess.CompletedProcess],
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize test runner.

        WHY: Dependency Injection for testability
        PATTERNS: Dependency Injection, Strategy Pattern

        Args:
            project_dir: Project root directory
            execute_command: Command executor (injected for testing)
            logger: Logger instance
        """
        self.project_dir = Path(project_dir)
        self.execute_command = execute_command
        self.logger = logger or logging.getLogger(__name__)

    def run_tests(self, test_dir: Optional[Path] = None) -> TestResult:
        """
        Run bats test suite.

        WHY: Single responsibility - execute tests
        RESPONSIBILITY: Run bats and return structured results
        PATTERNS: Guard Clauses, Result Pattern

        Args:
            test_dir: Test directory (auto-detected if None)

        Returns:
            TestResult with outcome and metrics
        """
        # Auto-detect test directory if not provided
        if test_dir is None:
            test_dir = self.find_test_directory()

        # Guard: No test directory found
        if test_dir is None:
            self.logger.info("No test directory found, skipping tests")
            return self._create_no_tests_result()

        # Guard: Test directory doesn't exist
        if not test_dir.exists():
            self.logger.warning(f"Test directory not found: {test_dir}")
            return self._create_no_tests_result()

        # Guard: Test directory is empty
        test_files = self._find_test_files(test_dir)
        if not test_files:
            self.logger.info(f"No test files in {test_dir}, skipping tests")
            return self._create_no_tests_result()

        # Execute tests
        return self._execute_tests(test_dir)

    def find_test_directory(self) -> Optional[Path]:
        """
        Auto-detect test directory.

        WHY: Convention over configuration
        RESPONSIBILITY: Find test directory using common names
        PATTERNS: Guard Clauses, Strategy Pattern

        Returns:
            Path to test directory or None
        """
        for dir_name in self.DEFAULT_TEST_DIRS:
            candidate = self.project_dir / dir_name
            if candidate.exists() and candidate.is_dir():
                self.logger.debug(f"Found test directory: {candidate}")
                return candidate

        self.logger.debug("No test directory found")
        return None

    def has_tests(self) -> bool:
        """
        Quick check if tests exist.

        WHY: Fast detection without running tests
        RESPONSIBILITY: Boolean existence check
        PATTERNS: Guard Clauses

        Returns:
            True if test directory with files exists
        """
        test_dir = self.find_test_directory()
        if test_dir is None:
            return False

        test_files = self._find_test_files(test_dir)
        return len(test_files) > 0

    def _execute_tests(self, test_dir: Path) -> TestResult:
        """
        Execute bats test suite.

        WHY: Centralize test execution logic
        RESPONSIBILITY: Run bats and parse results
        PATTERNS: Command Pattern, Exception Handling

        Args:
            test_dir: Directory containing tests

        Returns:
            TestResult with metrics
        """
        cmd = ["bats", str(test_dir)]

        self.logger.info(f"Running bats tests in {test_dir}...")
        start_time = time.time()

        try:
            # Execute bats
            result = self.execute_command(cmd)
            duration = time.time() - start_time

            # Parse result
            return self._parse_result(result, duration)

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            self.logger.error("Bats test timeout")
            return self._create_error_result(
                "Test execution timeout",
                duration
            )

        except FileNotFoundError:
            duration = time.time() - start_time
            self.logger.error("Bats not found in PATH")
            return self._create_error_result(
                "Bats not installed or not in PATH",
                duration
            )

        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"Test execution failed: {e}")
            return self._create_error_result(str(e), duration)

    def _parse_result(
        self,
        result: subprocess.CompletedProcess,
        duration: float
    ) -> TestResult:
        """
        Parse bats test output.

        WHY: Centralize result parsing logic
        RESPONSIBILITY: Extract test metrics from output
        PATTERNS: Factory Method, Parser Pattern

        Args:
            result: Subprocess result
            duration: Execution duration

        Returns:
            Structured TestResult
        """
        output = result.stdout.decode() if isinstance(result.stdout, bytes) else result.stdout
        passed = result.returncode == 0

        # Extract test metrics
        stats = self._extract_test_stats(output)

        return TestResult(
            passed=passed,
            output=output,
            exit_code=result.returncode,
            tests_run=stats['run'],
            tests_passed=stats['passed'],
            tests_failed=stats['failed'],
            tests_skipped=stats['skipped'],
            duration=duration
        )

    def _extract_test_stats(self, output: str) -> dict:
        """
        Extract test statistics from bats output.

        WHY: Parse structured metrics from text output
        RESPONSIBILITY: Extract counts using regex patterns
        PATTERNS: Parser Pattern, Regular Expressions

        Args:
            output: Bats output text

        Returns:
            Dictionary with test counts
        """
        stats = {
            'run': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0
        }

        # Bats output format examples:
        # "✓ test description"  (passed)
        # "✗ test description"  (failed)
        # "- test description"  (skipped)

        # Count test lines
        for line in output.splitlines():
            self._parse_test_line(line.strip(), stats)

        # Alternative: Parse summary line
        # Example: "3 tests, 0 failures"
        summary_match = re.search(
            r'(\d+)\s+tests?,\s+(\d+)\s+failures?',
            output,
            re.IGNORECASE
        )
        if summary_match:
            total = int(summary_match.group(1))
            failures = int(summary_match.group(2))
            stats['run'] = total
            stats['failed'] = failures
            stats['passed'] = total - failures

        return stats

    @staticmethod
    def _parse_test_line(line: str, stats: dict) -> None:
        """
        Parse single test line and update stats.

        WHY: Separate line parsing to avoid nested control flow
        RESPONSIBILITY: Update stats dict based on line prefix
        PATTERNS: Guard Clauses, Dispatch Table (O(1) lookups)
        """
        # Guard: Empty line
        if not line:
            return

        # Dispatch table: prefix → stats updates
        # Using tuple unpacking for clarity
        prefix_handlers = {
            '✓': ('run', 'passed'),
            '✗': ('run', 'failed'),
        }

        # Check dispatch table
        for prefix, fields in prefix_handlers.items():
            if line.startswith(prefix):
                for field in fields:
                    stats[field] += 1
                return

        # Special case: skipped tests (prefix + content check)
        if line.startswith('-') and 'skipped' in line.lower():
            stats['skipped'] += 1

    def _find_test_files(self, test_dir: Path) -> List[Path]:
        """
        Find all bats test files in directory.

        WHY: Validate test directory has actual tests
        RESPONSIBILITY: Locate .bats files
        PATTERNS: Guard Clauses

        Args:
            test_dir: Directory to search

        Returns:
            List of test file paths
        """
        # Guard: Directory doesn't exist
        if not test_dir.exists() or not test_dir.is_dir():
            return []

        try:
            # Find all .bats files
            return list(test_dir.glob("**/*.bats"))
        except Exception as e:
            self.logger.warning(f"Failed to scan test directory: {e}")
            return []

    def _create_no_tests_result(self) -> TestResult:
        """
        Create result for "no tests" scenario.

        WHY: Consistent result objects even when tests don't exist
        RESPONSIBILITY: Factory method for no-tests results
        PATTERNS: Factory Method, Null Object Pattern

        Returns:
            TestResult indicating no tests (passes)
        """
        return TestResult(
            passed=True,  # No tests = passing
            output="No tests found",
            exit_code=0,
            tests_run=0,
            tests_passed=0,
            tests_failed=0,
            tests_skipped=0,
            duration=0.0
        )

    def _create_error_result(self, error: str, duration: float) -> TestResult:
        """
        Create result for test execution errors.

        WHY: Consistent error handling
        RESPONSIBILITY: Factory method for error results
        PATTERNS: Factory Method

        Args:
            error: Error message
            duration: Execution duration

        Returns:
            TestResult indicating failure
        """
        return TestResult(
            passed=False,
            output=error,
            exit_code=1,
            tests_run=0,
            tests_passed=0,
            tests_failed=0,
            tests_skipped=0,
            duration=duration
        )


__all__ = [
    'BatsTestRunner'
]
