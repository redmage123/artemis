#!/usr/bin/env python3
"""
Composer Dependency Manager

WHY: Isolated dependency installation and management logic
RESPONSIBILITY: Handle package installation, updates, and removal operations
PATTERNS:
- Single Responsibility: Only handles dependency operations
- Command builder pattern: Construct command arrays
- Guard clauses: Validate inputs before execution
"""

from pathlib import Path
from typing import Optional, Callable, Any
import logging

from artemis_exceptions import wrap_exception
from build_system_exceptions import DependencyInstallError, BuildExecutionError
from build_manager_base import BuildResult


class DependencyManager:
    """
    Manages Composer dependency operations.

    WHY: Separate dependency logic from main manager
    RESPONSIBILITY: Install, update, and manage PHP packages via Composer
    """

    def __init__(
        self,
        project_dir: Path,
        execute_command: Callable,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize dependency manager.

        Args:
            project_dir: Project directory
            execute_command: Command execution function from parent manager
            logger: Logger instance
        """
        self.project_dir = project_dir
        self._execute_command = execute_command
        self.logger = logger or logging.getLogger(__name__)

    @wrap_exception(DependencyInstallError, "Failed to install dependencies")
    def install(
        self,
        no_dev: bool = False,
        optimize_autoloader: bool = False,
        prefer_dist: bool = False
    ) -> BuildResult:
        """
        Install all dependencies from composer.json.

        WHY: Central entry point for dependency installation
        RESPONSIBILITY: Construct install command with appropriate flags

        Args:
            no_dev: Skip development dependencies
            optimize_autoloader: Generate optimized autoloader
            prefer_dist: Prefer distribution packages over source

        Returns:
            BuildResult with installation status

        Raises:
            DependencyInstallError: If installation fails

        Example:
            result = dm.install(no_dev=True, optimize_autoloader=True)
        """
        cmd = self._build_install_command(no_dev, optimize_autoloader, prefer_dist)

        return self._execute_command(
            cmd,
            timeout=300,
            error_type=DependencyInstallError,
            error_message="Dependency installation failed"
        )

    def _build_install_command(
        self,
        no_dev: bool,
        optimize_autoloader: bool,
        prefer_dist: bool
    ) -> list[str]:
        """
        Build install command array.

        WHY: Separate command construction from execution
        RESPONSIBILITY: Construct command with conditional flags

        Args:
            no_dev: Skip dev dependencies flag
            optimize_autoloader: Optimize autoloader flag
            prefer_dist: Prefer dist flag

        Returns:
            Command array ready for execution
        """
        cmd = ["composer", "install"]

        if no_dev:
            cmd.append("--no-dev")

        if optimize_autoloader:
            cmd.append("--optimize-autoloader")

        if prefer_dist:
            cmd.append("--prefer-dist")

        return cmd

    @wrap_exception(DependencyInstallError, "Failed to add package")
    def require_package(
        self,
        package: str,
        version: Optional[str] = None,
        dev: bool = False
    ) -> bool:
        """
        Add a package to composer.json and install it.

        WHY: Streamlined package addition
        RESPONSIBILITY: Add and install package in single operation

        Args:
            package: Package name (e.g., "symfony/console")
            version: Version constraint (e.g., "^6.0")
            dev: Add as development dependency

        Returns:
            True if successful

        Raises:
            DependencyInstallError: If package installation fails

        Example:
            dm.require_package("symfony/console", version="^6.0")
            dm.require_package("phpunit/phpunit", dev=True)
        """
        if not package:
            raise DependencyInstallError(
                "Package name is required",
                {"package": package}
            )

        cmd = self._build_require_command(package, version, dev)

        result = self._execute_command(
            cmd,
            timeout=120,
            error_type=DependencyInstallError,
            error_message=f"Failed to add package {package}"
        )

        self.logger.info(f"Added package {package}")
        return result.success

    def _build_require_command(
        self,
        package: str,
        version: Optional[str],
        dev: bool
    ) -> list[str]:
        """
        Build require command array.

        WHY: Separate command construction from execution
        RESPONSIBILITY: Format package specification with version

        Args:
            package: Package name
            version: Version constraint
            dev: Development dependency flag

        Returns:
            Command array for composer require
        """
        package_spec = f"{package}:{version}" if version else package
        cmd = ["composer", "require", package_spec]

        if dev:
            cmd.append("--dev")

        return cmd

    @wrap_exception(BuildExecutionError, "Failed to update dependencies")
    def update(
        self,
        package: Optional[str] = None,
        with_dependencies: bool = True
    ) -> BuildResult:
        """
        Update dependencies to latest versions.

        WHY: Keep dependencies current with security patches
        RESPONSIBILITY: Update all or specific package dependencies

        Args:
            package: Specific package to update (None for all)
            with_dependencies: Update transitive dependencies

        Returns:
            BuildResult with update status

        Raises:
            BuildExecutionError: If update fails

        Example:
            dm.update()  # Update all
            dm.update(package="symfony/console")  # Update specific
        """
        cmd = self._build_update_command(package, with_dependencies)

        return self._execute_command(
            cmd,
            timeout=300,
            error_type=BuildExecutionError,
            error_message="Dependency update failed"
        )

    def _build_update_command(
        self,
        package: Optional[str],
        with_dependencies: bool
    ) -> list[str]:
        """
        Build update command array.

        WHY: Separate command construction logic
        RESPONSIBILITY: Construct update command with conditional flags

        Args:
            package: Optional package to update
            with_dependencies: Whether to update dependencies

        Returns:
            Command array for composer update
        """
        cmd = ["composer", "update"]

        if package:
            cmd.append(package)
            if not with_dependencies:
                cmd.append("--no-update-with-dependencies")

        return cmd

    @wrap_exception(BuildExecutionError, "Failed to show package info")
    def show(
        self,
        package: Optional[str] = None,
        installed: bool = False
    ) -> BuildResult:
        """
        Show information about packages.

        WHY: Enable package inspection and debugging
        RESPONSIBILITY: Display package details and metadata

        Args:
            package: Package name (None for all packages)
            installed: Show only installed packages

        Returns:
            BuildResult with package information

        Raises:
            BuildExecutionError: If command fails

        Example:
            result = dm.show("symfony/console")
        """
        cmd = ["composer", "show"]

        if installed:
            cmd.append("--installed")

        if package:
            cmd.append(package)

        return self._execute_command(
            cmd,
            timeout=30,
            error_type=BuildExecutionError,
            error_message="Failed to show package info"
        )
