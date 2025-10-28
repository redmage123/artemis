"""
Poetry Build Manager - Core Manager

WHY: Orchestrate Poetry build operations with component delegation
RESPONSIBILITY: Coordinate specialized managers for Poetry operations
PATTERNS: Template Method, Composition over Inheritance, Facade

This module provides the main PoetryManager class that coordinates all
Poetry operations by delegating to specialized component managers.
"""

from pathlib import Path
from typing import Dict, Optional, Any
import logging

from build_manager_base import BuildManagerBase, BuildResult
from build_manager_factory import register_build_manager, BuildSystem

from .config_parser import PoetryConfigParser
from .dependency_manager import DependencyManager
from .build_operations import BuildOperations
from .version_manager import VersionManager


@register_build_manager(BuildSystem.POETRY)
class PoetryManager(BuildManagerBase):
    """
    Enterprise-grade Poetry manager for Python projects.

    WHY: Provide unified interface to Poetry build system operations
    RESPONSIBILITY: Coordinate component managers and delegate operations
    PATTERNS: Facade pattern, Composition over Inheritance, Template Method

    This manager inherits from BuildManagerBase and delegates specialized
    operations to focused component managers for maintainability.

    Example:
        poetry = PoetryManager(project_dir="/path/to/project")
        result = poetry.build()
        test_result = poetry.test()
    """

    def __init__(
        self,
        project_dir: Optional[Path] = None,
        logger: Optional['logging.Logger'] = None
    ):
        """
        Initialize Poetry manager.

        WHY: Set up component managers for delegation
        PATTERNS: Dependency Injection, Template Method (super().__init__)

        Args:
            project_dir: Project directory (contains pyproject.toml)
            logger: Logger instance

        Raises:
            BuildSystemNotFoundError: If Poetry not found
            ProjectConfigurationError: If pyproject.toml invalid
        """
        # Initialize paths before calling super().__init__
        self.pyproject_path = None
        self.poetry_lock_path = None

        # Call parent initialization (triggers validation)
        super().__init__(project_dir, logger)

        # Set lock file path after project_dir is set
        self.poetry_lock_path = self.project_dir / "poetry.lock"

        # Initialize component managers
        self._init_components()

    def _init_components(self) -> None:
        """
        Initialize component managers.

        WHY: Centralize component initialization for clarity
        PATTERNS: Dependency Injection - pass execute method to components
        """
        # Configuration parser
        self.config_parser = PoetryConfigParser(logger=self.logger)

        # Version manager
        self.version_manager = VersionManager(
            execute_command=self._execute_command,
            logger=self.logger
        )

        # Dependency manager
        self.dependency_manager = DependencyManager(
            project_dir=self.project_dir,
            execute_command=self._execute_command,
            logger=self.logger
        )

        # Build operations
        self.build_ops = BuildOperations(
            project_dir=self.project_dir,
            execute_command=self._execute_command,
            logger=self.logger
        )

    def _validate_installation(self) -> None:
        """
        Validate Poetry is installed.

        WHY: Delegate to version manager for separation of concerns
        PATTERNS: Delegation to specialized component

        Raises:
            BuildSystemNotFoundError: If Poetry not in PATH
        """
        self.version_manager.validate_installation()

    def _validate_project(self) -> None:
        """
        Validate pyproject.toml exists and contains [tool.poetry] section.

        WHY: Delegate to config parser for separation of concerns
        PATTERNS: Delegation to specialized component

        Raises:
            ProjectConfigurationError: If pyproject.toml missing or invalid
        """
        self.pyproject_path = self.config_parser.validate_project(
            self.project_dir
        )

    def get_project_info(self) -> Dict[str, Any]:
        """
        Parse pyproject.toml for project information.

        WHY: Delegate to config parser for separation of concerns
        PATTERNS: Delegation to specialized component

        Returns:
            Dictionary with project information

        Raises:
            ProjectConfigurationError: If pyproject.toml malformed
        """
        return self.config_parser.parse_project_info(
            self.pyproject_path,
            self.poetry_lock_path
        )

    def build(self, format: str = "wheel", **kwargs) -> BuildResult:
        """
        Build Python package with Poetry.

        WHY: Delegate to build operations for separation of concerns
        PATTERNS: Delegation to specialized component

        Args:
            format: Build format ("wheel", "sdist", or "all")

        Returns:
            BuildResult with build output

        Raises:
            BuildExecutionError: If build fails

        Example:
            result = poetry.build(format="wheel")
        """
        return self.build_ops.build(format=format, **kwargs)

    def test(
        self,
        test_path: Optional[str] = None,
        verbose: bool = False,
        **kwargs
    ) -> BuildResult:
        """
        Run tests with Poetry (uses pytest by default).

        WHY: Delegate to build operations for separation of concerns
        PATTERNS: Delegation to specialized component

        Args:
            test_path: Specific test file or directory
            verbose: Verbose output

        Returns:
            BuildResult with test statistics

        Raises:
            TestExecutionError: If tests fail

        Example:
            result = poetry.test(verbose=True)
        """
        return self.build_ops.test(
            test_path=test_path,
            verbose=verbose,
            **kwargs
        )

    def install_dependency(
        self,
        package: str,
        version: Optional[str] = None,
        group: str = "main",
        **kwargs
    ) -> bool:
        """
        Add a dependency to pyproject.toml.

        WHY: Delegate to dependency manager for separation of concerns
        PATTERNS: Delegation to specialized component

        Args:
            package: Package name
            version: Package version (optional)
            group: Dependency group (main, dev, test, docs)

        Returns:
            True if successful

        Raises:
            DependencyInstallError: If installation fails

        Example:
            poetry.install_dependency("requests", version="^2.28.0")
            poetry.install_dependency("pytest", group="dev")
        """
        return self.dependency_manager.install_dependency(
            package=package,
            version=version,
            group=group,
            **kwargs
        )

    def install_dependencies(
        self,
        no_dev: bool = False,
        sync: bool = False
    ) -> BuildResult:
        """
        Install all dependencies from pyproject.toml.

        WHY: Delegate to dependency manager for separation of concerns
        PATTERNS: Delegation to specialized component

        Args:
            no_dev: Skip dev dependencies
            sync: Remove packages not in lock file

        Returns:
            BuildResult with installation output

        Raises:
            BuildExecutionError: If install fails

        Example:
            poetry.install_dependencies()
        """
        return self.dependency_manager.install_dependencies(
            no_dev=no_dev,
            sync=sync
        )

    def update_dependencies(
        self,
        package: Optional[str] = None,
        dry_run: bool = False
    ) -> BuildResult:
        """
        Update dependencies.

        WHY: Delegate to dependency manager for separation of concerns
        PATTERNS: Delegation to specialized component

        Args:
            package: Specific package to update (None = all)
            dry_run: Show what would be updated without updating

        Returns:
            BuildResult with update output

        Raises:
            BuildExecutionError: If update fails

        Example:
            poetry.update_dependencies()  # Update all
            poetry.update_dependencies(package="requests")  # Specific
        """
        return self.dependency_manager.update_dependencies(
            package=package,
            dry_run=dry_run
        )

    def run_script(self, script_name: str) -> BuildResult:
        """
        Run a script defined in pyproject.toml.

        WHY: Delegate to build operations for separation of concerns
        PATTERNS: Delegation to specialized component

        Args:
            script_name: Script name from [tool.poetry.scripts]

        Returns:
            BuildResult with script output

        Raises:
            BuildExecutionError: If script fails

        Example:
            poetry.run_script("serve")
        """
        return self.build_ops.run_script(script_name)

    def show_package_info(self, package: str) -> BuildResult:
        """
        Show information about a package.

        WHY: Delegate to dependency manager for separation of concerns
        PATTERNS: Delegation to specialized component

        Args:
            package: Package name

        Returns:
            BuildResult with package information

        Raises:
            BuildExecutionError: If command fails

        Example:
            result = poetry.show_package_info("requests")
        """
        return self.dependency_manager.show_package_info(package)

    def _extract_test_stats(self, output: str) -> Dict[str, int]:
        """
        Extract test statistics from pytest output.

        WHY: Delegate to build operations for separation of concerns
        PATTERNS: Delegation to specialized component

        Args:
            output: pytest output text

        Returns:
            Dictionary with test statistics
        """
        return self.build_ops.extract_test_stats(output)


__all__ = [
    'PoetryManager'
]
