"""
Poetry Build Manager - Build Operations

WHY: Isolate build, test, and script execution operations
RESPONSIBILITY: Execute Poetry build commands, tests, and scripts
PATTERNS: Single Responsibility, Guard Clauses, Regex Patterns

This module handles all Poetry build-related operations including package
building, test execution, script running, and test statistics extraction.
"""

from pathlib import Path
from typing import Optional, Callable, Dict
import re
import logging

from artemis_exceptions import wrap_exception
from build_system_exceptions import (
    BuildExecutionError,
    TestExecutionError
)
from build_manager_base import BuildResult


class BuildOperations:
    """
    Manages Poetry build operations.

    WHY: Centralize all build, test, and execution logic
    RESPONSIBILITY: Execute builds, tests, and custom scripts
    PATTERNS: Single Responsibility, Dependency Injection, Guard Clauses
    """

    def __init__(
        self,
        project_dir: Path,
        execute_command: Callable[..., BuildResult],
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize build operations manager.

        WHY: Inject command executor to decouple from execution details
        PATTERNS: Dependency Injection for testability

        Args:
            project_dir: Project directory path
            execute_command: Command execution callable
            logger: Logger instance
        """
        self.project_dir = project_dir
        self.execute_command = execute_command
        self.logger = logger or logging.getLogger(__name__)

    @wrap_exception(BuildExecutionError, "Poetry build failed")
    def build(self, format: str = "wheel", **kwargs) -> BuildResult:
        """
        Build Python package with Poetry.

        WHY: Create distributable package artifacts
        PATTERNS: Dispatch table pattern for format selection

        Args:
            format: Build format ("wheel", "sdist", or "all")

        Returns:
            BuildResult with build output

        Raises:
            BuildExecutionError: If build fails

        Example:
            result = operations.build(format="wheel")
        """
        cmd = ["poetry", "build"]

        # Format selection dispatch
        format_flags = {
            "wheel": "--format=wheel",
            "sdist": "--format=sdist",
            # "all" builds both by default, no flag needed
        }

        if format in format_flags:
            cmd.append(format_flags[format])

        return self.execute_command(
            cmd,
            timeout=300,
            error_type=BuildExecutionError,
            error_message="Poetry build failed"
        )

    @wrap_exception(TestExecutionError, "Poetry tests failed")
    def test(
        self,
        test_path: Optional[str] = None,
        verbose: bool = False,
        **kwargs
    ) -> BuildResult:
        """
        Run tests with Poetry (uses pytest by default).

        WHY: Execute test suite to verify code quality
        PATTERNS: Boolean flags for operation modes

        Args:
            test_path: Specific test file or directory
            verbose: Verbose output

        Returns:
            BuildResult with test statistics

        Raises:
            TestExecutionError: If tests fail

        Example:
            result = operations.test(verbose=True)
            result = operations.test(test_path="tests/unit")
        """
        cmd = ["poetry", "run", "pytest"]

        if verbose:
            cmd.append("-v")

        if test_path:
            cmd.append(test_path)

        return self.execute_command(
            cmd,
            timeout=300,
            error_type=TestExecutionError,
            error_message="Test execution failed"
        )

    @wrap_exception(BuildExecutionError, "Failed to run Poetry command")
    def run_script(self, script_name: str) -> BuildResult:
        """
        Run a script defined in pyproject.toml.

        WHY: Execute custom project scripts and commands
        PATTERNS: Simple wrapper for script execution

        Args:
            script_name: Script name from [tool.poetry.scripts]

        Returns:
            BuildResult with script output

        Raises:
            BuildExecutionError: If script fails

        Example:
            result = operations.run_script("serve")
        """
        cmd = ["poetry", "run", script_name]

        return self.execute_command(
            cmd,
            timeout=600,
            error_type=BuildExecutionError,
            error_message=f"Script '{script_name}' failed"
        )

    @staticmethod
    def extract_test_stats(output: str) -> Dict[str, int]:
        """
        Extract test statistics from pytest output.

        WHY: Parse test results for reporting and metrics
        PATTERNS: Regex pattern matching, guard clauses

        Args:
            output: pytest output text

        Returns:
            Dictionary with test statistics (run, passed, failed, skipped)

        Example:
            stats = BuildOperations.extract_test_stats(result.output)
        """
        stats = {
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'tests_skipped': 0
        }

        # pytest summary: "5 passed, 2 failed, 1 skipped in 2.34s"
        summary_match = re.search(
            r"(\d+)\s+passed(?:,\s+(\d+)\s+failed)?(?:,\s+(\d+)\s+skipped)?",
            output
        )

        if not summary_match:
            return stats

        passed = int(summary_match.group(1))
        failed = int(summary_match.group(2) or 0)
        skipped = int(summary_match.group(3) or 0)

        stats['tests_passed'] = passed
        stats['tests_failed'] = failed
        stats['tests_skipped'] = skipped
        stats['tests_run'] = passed + failed

        return stats


__all__ = [
    'BuildOperations'
]
