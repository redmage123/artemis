#!/usr/bin/env python3
"""
WHY: Execute CMake tests using CTest
RESPONSIBILITY: Run test suite and report results
PATTERNS: Test Runner, Command Builder

Test runner executes CTest to validate build quality.
"""

from pathlib import Path
import multiprocessing
from artemis_exceptions import wrap_exception
from build_system_exceptions import TestExecutionError
from build_manager_base import BuildResult


class CMakeTestRunner:
    """
    Runs CMake tests using CTest.

    WHY: Validates build quality through automated testing.
    PATTERNS: Test runner pattern.
    """

    @wrap_exception(TestExecutionError, "Tests failed")
    def test(
        self,
        build_dir: Path,
        execute_fn,
        verbose: bool = False,
        parallel: bool = True
    ) -> BuildResult:
        """
        Run CMake tests using CTest.

        WHY: Executes test suite to validate functionality.

        Args:
            build_dir: Build directory
            execute_fn: Function to execute ctest
            verbose: Verbose output
            parallel: Run tests in parallel

        Returns:
            BuildResult with test statistics

        Raises:
            TestExecutionError: If tests fail

        Example:
            >>> runner.test(Path("build"), execute_fn, verbose=True)
        """
        cmd = self._build_test_command(build_dir, verbose, parallel)

        return execute_fn(
            cmd,
            timeout=300,
            error_type=TestExecutionError,
            error_message="CTest execution failed"
        )

    def _build_test_command(
        self,
        build_dir: Path,
        verbose: bool,
        parallel: bool
    ) -> list:
        """
        Build ctest command.

        WHY: Centralizes command construction.

        Args:
            build_dir: Build directory
            verbose: Verbose flag
            parallel: Parallel flag

        Returns:
            Command list
        """
        cmd = ["ctest", "--test-dir", str(build_dir)]

        if verbose:
            cmd.append("--verbose")

        if parallel:
            cpu_count = multiprocessing.cpu_count()
            cmd.extend(["--parallel", str(cpu_count)])

        return cmd
