"""
NPM Build Manager - Build Operations

WHY: Execute build, test, and script operations
RESPONSIBILITY: Handle build execution, testing, and cleanup
PATTERNS: Command pattern, Strategy pattern, Guard clauses

This module manages all build-related operations including builds,
tests, script execution, and cleanup.
"""

from pathlib import Path
from typing import Optional, Callable, Dict, List
import logging
import shutil
import re

from artemis_exceptions import wrap_exception
from build_system_exceptions import (
    BuildExecutionError,
    TestExecutionError
)
from build_manager_base import BuildResult

from .models import PackageManager


class BuildOperations:
    """
    Execute build and test operations.

    WHY: Centralize build execution logic
    RESPONSIBILITY: Run builds, tests, scripts, and cleanup
    PATTERNS: Command pattern, Strategy pattern, Template method

    This class handles all build-related operations with support for
    different package managers and test frameworks.
    """

    def __init__(
        self,
        project_dir: Path,
        execute_command: Callable[..., BuildResult],
        package_manager: PackageManager,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize build operations.

        WHY: Setup dependencies for build execution
        PATTERNS: Dependency injection

        Args:
            project_dir: Project directory
            execute_command: Command executor function
            package_manager: Package manager to use
            logger: Logger instance
        """
        self.project_dir = project_dir
        self.execute_command = execute_command
        self.package_manager = package_manager
        self.logger = logger or logging.getLogger(__name__)

    @wrap_exception(BuildExecutionError, "Build failed")
    def build(
        self,
        script_name: str = "build",
        production: bool = False,
        timeout: int = 600
    ) -> BuildResult:
        """
        Run npm build script.

        WHY: Execute build scripts from package.json
        PATTERNS: Command pattern, Guard clauses

        Args:
            script_name: Script name from package.json (default: "build")
            production: Build for production
            timeout: Build timeout in seconds

        Returns:
            BuildResult

        Raises:
            BuildExecutionError: If build fails

        Example:
            result = ops.build(script_name="build:prod", production=True)
        """
        # Build command
        cmd = [self.package_manager.value, "run", script_name]

        # Add production flag for npm
        if production and self.package_manager == PackageManager.NPM:
            cmd.append("--production")

        return self.execute_command(
            cmd,
            timeout=timeout,
            error_type=BuildExecutionError,
            error_message=f"{script_name} script failed"
        )

    @wrap_exception(TestExecutionError, "Tests failed")
    def test(
        self,
        watch: bool = False,
        coverage: bool = False,
        timeout: int = 300
    ) -> BuildResult:
        """
        Run npm test.

        WHY: Execute test suite with coverage and reporting
        PATTERNS: Command pattern, Guard clauses

        Args:
            watch: Run in watch mode (not supported with subprocess)
            coverage: Generate coverage report
            timeout: Test timeout in seconds

        Returns:
            BuildResult with test statistics

        Raises:
            TestExecutionError: If tests fail

        Example:
            result = ops.test(coverage=True)
        """
        cmd = [self.package_manager.value, "test"]

        # Coverage flag
        if coverage:
            cmd.append("--coverage")

        # Watch mode not supported in subprocess
        if watch:
            self.logger.warning("Watch mode not supported in automated execution")

        return self.execute_command(
            cmd,
            timeout=timeout,
            error_type=TestExecutionError,
            error_message="Test execution failed"
        )

    @wrap_exception(BuildExecutionError, "Script execution failed")
    def run_script(self, script_name: str, timeout: int = 300) -> BuildResult:
        """
        Run a script from package.json.

        WHY: Execute custom scripts defined in package.json
        PATTERNS: Command pattern

        Args:
            script_name: Script name from package.json
            timeout: Script timeout in seconds

        Returns:
            BuildResult

        Raises:
            BuildExecutionError: If script fails

        Example:
            result = ops.run_script("lint")
        """
        cmd = [self.package_manager.value, "run", script_name]

        return self.execute_command(
            cmd,
            timeout=timeout,
            error_type=BuildExecutionError,
            error_message=f"Script '{script_name}' failed"
        )

    def clean(self) -> BuildResult:
        """
        Clean build artifacts and node_modules.

        WHY: Remove build artifacts for fresh build
        PATTERNS: Template method for cleanup steps

        Returns:
            BuildResult
        """
        # Remove node_modules
        node_modules = self.project_dir / "node_modules"
        if node_modules.exists():
            self.logger.info("Removing node_modules...")
            shutil.rmtree(node_modules)

        # Remove common build directories
        self._clean_build_directories()

        return BuildResult(
            success=True,
            exit_code=0,
            duration=0.0,
            output="Clean completed",
            build_system="npm"
        )

    def _clean_build_directories(self) -> None:
        """
        Remove common build directories.

        WHY: Clean framework-specific build artifacts
        PATTERNS: Guard clauses for existence checks
        """
        build_dirs = ["dist", "build", "out", ".next", ".nuxt"]

        for build_dir in build_dirs:
            path = self.project_dir / build_dir

            if not path.exists():
                continue
            if not path.is_dir():
                continue

            self.logger.info(f"Removing {build_dir}...")
            shutil.rmtree(path)

    def extract_test_stats(self, output: str) -> Dict[str, int]:
        """
        Extract test statistics from Jest/Mocha output.

        WHY: Parse test results for reporting
        PATTERNS: Strategy pattern for different test frameworks

        Args:
            output: Test output

        Returns:
            Dict with test statistics
        """
        stats = {
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'tests_skipped': 0
        }

        # Try Jest pattern first
        jest_stats = self._parse_jest_output(output)
        if jest_stats['tests_run'] > 0:
            return jest_stats

        # Try Mocha pattern
        mocha_stats = self._parse_mocha_output(output)
        if mocha_stats['tests_run'] > 0:
            return mocha_stats

        return stats

    def _parse_jest_output(self, output: str) -> Dict[str, int]:
        """
        Parse Jest test output.

        WHY: Extract test statistics from Jest format
        PATTERNS: Regular expression parsing

        Args:
            output: Test output

        Returns:
            Dictionary with test statistics
        """
        # Jest output pattern:
        # "Tests:       5 passed, 5 total"
        pattern = r"Tests:\s+(?:(\d+)\s+failed,\s+)?(?:(\d+)\s+passed,\s+)?(?:(\d+)\s+skipped,\s+)?(\d+)\s+total"
        match = re.search(pattern, output)

        if not match:
            return {
                'tests_run': 0,
                'tests_passed': 0,
                'tests_failed': 0,
                'tests_skipped': 0
            }

        failed = int(match.group(1) or 0)
        passed = int(match.group(2) or 0)
        skipped = int(match.group(3) or 0)
        total = int(match.group(4) or 0)

        return {
            'tests_run': total,
            'tests_passed': passed,
            'tests_failed': failed,
            'tests_skipped': skipped
        }

    def _parse_mocha_output(self, output: str) -> Dict[str, int]:
        """
        Parse Mocha test output.

        WHY: Extract test statistics from Mocha format
        PATTERNS: Regular expression parsing

        Args:
            output: Test output

        Returns:
            Dictionary with test statistics
        """
        # Mocha output patterns:
        # "5 passing"
        # "2 failing"
        passing_match = re.search(r"(\d+)\s+passing", output)
        failing_match = re.search(r"(\d+)\s+failing", output)

        passed = int(passing_match.group(1)) if passing_match else 0
        failed = int(failing_match.group(1)) if failing_match else 0

        return {
            'tests_run': passed + failed,
            'tests_passed': passed,
            'tests_failed': failed,
            'tests_skipped': 0
        }


__all__ = [
    'BuildOperations'
]
