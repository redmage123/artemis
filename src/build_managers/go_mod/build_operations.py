"""
Go Build Operations

WHY: Dedicated module for build, test, and code quality operations
RESPONSIBILITY: Handle all Go build, test, fmt, vet, and clean operations
PATTERNS: Single Responsibility, command builder, dispatch table
"""

import re
import logging
from typing import Optional, List, Dict, Callable, Any

from artemis_exceptions import wrap_exception
from build_system_exceptions import (
    BuildExecutionError,
    TestExecutionError
)
from build_manager_base import BuildResult


class GoBuildOperations:
    """
    WHY: Centralize all build and test operations
    RESPONSIBILITY: Execute build, test, fmt, vet, clean commands
    PATTERNS: Single Responsibility, dependency injection, command builder
    """

    def __init__(
        self,
        execute_command: Callable[..., BuildResult],
        logger: Optional[logging.Logger] = None
    ):
        """
        WHY: Inject command executor for testability
        RESPONSIBILITY: Initialize with required dependencies
        PATTERNS: Dependency injection

        Args:
            execute_command: Command execution function
            logger: Logger instance
        """
        self.execute_command = execute_command
        self.logger = logger or logging.getLogger(__name__)

    @wrap_exception(BuildExecutionError, "Go build failed")
    def build(
        self,
        output: Optional[str] = None,
        tags: Optional[List[str]] = None,
        ldflags: Optional[str] = None,
        race: bool = False,
        goos: Optional[str] = None,
        goarch: Optional[str] = None
    ) -> BuildResult:
        """
        WHY: Build Go project with configurable options
        RESPONSIBILITY: Construct and execute go build command
        PATTERNS: Guard clauses, command builder, environment variables

        Args:
            output: Output binary name
            tags: Build tags
            ldflags: Linker flags
            race: Enable race detector
            goos: Target OS (GOOS)
            goarch: Target architecture (GOARCH)

        Returns:
            BuildResult

        Raises:
            BuildExecutionError: If build fails
        """
        cmd = ["go", "build"]

        if output:
            cmd.extend(["-o", output])

        if tags:
            cmd.extend(["-tags", ",".join(tags)])

        if ldflags:
            cmd.extend(["-ldflags", ldflags])

        if race:
            cmd.append("-race")

        # Set environment variables for cross-compilation
        env = self._build_cross_compile_env(goos, goarch)

        return self.execute_command(
            cmd,
            timeout=600,
            error_type=BuildExecutionError,
            error_message="Go build failed",
            env=env if env else None
        )

    @wrap_exception(TestExecutionError, "Go tests failed")
    def test(
        self,
        package: Optional[str] = None,
        verbose: bool = False,
        race: bool = False,
        cover: bool = False,
        bench: bool = False
    ) -> BuildResult:
        """
        WHY: Run Go tests with various options
        RESPONSIBILITY: Construct and execute go test command
        PATTERNS: Guard clauses, command builder

        Args:
            package: Specific package to test (default: ./...)
            verbose: Verbose output
            race: Enable race detector
            cover: Enable coverage
            bench: Run benchmarks

        Returns:
            BuildResult with test statistics

        Raises:
            TestExecutionError: If tests fail
        """
        cmd = ["go", "test"]

        if verbose:
            cmd.append("-v")

        if race:
            cmd.append("-race")

        if cover:
            cmd.append("-cover")

        if bench:
            cmd.append("-bench=.")

        # Default to all packages
        cmd.append(package if package else "./...")

        return self.execute_command(
            cmd,
            timeout=300,
            error_type=TestExecutionError,
            error_message="Go test execution failed"
        )

    @wrap_exception(BuildExecutionError, "Failed to run go fmt")
    def fmt(self) -> BuildResult:
        """
        WHY: Format Go code according to standard conventions
        RESPONSIBILITY: Execute 'go fmt'
        PATTERNS: Simple command execution

        Returns:
            BuildResult

        Raises:
            BuildExecutionError: If formatting fails
        """
        cmd = ["go", "fmt", "./..."]

        return self.execute_command(
            cmd,
            timeout=60,
            error_type=BuildExecutionError,
            error_message="go fmt failed"
        )

    @wrap_exception(BuildExecutionError, "Failed to run go vet")
    def vet(self) -> BuildResult:
        """
        WHY: Run static analysis on Go code
        RESPONSIBILITY: Execute 'go vet' for suspicious code detection
        PATTERNS: Simple command execution

        Returns:
            BuildResult

        Raises:
            BuildExecutionError: If vet fails
        """
        cmd = ["go", "vet", "./..."]

        return self.execute_command(
            cmd,
            timeout=120,
            error_type=BuildExecutionError,
            error_message="go vet failed"
        )

    def clean(self) -> BuildResult:
        """
        WHY: Clean build cache to free disk space
        RESPONSIBILITY: Execute 'go clean -cache'
        PATTERNS: Exception handling with fallback

        Returns:
            BuildResult
        """
        cmd = ["go", "clean", "-cache"]

        try:
            return self.execute_command(
                cmd,
                timeout=30,
                error_type=BuildExecutionError,
                error_message="go clean failed"
            )
        except BuildExecutionError as e:
            self.logger.warning(f"Clean failed: {e}")
            return BuildResult(
                success=False,
                exit_code=1,
                duration=0.0,
                output=str(e),
                build_system="go"
            )

    @staticmethod
    def _build_cross_compile_env(
        goos: Optional[str],
        goarch: Optional[str]
    ) -> Optional[Dict[str, str]]:
        """
        WHY: Build environment variables for cross-compilation
        RESPONSIBILITY: Create env dict with GOOS/GOARCH
        PATTERNS: Guard clause, dictionary builder

        Args:
            goos: Target operating system
            goarch: Target architecture

        Returns:
            Environment dict or None
        """
        if not goos and not goarch:
            return None

        env = {}

        if goos:
            env["GOOS"] = goos

        if goarch:
            env["GOARCH"] = goarch

        return env

    @staticmethod
    def extract_test_stats(output: str) -> Dict[str, int]:
        """
        WHY: Parse test results from Go test output
        RESPONSIBILITY: Extract test statistics
        PATTERNS: Regex parsing, static method

        Args:
            output: Go test output

        Returns:
            Dict with test statistics
        """
        stats = {
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'tests_skipped': 0
        }

        # Count test results from Go test markers
        passed = len(re.findall(r'--- PASS:', output))
        failed = len(re.findall(r'--- FAIL:', output))
        skipped = len(re.findall(r'--- SKIP:', output))

        stats['tests_passed'] = passed
        stats['tests_failed'] = failed
        stats['tests_skipped'] = skipped
        stats['tests_run'] = passed + failed

        return stats
