#!/usr/bin/env python3
"""
Module: services.core.test_runner

WHY: Encapsulates all test execution logic in one place, making it testable and
     allowing easy substitution with mock implementations during testing.

RESPONSIBILITY: Execute pytest test suites and parse results into structured data.

PATTERNS:
- Single Responsibility: Only handles test execution and result parsing
- Strategy Pattern: Can be swapped with different test runners (pytest, unittest, etc.)
- Interface Segregation: Implements TestRunnerInterface for loose coupling

DESIGN DECISIONS:
- Uses subprocess for pytest execution (isolation, timeout control)
- Regex parsing for output (pytest format is stable and well-documented)
- Timeout defaults to 60s (prevents infinite loops in tests)
- Returns standardized dict format (consistent API for consumers)

Dependencies: core.interfaces, core.constants
"""

import re
import subprocess
from typing import Dict, Optional, Tuple

from core.interfaces import TestRunnerInterface
from core.constants import PYTEST_PATH as DEFAULT_PYTEST_PATH


class TestRunner(TestRunnerInterface):
    """
    Test execution service using pytest.

    WHAT: Executes pytest test suites and parses the output into structured data.
    WHY: Provides a consistent interface for running tests across the pipeline.

    Attributes:
        pytest_path: Path to pytest executable (allows venv/system override)

    Example:
        >>> runner = TestRunner()
        >>> results = runner.run_tests("tests/unit/")
        >>> print(f"Pass rate: {results['pass_rate']}")
    """

    # Configuration constants
    DEFAULT_TIMEOUT: int = 60
    PYTEST_ARGS: Tuple[str, ...] = ("-v", "--tb=short", "-q")

    # Regex patterns for parsing pytest output
    PATTERN_PASSED: str = r'(\d+) passed'
    PATTERN_FAILED: str = r'(\d+) failed'
    PATTERN_SKIPPED: str = r'(\d+) skipped'

    def __init__(self, pytest_path: Optional[str] = None) -> None:
        """
        Initialize test runner.

        Args:
            pytest_path: Custom path to pytest executable. If None, uses default from constants.

        WHY: Allows overriding pytest location for different environments (venv, system, etc).
        """
        self.pytest_path: str = pytest_path or DEFAULT_PYTEST_PATH

    def run_tests(self, test_path: str, timeout: int = DEFAULT_TIMEOUT) -> Dict:
        """
        Run pytest and return parsed results.

        WHAT: Executes pytest with verbose output and parses pass/fail/skip counts.
        WHY: Provides standardized test results format for pipeline stages to consume.
             Timeout prevents hanging on infinite loops in tests.

        Args:
            test_path: Path to test files/directory
            timeout: Maximum execution time in seconds

        Returns:
            Dict containing:
                - total: Total number of tests run
                - passed: Number of passed tests
                - failed: Number of failed tests
                - skipped: Number of skipped tests
                - pass_rate: Percentage string (e.g., "85.7%")
                - exit_code: pytest exit code (0 = all passed)
                - output: Full pytest output (stdout + stderr)
                - stdout: Standard output only
                - stderr: Standard error only

        Raises:
            subprocess.TimeoutExpired: If tests exceed timeout duration
            FileNotFoundError: If pytest executable not found

        Example:
            >>> results = runner.run_tests("tests/", timeout=120)
            >>> if results['exit_code'] == 0:
            ...     print("All tests passed!")
        """
        # Guard clause: Validate test path
        if not test_path:
            raise ValueError("test_path cannot be empty")

        # Determine working directory for pytest
        # WHY: Tests need to import modules relative to their package root (e.g., "from auth.module import X")
        # If test_path points to a 'tests' directory, run pytest from the parent directory
        # so Python's import system can find sibling modules
        from pathlib import Path
        test_path_obj = Path(test_path)

        # If test_path is a tests directory, use parent as cwd so imports work
        if test_path_obj.name == 'tests' and test_path_obj.is_dir():
            working_dir = str(test_path_obj.parent)
            # Use relative path "tests" instead of absolute path
            pytest_target = "tests"
        else:
            working_dir = None
            pytest_target = test_path

        # Discover modules for coverage tracking
        # WHY: Generated code needs coverage tracking on its specific modules, not global config
        coverage_args = self._discover_coverage_modules(working_dir if working_dir else Path.cwd())

        # Execute pytest with configured arguments
        # WHY: Use "python -m pytest" instead of "pytest" directly for proper import resolution
        # This ensures Python's sys.path is set correctly for module imports
        import sys
        result = subprocess.run(
            [sys.executable, "-m", "pytest", pytest_target, *self.PYTEST_ARGS, *coverage_args],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=working_dir  # Set working directory for proper imports
        )

        # Combine stdout and stderr for comprehensive parsing
        output = result.stdout + result.stderr

        # Parse test counts from output
        passed, failed, skipped = self._parse_pytest_output(output)
        total = passed + failed + skipped

        # Calculate pass rate with guard against division by zero
        pass_rate = f"{(passed/total*100):.1f}%" if total > 0 else "0%"

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "pass_rate": pass_rate,
            "exit_code": result.returncode,
            "output": output,
            "stdout": result.stdout,  # Added for detailed debugging
            "stderr": result.stderr   # Added for detailed debugging
        }

    def _discover_coverage_modules(self, working_dir: str) -> Tuple[str, ...]:
        """
        Discover Python modules/packages in working directory for coverage tracking.

        WHAT: Scans for directories containing __init__.py (Python packages) to track coverage.
        WHY: Generated code needs dynamic coverage configuration based on what modules exist.

        Args:
            working_dir: Directory to scan for Python packages

        Returns:
            Tuple of coverage arguments (e.g., ("--cov=auth_module", "--cov-fail-under=75"))

        Example:
            If working_dir contains auth_module/__init__.py, returns:
            ("--cov=auth_module", "--cov-report=term-missing", "--cov-fail-under=75")
        """
        from pathlib import Path

        coverage_args = []
        working_path = Path(working_dir)

        # Find all directories with __init__.py (Python packages)
        for item in working_path.iterdir():
            if item.is_dir() and not item.name.startswith(('.', '__', 'tests')):
                init_file = item / '__init__.py'
                if init_file.exists():
                    # Add coverage for this module
                    coverage_args.append(f"--cov={item.name}")

        # If we found modules, add coverage reporting options
        if coverage_args:
            coverage_args.extend([
                "--cov-report=term-missing",
                "--cov-fail-under=80"  # Require 80% coverage for generated code
            ])
        else:
            # No modules found - skip coverage to avoid global pytest.ini conflicts
            coverage_args.append("--no-cov")

        return tuple(coverage_args)

    def _parse_pytest_output(self, output: str) -> Tuple[int, int, int]:
        """
        Parse pytest output to extract test counts.

        WHAT: Uses regex to extract passed/failed/skipped counts from pytest summary.
        WHY: Pytest output format is consistent and well-documented, making regex reliable.

        Args:
            output: Combined stdout and stderr from pytest execution

        Returns:
            Tuple of (passed, failed, skipped) counts

        Note: Uses walrus operator (:=) for concise pattern matching
        """
        passed = failed = skipped = 0

        # Extract counts using regex with walrus operator (guard clause pattern)
        if match := re.search(self.PATTERN_PASSED, output):
            passed = int(match.group(1))

        if match := re.search(self.PATTERN_FAILED, output):
            failed = int(match.group(1))

        if match := re.search(self.PATTERN_SKIPPED, output):
            skipped = int(match.group(1))

        return passed, failed, skipped


# Service factory function for dependency injection
def create_test_runner(pytest_path: Optional[str] = None) -> TestRunner:
    """
    Factory function to create TestRunner instance.

    WHY: Enables dependency injection and easier testing/mocking.
    PATTERN: Factory Method pattern

    Args:
        pytest_path: Optional custom pytest path

    Returns:
        Configured TestRunner instance

    Example:
        >>> runner = create_test_runner(pytest_path="/custom/pytest")
    """
    return TestRunner(pytest_path=pytest_path)


__all__ = ["TestRunner", "create_test_runner"]
