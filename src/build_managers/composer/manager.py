#!/usr/bin/env python3
"""
Composer Build Manager (PHP)

WHY: Enterprise-grade PHP dependency management using Composer
RESPONSIBILITY: Orchestrate all Composer operations via specialized components
PATTERNS:
- Template Method: Inherits from BuildManagerBase
- Facade pattern: Delegates to specialized managers
- Composition over inheritance: Uses component managers
"""

from pathlib import Path
from typing import Dict, Optional, Any
import logging

from artemis_exceptions import wrap_exception
from build_system_exceptions import (
    BuildSystemNotFoundError,
    ProjectConfigurationError,
    BuildExecutionError,
    TestExecutionError,
    DependencyInstallError
)
from build_manager_base import BuildManagerBase, BuildResult
from build_manager_factory import register_build_manager, BuildSystem

from .parser import ComposerParser
from .dependency_manager import DependencyManager
from .autoloader import AutoloaderManager
from .version_detector import VersionDetector
from .test_runner import TestRunner


@register_build_manager(BuildSystem.COMPOSER)
class ComposerManager(BuildManagerBase):
    """
    Enterprise-grade Composer manager for PHP projects.

    WHY: Unified interface for all Composer operations
    RESPONSIBILITY: Coordinate specialized managers for parsing, dependencies, testing, etc.
    PATTERNS:
    - Facade: Provides simple interface to complex subsystems
    - Delegation: Delegates specific tasks to specialized managers

    Example:
        composer = ComposerManager(project_dir="/path/to/project")
        result = composer.install()
        test_result = composer.test()
    """

    def __init__(
        self,
        project_dir: Optional[Path] = None,
        logger: Optional['logging.Logger'] = None
    ):
        """
        Initialize Composer manager.

        WHY: Set up manager and initialize components
        RESPONSIBILITY: Create and wire specialized component managers

        Args:
            project_dir: Project directory (contains composer.json)
            logger: Logger instance

        Raises:
            BuildSystemNotFoundError: If Composer not found
            ProjectConfigurationError: If composer.json invalid
        """
        # Store paths before calling super().__init__
        self.composer_json_path = None
        self.composer_lock_path = None

        # Initialize base class
        super().__init__(project_dir, logger)

        # Initialize component managers
        self._initialize_components()

    def _initialize_components(self) -> None:
        """
        Initialize specialized component managers.

        WHY: Separate initialization logic for clarity
        RESPONSIBILITY: Create and configure all component managers
        """
        self.parser = ComposerParser(self.project_dir)
        self.dependency_manager = DependencyManager(
            self.project_dir,
            self._execute_command,
            self.logger
        )
        self.autoloader_manager = AutoloaderManager(
            self.project_dir,
            self._execute_command,
            self.logger
        )
        self.version_detector = VersionDetector(
            self._execute_command,
            self.logger
        )
        self.test_runner = TestRunner(
            self.project_dir,
            self._execute_command,
            self.parser,
            self.logger
        )

        # Update paths after parser initialization
        self.composer_json_path = self.parser.composer_json_path
        self.composer_lock_path = self.parser.composer_lock_path

    @wrap_exception(BuildSystemNotFoundError, "Composer not found")
    def _validate_installation(self) -> None:
        """
        Validate Composer is installed.

        WHY: Ensure Composer availability before operations
        RESPONSIBILITY: Detect and log Composer version

        Raises:
            BuildSystemNotFoundError: If Composer not in PATH
        """
        version = self.version_detector.detect_composer_version()
        self.logger.info(f"Using Composer version: {version}")

    @wrap_exception(ProjectConfigurationError, "Invalid Composer project")
    def _validate_project(self) -> None:
        """
        Validate composer.json exists.

        WHY: Ensure project is properly configured
        RESPONSIBILITY: Check for composer.json presence

        Raises:
            ProjectConfigurationError: If composer.json missing
        """
        if not self.parser.composer_json_path.exists():
            raise ProjectConfigurationError(
                "composer.json not found",
                {"project_dir": str(self.project_dir)}
            )

    @wrap_exception(ProjectConfigurationError, "Failed to parse composer.json")
    def get_project_info(self) -> Dict[str, Any]:
        """
        Parse composer.json for project information.

        WHY: Provide access to project metadata
        RESPONSIBILITY: Delegate to parser component

        Returns:
            Dict with project information

        Raises:
            ProjectConfigurationError: If composer.json malformed
        """
        return self.parser.get_project_info()

    @wrap_exception(BuildExecutionError, "Composer install failed")
    def build(self, **kwargs) -> BuildResult:
        """
        Install dependencies (alias for install).

        WHY: Provide standard build interface
        RESPONSIBILITY: Delegate to install method

        Returns:
            BuildResult

        Raises:
            BuildExecutionError: If install fails

        Example:
            result = composer.build()
        """
        return self.install(**kwargs)

    @wrap_exception(DependencyInstallError, "Failed to install dependencies")
    def install(
        self,
        no_dev: bool = False,
        optimize_autoloader: bool = False,
        prefer_dist: bool = False,
        **kwargs
    ) -> BuildResult:
        """
        Install all dependencies from composer.json.

        WHY: Install project dependencies
        RESPONSIBILITY: Delegate to dependency manager

        Args:
            no_dev: Skip dev dependencies
            optimize_autoloader: Optimize autoloader
            prefer_dist: Prefer dist over source

        Returns:
            BuildResult

        Raises:
            DependencyInstallError: If installation fails

        Example:
            composer.install(no_dev=True, optimize_autoloader=True)
        """
        return self.dependency_manager.install(
            no_dev=no_dev,
            optimize_autoloader=optimize_autoloader,
            prefer_dist=prefer_dist
        )

    @wrap_exception(TestExecutionError, "Tests failed")
    def test(
        self,
        test_path: Optional[str] = None,
        verbose: bool = False,
        **kwargs
    ) -> BuildResult:
        """
        Run tests with PHPUnit via composer.

        WHY: Execute test suite
        RESPONSIBILITY: Delegate to test runner

        Args:
            test_path: Specific test file or directory
            verbose: Verbose output

        Returns:
            BuildResult with test statistics

        Raises:
            TestExecutionError: If tests fail

        Example:
            result = composer.test(verbose=True)
        """
        return self.test_runner.run_tests(
            test_path=test_path,
            verbose=verbose
        )

    @wrap_exception(DependencyInstallError, "Failed to add package")
    def install_dependency(
        self,
        package: str,
        version: Optional[str] = None,
        dev: bool = False,
        **kwargs
    ) -> bool:
        """
        Add a package to composer.json.

        WHY: Add new dependencies to project
        RESPONSIBILITY: Delegate to dependency manager

        Args:
            package: Package name
            version: Package version (optional)
            dev: Add as dev dependency

        Returns:
            True if successful

        Raises:
            DependencyInstallError: If installation fails

        Example:
            composer.install_dependency("symfony/console", version="^6.0")
            composer.install_dependency("phpunit/phpunit", dev=True)
        """
        return self.dependency_manager.require_package(
            package=package,
            version=version,
            dev=dev
        )

    @wrap_exception(BuildExecutionError, "Failed to update dependencies")
    def update(
        self,
        package: Optional[str] = None,
        with_dependencies: bool = True,
        **kwargs
    ) -> BuildResult:
        """
        Update dependencies.

        WHY: Keep dependencies current
        RESPONSIBILITY: Delegate to dependency manager

        Args:
            package: Specific package to update (None = all)
            with_dependencies: Also update dependencies of specified package

        Returns:
            BuildResult

        Raises:
            BuildExecutionError: If update fails

        Example:
            composer.update()  # Update all
            composer.update(package="symfony/console")  # Update specific
        """
        return self.dependency_manager.update(
            package=package,
            with_dependencies=with_dependencies
        )

    @wrap_exception(BuildExecutionError, "Failed to run script")
    def run_script(self, script_name: str) -> BuildResult:
        """
        Run a script defined in composer.json.

        WHY: Execute custom project scripts
        RESPONSIBILITY: Execute composer scripts

        Args:
            script_name: Script name from scripts section

        Returns:
            BuildResult

        Raises:
            BuildExecutionError: If script fails

        Example:
            composer.run_script("post-install-cmd")
        """
        cmd = ["composer", "run-script", script_name]

        return self._execute_command(
            cmd,
            timeout=600,
            error_type=BuildExecutionError,
            error_message=f"Script '{script_name}' failed"
        )

    @wrap_exception(BuildExecutionError, "Failed to show package info")
    def show(
        self,
        package: Optional[str] = None,
        installed: bool = False
    ) -> BuildResult:
        """
        Show information about packages.

        WHY: Inspect package details
        RESPONSIBILITY: Delegate to dependency manager

        Args:
            package: Package name (None = all)
            installed: Show only installed packages

        Returns:
            BuildResult with package information

        Raises:
            BuildExecutionError: If command fails

        Example:
            result = composer.show("symfony/console")
        """
        return self.dependency_manager.show(
            package=package,
            installed=installed
        )

    @wrap_exception(BuildExecutionError, "Failed to validate")
    def validate(self) -> BuildResult:
        """
        Validate composer.json and composer.lock.

        WHY: Check configuration validity
        RESPONSIBILITY: Execute validation command

        Returns:
            BuildResult

        Raises:
            BuildExecutionError: If validation fails

        Example:
            composer.validate()
        """
        cmd = ["composer", "validate"]

        return self._execute_command(
            cmd,
            timeout=30,
            error_type=BuildExecutionError,
            error_message="Validation failed"
        )

    @wrap_exception(BuildExecutionError, "Failed to dump autoload")
    def dump_autoload(self, optimize: bool = False) -> BuildResult:
        """
        Regenerate autoloader.

        WHY: Update autoloader after file changes
        RESPONSIBILITY: Delegate to autoloader manager

        Args:
            optimize: Optimize autoloader

        Returns:
            BuildResult

        Raises:
            BuildExecutionError: If dump-autoload fails

        Example:
            composer.dump_autoload(optimize=True)
        """
        return self.autoloader_manager.dump_autoload(optimize=optimize)

    @wrap_exception(BuildExecutionError, "Failed to diagnose")
    def diagnose(self) -> BuildResult:
        """
        Run diagnostics.

        WHY: Diagnose setup issues
        RESPONSIBILITY: Execute diagnostic command

        Returns:
            BuildResult

        Raises:
            BuildExecutionError: If diagnose fails
        """
        cmd = ["composer", "diagnose"]

        return self._execute_command(
            cmd,
            timeout=60,
            error_type=BuildExecutionError,
            error_message="Diagnose failed"
        )

    def clean(self) -> BuildResult:
        """
        Clear Composer cache.

        WHY: Clear cache to resolve issues
        RESPONSIBILITY: Execute cache clear command

        Returns:
            BuildResult
        """
        cmd = ["composer", "clear-cache"]

        try:
            return self._execute_command(
                cmd,
                timeout=30,
                error_type=BuildExecutionError,
                error_message="Clear cache failed"
            )
        except BuildExecutionError as e:
            self.logger.warning(f"Clean failed: {e}")
            return BuildResult(
                success=False,
                exit_code=1,
                duration=0.0,
                output=str(e),
                build_system="composer"
            )

    def _extract_test_stats(self, output: str) -> Dict[str, int]:
        """
        Extract test statistics from PHPUnit output.

        WHY: Backward compatibility for direct calls
        RESPONSIBILITY: Delegate to test runner

        Args:
            output: PHPUnit output

        Returns:
            Dict with test statistics
        """
        return self.test_runner._extract_test_stats(output)
