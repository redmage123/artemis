"""
Module: managers/build_managers/cargo/build_operations.py

WHY: Execute Cargo build, test, and quality operations.
RESPONSIBILITY: Handle all build-related command execution (build, test, check, clippy, fmt, clean).
PATTERNS: Command Pattern, Dispatch Tables, Guard Clauses, Exception Wrapping.

This module contains:
- Build operations (debug/release)
- Test execution
- Quality checks (check, clippy, fmt)
- Clean operations
- Test statistics extraction

EXTRACTED FROM: cargo_manager.py (lines 188-475)
"""

import logging
import re
from pathlib import Path
from typing import Callable, Dict, List, Optional

from artemis_exceptions import wrap_exception
from build_manager_base import BuildResult
from build_system_exceptions import (
    BuildExecutionError,
    TestExecutionError
)


class BuildOperations:
    """
    Handles Cargo build and test operations.

    WHY: Isolate build execution logic from main manager.
    RESPONSIBILITY: Execute build, test, and quality commands.
    """

    def __init__(
        self,
        project_dir: Path,
        execute_command: Callable,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize build operations handler.

        Args:
            project_dir: Project root directory
            execute_command: Command execution function
            logger: Logger instance
        """
        self.project_dir = project_dir
        self.execute_command = execute_command
        self.logger = logger or logging.getLogger(__name__)

    @wrap_exception(BuildExecutionError, "Cargo build failed")
    def build(
        self,
        release: bool = False,
        features: Optional[List[str]] = None,
        all_features: bool = False,
        no_default_features: bool = False,
        target: Optional[str] = None,
        **kwargs
    ) -> BuildResult:
        """
        Build Rust project with Cargo.

        WHY: Compile Rust code with various build configurations.
        RESPONSIBILITY: Construct and execute cargo build command.

        Args:
            release: Build in release mode (optimized)
            features: List of features to enable
            all_features: Enable all features
            no_default_features: Disable default features
            target: Target triple (e.g., "x86_64-unknown-linux-gnu")

        Returns:
            BuildResult

        Raises:
            BuildExecutionError: If build fails

        Example:
            result = ops.build(release=True, features=["full"])
        """
        cmd = ["cargo", "build"]

        # Release mode
        if release:
            cmd.append("--release")

        # Features (guard clause: mutually exclusive options)
        if all_features:
            cmd.append("--all-features")
        elif no_default_features:
            cmd.append("--no-default-features")

        if features:
            cmd.extend(["--features", ",".join(features)])

        # Target
        if target:
            cmd.extend(["--target", target])

        return self.execute_command(
            cmd,
            timeout=600,
            error_type=BuildExecutionError,
            error_message="Cargo build failed"
        )

    @wrap_exception(TestExecutionError, "Cargo tests failed")
    def test(
        self,
        release: bool = False,
        test_name: Optional[str] = None,
        no_fail_fast: bool = False,
        **kwargs
    ) -> BuildResult:
        """
        Run Cargo tests.

        WHY: Execute Rust test suite.
        RESPONSIBILITY: Run tests and extract statistics.

        Args:
            release: Test release build
            test_name: Specific test to run
            no_fail_fast: Run all tests regardless of failures

        Returns:
            BuildResult with test statistics

        Raises:
            TestExecutionError: If tests fail

        Example:
            result = ops.test(test_name="integration_tests")
        """
        cmd = ["cargo", "test"]

        if release:
            cmd.append("--release")

        if no_fail_fast:
            cmd.append("--no-fail-fast")

        if test_name:
            cmd.append(test_name)

        result = self.execute_command(
            cmd,
            timeout=300,
            error_type=TestExecutionError,
            error_message="Cargo test execution failed"
        )

        # Extract test statistics
        if result.success:
            stats = self._extract_test_stats(result.output)
            result.metadata.update(stats)

        return result

    @wrap_exception(BuildExecutionError, "Failed to check project")
    def check(self, all_features: bool = False) -> BuildResult:
        """
        Check project for errors without building.

        WHY: Fast error checking without full compilation.
        RESPONSIBILITY: Run cargo check command.

        Args:
            all_features: Check with all features enabled

        Returns:
            BuildResult

        Raises:
            BuildExecutionError: If check fails

        Example:
            result = ops.check(all_features=True)
        """
        cmd = ["cargo", "check"]

        if all_features:
            cmd.append("--all-features")

        return self.execute_command(
            cmd,
            timeout=120,
            error_type=BuildExecutionError,
            error_message="Cargo check failed"
        )

    @wrap_exception(BuildExecutionError, "Failed to run clippy")
    def clippy(self, fix: bool = False) -> BuildResult:
        """
        Run Clippy linter.

        WHY: Enforce Rust code quality standards.
        RESPONSIBILITY: Execute clippy with optional auto-fix.

        Args:
            fix: Automatically fix warnings

        Returns:
            BuildResult

        Raises:
            BuildExecutionError: If clippy fails

        Example:
            result = ops.clippy(fix=True)
        """
        cmd = ["cargo", "clippy"]

        if fix:
            cmd.append("--fix")

        return self.execute_command(
            cmd,
            timeout=120,
            error_type=BuildExecutionError,
            error_message="Cargo clippy failed"
        )

    @wrap_exception(BuildExecutionError, "Failed to format code")
    def fmt(self, check: bool = False) -> BuildResult:
        """
        Format code with rustfmt.

        WHY: Enforce consistent code formatting.
        RESPONSIBILITY: Execute rustfmt with optional check-only mode.

        Args:
            check: Check formatting without applying

        Returns:
            BuildResult

        Raises:
            BuildExecutionError: If formatting fails

        Example:
            result = ops.fmt(check=True)
        """
        cmd = ["cargo", "fmt"]

        if check:
            cmd.append("--check")

        return self.execute_command(
            cmd,
            timeout=60,
            error_type=BuildExecutionError,
            error_message="Cargo fmt failed"
        )

    def clean(self) -> BuildResult:
        """
        Clean build artifacts.

        WHY: Remove compiled artifacts to free space or force rebuild.
        RESPONSIBILITY: Execute cargo clean command.

        Returns:
            BuildResult

        Example:
            result = ops.clean()
        """
        cmd = ["cargo", "clean"]

        try:
            return self.execute_command(
                cmd,
                timeout=30,
                error_type=BuildExecutionError,
                error_message="Cargo clean failed"
            )
        except BuildExecutionError as e:
            self.logger.warning(f"Clean failed: {e}")
            return BuildResult(
                success=False,
                exit_code=1,
                duration=0.0,
                output=str(e),
                build_system="cargo"
            )

    def _extract_test_stats(self, output: str) -> Dict[str, int]:
        """
        Extract test statistics from Cargo test output.

        WHY: Provide detailed test execution metrics.
        RESPONSIBILITY: Parse test summary from cargo output.

        Args:
            output: Cargo test output

        Returns:
            Dict with test statistics

        Example:
            Input: "test result: ok. 15 passed; 0 failed; 0 ignored"
            Output: {"tests_run": 15, "tests_passed": 15, "tests_failed": 0, "tests_skipped": 0}
        """
        stats = {
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'tests_skipped': 0
        }

        # Cargo test summary: "test result: ok. 15 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out"
        summary_match = re.search(
            r"test result: (\w+)\.\s+(\d+) passed;\s+(\d+) failed;\s+(\d+) ignored",
            output
        )

        if not summary_match:
            return stats

        passed = int(summary_match.group(2))
        failed = int(summary_match.group(3))
        ignored = int(summary_match.group(4))

        stats['tests_passed'] = passed
        stats['tests_failed'] = failed
        stats['tests_skipped'] = ignored
        stats['tests_run'] = passed + failed

        return stats


__all__ = [
    "BuildOperations",
]
