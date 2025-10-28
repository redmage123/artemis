#!/usr/bin/env python3
"""
Bash Manager - Core Orchestration

WHY: Coordinate specialized components following Template Method pattern
RESPONSIBILITY: Implement BuildManagerBase interface with component delegation
PATTERNS: Template Method, Facade, Composition over Inheritance

This module provides the main BashManager class that inherits from
BuildManagerBase and delegates operations to specialized components.
"""

from pathlib import Path
from typing import Dict, List, Optional
import subprocess
import logging

from build_manager_base import BuildManagerBase, BuildResult
from build_manager_factory import register_build_manager, BuildSystem
from build_system_exceptions import BuildSystemNotFoundError

from .models import (
    QualityCheckConfig,
    ShellDialect,
    BashProjectMetadata
)
from .script_detector import ScriptDetector
from .linter import ShellcheckLinter
from .formatter import ShfmtFormatter
from .test_runner import BatsTestRunner


@register_build_manager(BuildSystem.BASH)
class BashManager(BuildManagerBase):
    """
    Manages bash shell script projects.

    WHY: Bring shell scripts into modern CI/CD with quality gates
    RESPONSIBILITY: Orchestrate quality checks via component delegation
    PATTERNS: Facade, Template Method, Composition over Inheritance

    This manager coordinates specialized components:
    - ScriptDetector: Find shell scripts
    - ShellcheckLinter: Static analysis
    - ShfmtFormatter: Format checking
    - BatsTestRunner: Test execution

    Integration: Registered with BuildManagerFactory as BuildSystem.BASH
    """

    def __init__(self, project_dir: Path):
        """
        Initialize Bash manager.

        WHY: Set up component delegation pattern
        PATTERNS: Dependency Injection, Template Method (super().__init__)

        Args:
            project_dir: Root directory containing shell scripts

        Raises:
            BuildException: If initialization fails (wrapped by decorator)
        """
        super().__init__(project_dir)

        # Initialize configuration
        self.config = QualityCheckConfig(
            shell_dialect=ShellDialect.BASH,
            enable_shellcheck=True,
            enable_shfmt=True
        )

        # Initialize component managers
        self._init_components()

    def _init_components(self) -> None:
        """
        Initialize specialized component managers.

        WHY: Centralize component initialization with dependency injection
        PATTERNS: Dependency Injection, Composition
        """
        # Script detector
        self.detector = ScriptDetector(
            project_dir=self.project_dir,
            logger=self.logger
        )

        # Discover scripts once during initialization
        self.shell_scripts = self.detector.detect_scripts()

        # Linter
        self.linter = ShellcheckLinter(
            config=self.config,
            execute_command=self._execute_command_wrapper,
            logger=self.logger
        )

        # Formatter
        self.formatter = ShfmtFormatter(
            config=self.config,
            execute_command=self._execute_command_wrapper,
            logger=self.logger
        )

        # Test runner
        self.test_runner = BatsTestRunner(
            project_dir=self.project_dir,
            execute_command=self._execute_command_wrapper,
            logger=self.logger
        )

    def _validate_installation(self) -> None:
        """
        Validate shellcheck, shfmt, and bats are installed.

        WHY: BuildManagerBase requires validation of tools
        RESPONSIBILITY: Check required tools are available
        PATTERNS: Template Method (required by base class)

        Raises:
            BuildSystemNotFoundError: If required tools not in PATH

        Note: Only checks shellcheck; shfmt and bats are optional
        """
        # Check shellcheck (required for build)
        try:
            result = subprocess.run(
                ["shellcheck", "--version"],
                capture_output=True,
                timeout=5
            )
            if result.returncode != 0:
                raise BuildSystemNotFoundError("shellcheck not found in PATH")
        except FileNotFoundError:
            raise BuildSystemNotFoundError("shellcheck not found in PATH")
        except subprocess.TimeoutExpired:
            self.logger.warning("shellcheck version check timed out")

        # Log optional tools status
        for tool in ["shfmt", "bats"]:
            try:
                subprocess.run(
                    [tool, "--version"],
                    capture_output=True,
                    timeout=5
                )
                self.logger.debug(f"{tool} is available")
            except FileNotFoundError:
                self.logger.warning(f"{tool} not found (optional)")

    def _validate_project(self) -> None:
        """
        Validate project has shell scripts.

        WHY: BuildManagerBase requires project validation
        RESPONSIBILITY: Ensure project is valid bash project
        PATTERNS: Template Method (required by base class)

        Note: Validation is lenient - any .sh files make it valid
        """
        # No strict validation needed - detection handles this
        # This allows initialization even for empty directories
        pass

    def _execute_command_wrapper(self, cmd: List[str]) -> subprocess.CompletedProcess:
        """
        Wrapper to adapt _run_command to component interface.

        WHY: Bridge between BuildManagerBase interface and component needs
        RESPONSIBILITY: Adapt command execution interface
        PATTERNS: Adapter Pattern

        Args:
            cmd: Command arguments

        Returns:
            subprocess.CompletedProcess

        Raises:
            subprocess.SubprocessError: On execution failure
        """
        # Run command and capture output
        result = subprocess.run(
            cmd,
            cwd=self.project_dir,
            capture_output=True,
            text=True
        )
        return result

    @property
    def name(self) -> str:
        """
        Get build manager name.

        WHY: Identifies this manager in logs and error messages
        RESPONSIBILITY: Return constant identifier
        PATTERNS: Template Method (required by base class)

        Returns:
            str: Always returns "bash"
        """
        return "bash"

    def detect(self) -> bool:
        """
        Detect if this is a bash/shell script project.

        WHY: Auto-detection for repository classification
        RESPONSIBILITY: Delegate to detector component
        PATTERNS: Delegation, Guard Clauses

        Returns:
            bool: True if any .sh files exist in project tree

        Edge cases:
            - Empty directories return False
            - Mixed-language projects return True if any .sh files exist
        """
        return self.detector.has_scripts()

    def install_dependencies(self) -> bool:
        """
        Install dependencies (no-op for bash).

        WHY: Template Method pattern requires this method
        RESPONSIBILITY: No-op for shell scripts (no package manager)
        PATTERNS: Template Method, Null Object Pattern

        Returns:
            bool: Always True

        Note: Could be enhanced to check for required commands
        """
        self.logger.debug("No dependency installation needed for bash projects")
        return True

    def build(self, **kwargs) -> BuildResult:
        """
        Lint and format-check all shell scripts.

        WHY: "Build" for scripts means quality checks
        RESPONSIBILITY: Coordinate linting and formatting via delegation
        PATTERNS: Facade, Delegation, Guard Clauses

        What it does:
            1. Run shellcheck on all scripts (static analysis)
            2. Run shfmt on all scripts (format verification)

        Args:
            **kwargs: Ignored (for base class compatibility)

        Returns:
            BuildResult with quality check outcome

        Edge cases:
            - Returns success if no scripts found (shouldn't happen after detect())
            - Continues checking all scripts even if some fail
        """
        import time
        start_time = time.time()

        # Guard: No scripts to check
        if not self.shell_scripts:
            self.logger.warning("No shell scripts found to build")
            return BuildResult(
                success=True,
                exit_code=0,
                duration=time.time() - start_time,
                output="No scripts to check",
                build_system="bash"
            )

        all_passed = True
        errors = []
        warnings = []

        # Lint all scripts
        self.logger.info("Running shellcheck linter...")
        lint_results = self.linter.lint_scripts(self.shell_scripts)
        if not self.linter.all_passed(lint_results):
            all_passed = False
            for result in lint_results:
                if not result.passed:
                    errors.extend(result.errors)
                    warnings.extend(result.warnings)

        # Format check all scripts
        self.logger.info("Running shfmt format check...")
        format_results = self.formatter.check_formats(self.shell_scripts)
        if not self.formatter.all_formatted(format_results):
            all_passed = False
            for result in format_results:
                if result.needs_formatting:
                    warnings.append(f"{result.script.name} needs formatting")

        # Summary
        duration = time.time() - start_time
        if all_passed:
            self.logger.info("All quality checks passed")
        else:
            self.logger.warning("Some quality checks failed")

        return BuildResult(
            success=all_passed,
            exit_code=0 if all_passed else 1,
            duration=duration,
            output=f"Checked {len(self.shell_scripts)} script(s)",
            build_system="bash",
            errors=errors,
            warnings=warnings
        )

    def test(self, **kwargs) -> BuildResult:
        """
        Run bats (Bash Automated Testing System) test suite.

        WHY: BuildManagerBase requires test() method
        RESPONSIBILITY: Delegate to test runner component
        PATTERNS: Delegation, Guard Clauses, Template Method

        Args:
            **kwargs: Ignored (for base class compatibility)

        Returns:
            BuildResult with test outcome

        Edge cases:
            - Returns success if no tests exist (legacy projects)
            - Returns failure if bats not installed
        """
        test_result = self.test_runner.run_tests()

        # Log test summary
        if test_result.tests_run > 0:
            self.logger.info(
                f"Tests: {test_result.tests_passed}/{test_result.tests_run} passed "
                f"in {test_result.duration:.2f}s"
            )

        return BuildResult(
            success=test_result.passed,
            exit_code=test_result.exit_code,
            duration=test_result.duration,
            output=test_result.output,
            build_system="bash",
            tests_run=test_result.tests_run,
            tests_passed=test_result.tests_passed,
            tests_failed=test_result.tests_failed,
            tests_skipped=test_result.tests_skipped
        )

    def run_tests(self) -> bool:
        """
        Legacy method for backward compatibility.

        WHY: Maintain backward compatibility with old API
        RESPONSIBILITY: Delegate to test() and return boolean
        PATTERNS: Adapter Pattern

        Returns:
            bool: True if tests pass or don't exist, False if tests fail

        Deprecated: Use test() instead for BuildResult
        """
        result = self.test()
        return result.success

    def clean(self) -> bool:
        """
        Clean build artifacts (no-op for bash).

        WHY: Template Method pattern requires this method
        RESPONSIBILITY: No-op for shell scripts (no artifacts)
        PATTERNS: Template Method, Null Object Pattern

        Returns:
            bool: Always True

        Note: Could be enhanced to clean test artifacts
        """
        self.logger.debug("No cleanup needed for bash projects")
        return True

    def get_metadata(self) -> Dict:
        """
        Extract bash project metadata.

        WHY: Provide project analysis and reporting data
        RESPONSIBILITY: Build metadata snapshot from components
        PATTERNS: Facade, Builder Pattern

        Returns:
            Dict: Project metadata including:
                - manager: "bash"
                - shell_scripts: List of script paths
                - has_tests: Boolean test presence
                - script_count: Total script count
                - total_size_bytes: Combined size

        Edge cases:
            - Empty list if no scripts (shouldn't happen after detect())
            - has_tests=false for projects without test directory
        """
        # Calculate total size
        total_size = sum(script.size_bytes for script in self.shell_scripts)

        # Find test directory
        test_dir = self.test_runner.find_test_directory()

        # Build metadata object
        metadata = BashProjectMetadata(
            manager="bash",
            scripts=self.shell_scripts,
            has_tests=test_dir is not None,
            test_directory=test_dir,
            total_size_bytes=total_size
        )

        # Convert to dict for backward compatibility
        return metadata.to_dict()

    def get_project_info(self) -> Dict:
        """
        Get project information (alias for get_metadata).

        WHY: BuildManagerBase requires get_project_info() method
        RESPONSIBILITY: Return project metadata
        PATTERNS: Adapter Pattern, Template Method

        Returns:
            Dict: Project information (same as get_metadata())

        Note: This is an adapter for BuildManagerBase compatibility
        """
        return self.get_metadata()


__all__ = [
    'BashManager'
]
