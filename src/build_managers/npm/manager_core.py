"""
NPM Build Manager - Core Manager

WHY: Orchestrate NPM build operations with component delegation
RESPONSIBILITY: Coordinate specialized managers for NPM operations
PATTERNS: Template Method, Composition over Inheritance, Facade

This module provides the main NpmManager class that coordinates all
NPM operations by delegating to specialized component managers.
"""

from pathlib import Path
from typing import Dict, Optional, Any
import logging

from build_manager_base import BuildManagerBase, BuildResult
from build_manager_factory import register_build_manager, BuildSystem

from .models import PackageManager
from .config_parser import NpmConfigParser
from .version_manager import VersionManager
from .dependency_manager import DependencyManager
from .build_operations import BuildOperations


@register_build_manager(BuildSystem.NPM)
class NpmManager(BuildManagerBase):
    """
    Enterprise-grade NPM/Yarn/PNPM manager.

    WHY: Provide unified interface to JavaScript package managers
    RESPONSIBILITY: Coordinate component managers and delegate operations
    PATTERNS: Facade pattern, Composition over Inheritance, Template Method

    This manager inherits from BuildManagerBase and delegates specialized
    operations to focused component managers for maintainability.

    Auto-detects package manager from lock files (npm/yarn/pnpm).

    Example:
        npm = NpmManager(project_dir="/path/to/project")
        result = npm.build(script_name="build", production=True)
        test_result = npm.test(coverage=True)
    """

    def __init__(
        self,
        project_dir: Optional[Path] = None,
        logger: Optional['logging.Logger'] = None
    ):
        """
        Initialize NPM manager.

        WHY: Set up component managers for delegation
        PATTERNS: Dependency Injection, Template Method (super().__init__)

        Auto-detects npm/yarn/pnpm from lock files.

        Args:
            project_dir: Project directory
            logger: Logger instance

        Raises:
            BuildSystemNotFoundError: If package manager not found
            ProjectConfigurationError: If package.json invalid
        """
        # Initialize paths and detect package manager BEFORE super().__init__
        # because super().__init__() calls _validate_installation()
        project_path = Path(project_dir) if project_dir else Path.cwd()
        self.package_json_path = project_path / "package.json"
        self.package_manager = None

        # Create version manager early for detection
        self._temp_version_manager = VersionManager(
            execute_command=None,  # Will set after super().__init__
            logger=logger or logging.getLogger(__name__)
        )

        # Detect package manager
        self.package_manager = self._temp_version_manager.detect_package_manager(
            project_path
        )

        # Call parent initialization (triggers validation)
        super().__init__(project_dir, logger)

        # Initialize component managers
        self._init_components()

    def _init_components(self) -> None:
        """
        Initialize component managers.

        WHY: Centralize component initialization for clarity
        PATTERNS: Dependency Injection - pass execute method to components
        """
        # Configuration parser
        self.config_parser = NpmConfigParser(logger=self.logger)

        # Version manager (replace temp one)
        self.version_manager = VersionManager(
            execute_command=self._execute_command,
            logger=self.logger
        )

        # Dependency manager
        self.dependency_manager = DependencyManager(
            project_dir=self.project_dir,
            execute_command=self._execute_command,
            package_manager=self.package_manager,
            logger=self.logger
        )

        # Build operations
        self.build_ops = BuildOperations(
            project_dir=self.project_dir,
            execute_command=self._execute_command,
            package_manager=self.package_manager,
            logger=self.logger
        )

    def _validate_installation(self) -> None:
        """
        Validate package manager is installed.

        WHY: Delegate to version manager for separation of concerns
        PATTERNS: Delegation to specialized component

        Raises:
            BuildSystemNotFoundError: If package manager not in PATH
        """
        # Use temp version manager during initialization
        if hasattr(self, 'version_manager'):
            self.version_manager.validate_installation(self.package_manager)
        else:
            # During __init__, use execute_command directly
            from build_system_exceptions import BuildSystemNotFoundError
            from artemis_exceptions import wrap_exception

            cmd = self.package_manager.value
            result = self._execute_command(
                [cmd, "--version"],
                timeout=10,
                error_type=BuildSystemNotFoundError,
                error_message=f"{cmd} not installed or not in PATH"
            )
            version = result.output.strip()
            self.logger.info(f"Using {cmd} version: {version}")

    def _validate_project(self) -> None:
        """
        Validate package.json exists.

        WHY: Delegate to config parser for separation of concerns
        PATTERNS: Delegation to specialized component

        Raises:
            ProjectConfigurationError: If package.json missing
        """
        # Ensure config_parser is initialized
        if not hasattr(self, 'config_parser'):
            self.config_parser = NpmConfigParser(logger=self.logger)

        self.package_json_path = self.config_parser.validate_project(
            self.project_dir
        )

    def get_project_info(self) -> Dict[str, Any]:
        """
        Parse package.json for project information.

        WHY: Delegate to config parser for separation of concerns
        PATTERNS: Delegation to specialized component

        Returns:
            Dictionary with project information

        Raises:
            ProjectConfigurationError: If package.json malformed
        """
        return self.config_parser.parse_project_info(
            self.package_json_path,
            self.package_manager
        )

    def build(
        self,
        script_name: str = "build",
        production: bool = False,
        timeout: int = 600
    ) -> BuildResult:
        """
        Run npm build script.

        WHY: Delegate to build operations for separation of concerns
        PATTERNS: Delegation to specialized component

        Args:
            script_name: Script name from package.json (default: "build")
            production: Build for production
            timeout: Build timeout in seconds

        Returns:
            BuildResult

        Raises:
            BuildExecutionError: If build fails

        Example:
            result = npm.build(script_name="build:prod", production=True)
        """
        # Check if script exists (warning only)
        if not self.config_parser.has_script(self.package_json_path, script_name):
            self.logger.warning(f"Script '{script_name}' not found in package.json")

        return self.build_ops.build(
            script_name=script_name,
            production=production,
            timeout=timeout
        )

    def test(
        self,
        watch: bool = False,
        coverage: bool = False,
        timeout: int = 300
    ) -> BuildResult:
        """
        Run npm test.

        WHY: Delegate to build operations for separation of concerns
        PATTERNS: Delegation to specialized component

        Args:
            watch: Run in watch mode (not supported with subprocess)
            coverage: Generate coverage report
            timeout: Test timeout in seconds

        Returns:
            BuildResult with test statistics

        Raises:
            TestExecutionError: If tests fail

        Example:
            result = npm.test(coverage=True)
        """
        return self.build_ops.test(
            watch=watch,
            coverage=coverage,
            timeout=timeout
        )

    def install_dependency(
        self,
        package: str,
        version: Optional[str] = None,
        dev: bool = False,
        **kwargs
    ) -> bool:
        """
        Install a dependency.

        WHY: Delegate to dependency manager for separation of concerns
        PATTERNS: Delegation to specialized component

        Args:
            package: Package name
            version: Package version (optional)
            dev: Install as dev dependency

        Returns:
            True if successful

        Raises:
            DependencyInstallError: If installation fails

        Example:
            npm.install_dependency("react", version="18.2.0")
            npm.install_dependency("typescript", dev=True)
        """
        return self.dependency_manager.install_dependency(
            package=package,
            version=version,
            dev=dev,
            **kwargs
        )

    def install_dependencies(self, production: bool = False) -> BuildResult:
        """
        Install all dependencies from package.json.

        WHY: Delegate to dependency manager for separation of concerns
        PATTERNS: Delegation to specialized component

        Args:
            production: Install only production dependencies

        Returns:
            BuildResult

        Raises:
            BuildExecutionError: If install fails

        Example:
            npm.install_dependencies(production=True)
        """
        return self.dependency_manager.install_dependencies(
            production=production
        )

    def clean(self) -> BuildResult:
        """
        Clean build artifacts and node_modules.

        WHY: Delegate to build operations for separation of concerns
        PATTERNS: Delegation to specialized component

        Returns:
            BuildResult
        """
        return self.build_ops.clean()

    def _extract_test_stats(self, output: str) -> Dict[str, int]:
        """
        Extract test statistics from Jest/Mocha output.

        WHY: Delegate to build operations for separation of concerns
        PATTERNS: Delegation to specialized component

        Args:
            output: Test output

        Returns:
            Dict with test statistics
        """
        return self.build_ops.extract_test_stats(output)


__all__ = [
    'NpmManager'
]
