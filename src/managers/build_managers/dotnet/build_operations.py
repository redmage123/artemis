#!/usr/bin/env python3
"""
.NET Build Operations

WHY: Encapsulate all build, test, publish, run, and clean operations.
RESPONSIBILITY: Execute dotnet CLI commands for project lifecycle operations.
PATTERNS: Command pattern, Single Responsibility Principle.

Part of: managers.build_managers.dotnet
Dependencies: None (uses external dotnet CLI)
"""

import re
from pathlib import Path
from typing import Optional, Callable, Any, Dict

from artemis_exceptions import wrap_exception
from build_system_exceptions import (
    BuildExecutionError,
    TestExecutionError
)
from build_manager_base import BuildResult


class BuildOperations:
    """
    Executor for .NET build lifecycle operations.

    WHY: Centralize build/test/publish command construction and execution.
    RESPONSIBILITY: Translate high-level operations to dotnet CLI commands.
    PATTERNS: Command pattern, Strategy pattern for configurations.
    """

    def __init__(
        self,
        target_path: Path,
        is_solution: bool,
        execute_command: Callable,
        logger: Any
    ):
        """
        Initialize build operations executor.

        WHY: Dependency injection for flexibility and testability.

        Args:
            target_path: Path to project or solution file
            is_solution: Whether target is a solution file
            execute_command: Command execution function from BuildManagerBase
            logger: Logger instance

        Guards:
            - target_path must not be None
        """
        if target_path is None:
            raise ValueError("target_path cannot be None")

        self.target_path = target_path
        self.is_solution = is_solution
        self._execute_command = execute_command
        self.logger = logger

    @wrap_exception(BuildExecutionError, ".NET build failed")
    def build(
        self,
        configuration: str = "Debug",
        framework: Optional[str] = None,
        runtime: Optional[str] = None,
        no_restore: bool = False
    ) -> BuildResult:
        """
        Build .NET project or solution.

        WHY: Compile source code to binaries.

        Args:
            configuration: Build configuration (Debug/Release)
            framework: Target framework moniker (net8.0, net6.0, etc.)
            runtime: Runtime identifier (win-x64, linux-x64, etc.)
            no_restore: Skip restoring dependencies

        Returns:
            BuildResult with compilation details

        Raises:
            BuildExecutionError: If build fails

        Guards:
            - configuration must not be empty
        """
        if not configuration:
            configuration = "Debug"

        cmd = ["dotnet", "build", str(self.target_path)]
        cmd.extend(["-c", configuration])

        if framework:
            cmd.extend(["-f", framework])

        if runtime:
            cmd.extend(["-r", runtime])

        if no_restore:
            cmd.append("--no-restore")

        return self._execute_command(
            cmd,
            timeout=600,
            error_type=BuildExecutionError,
            error_message=".NET build failed"
        )

    @wrap_exception(TestExecutionError, ".NET tests failed")
    def test(
        self,
        configuration: str = "Debug",
        no_build: bool = False,
        verbosity: Optional[str] = None,
        filter: Optional[str] = None
    ) -> BuildResult:
        """
        Run .NET unit tests.

        WHY: Execute test suite to verify code correctness.

        Args:
            configuration: Build configuration
            no_build: Skip building before testing
            verbosity: Log verbosity (q[uiet], m[inimal], n[ormal], d[etailed], diag[nostic])
            filter: Test filter expression

        Returns:
            BuildResult with test statistics

        Raises:
            TestExecutionError: If tests fail

        Guards:
            - configuration must not be empty
        """
        if not configuration:
            configuration = "Debug"

        cmd = ["dotnet", "test", str(self.target_path)]
        cmd.extend(["-c", configuration])

        if no_build:
            cmd.append("--no-build")

        if verbosity:
            cmd.extend(["-v", verbosity])

        if filter:
            cmd.extend(["--filter", filter])

        return self._execute_command(
            cmd,
            timeout=300,
            error_type=TestExecutionError,
            error_message=".NET test execution failed"
        )

    @wrap_exception(BuildExecutionError, "Failed to publish")
    def publish(
        self,
        configuration: str = "Release",
        framework: Optional[str] = None,
        runtime: Optional[str] = None,
        output: Optional[str] = None,
        self_contained: bool = False
    ) -> BuildResult:
        """
        Publish .NET application for deployment.

        WHY: Create deployment-ready artifacts with all dependencies.

        Args:
            configuration: Build configuration
            framework: Target framework
            runtime: Runtime identifier
            output: Output directory path
            self_contained: Include .NET runtime in output

        Returns:
            BuildResult with publish details

        Raises:
            BuildExecutionError: If publish fails

        Guards:
            - configuration must not be empty
        """
        if not configuration:
            configuration = "Release"

        cmd = ["dotnet", "publish", str(self.target_path)]
        cmd.extend(["-c", configuration])

        if framework:
            cmd.extend(["-f", framework])

        if runtime:
            cmd.extend(["-r", runtime])

        if output:
            cmd.extend(["-o", output])

        if self_contained:
            cmd.append("--self-contained")

        return self._execute_command(
            cmd,
            timeout=600,
            error_type=BuildExecutionError,
            error_message="Publish failed"
        )

    @wrap_exception(BuildExecutionError, "Failed to run application")
    def run(
        self,
        configuration: str = "Debug",
        framework: Optional[str] = None
    ) -> BuildResult:
        """
        Run .NET application directly.

        WHY: Execute console/web application without explicit build step.

        Args:
            configuration: Build configuration
            framework: Target framework

        Returns:
            BuildResult with run output

        Raises:
            BuildExecutionError: If run fails

        Guards:
            - Cannot run solution files, only projects
        """
        if self.is_solution:
            raise BuildExecutionError(
                "Cannot run solution files. Specify a project.",
                {"target": str(self.target_path)}
            )

        if not configuration:
            configuration = "Debug"

        cmd = ["dotnet", "run", "--project", str(self.target_path)]
        cmd.extend(["-c", configuration])

        if framework:
            cmd.extend(["-f", framework])

        return self._execute_command(
            cmd,
            timeout=600,
            error_type=BuildExecutionError,
            error_message="Application run failed"
        )

    def clean(self) -> BuildResult:
        """
        Clean build outputs (bin/obj directories).

        WHY: Remove intermediate and output files for fresh build.

        Returns:
            BuildResult (always succeeds, logs warnings on failure)
        """
        cmd = ["dotnet", "clean", str(self.target_path)]

        try:
            return self._execute_command(
                cmd,
                timeout=30,
                error_type=BuildExecutionError,
                error_message="Clean failed"
            )
        except BuildExecutionError as e:
            self.logger.warning(f"Clean failed: {e}")
            return BuildResult(
                success=False,
                exit_code=1,
                duration=0.0,
                output=str(e),
                build_system="dotnet"
            )

    @staticmethod
    def extract_test_stats(output: str) -> Dict[str, int]:
        """
        Parse test statistics from dotnet test output.

        WHY: Provide structured test results for reporting.

        Args:
            output: Raw dotnet test command output

        Returns:
            Dictionary with test counts (run, passed, failed, skipped)

        Example output:
            "Passed!  - Failed:     0, Passed:    15, Skipped:     0, Total:    15"
            "Failed!  - Failed:     2, Passed:    13, Skipped:     1, Total:    16"
        """
        stats = {
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'tests_skipped': 0
        }

        summary_match = re.search(
            r'Failed:\s+(\d+),\s+Passed:\s+(\d+),\s+Skipped:\s+(\d+),\s+Total:\s+(\d+)',
            output
        )

        if not summary_match:
            return stats

        failed = int(summary_match.group(1))
        passed = int(summary_match.group(2))
        skipped = int(summary_match.group(3))
        total = int(summary_match.group(4))

        stats['tests_failed'] = failed
        stats['tests_passed'] = passed
        stats['tests_skipped'] = skipped
        stats['tests_run'] = total - skipped

        return stats


__all__ = ["BuildOperations"]
