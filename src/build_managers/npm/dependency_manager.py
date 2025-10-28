"""
NPM Build Manager - Dependency Manager

WHY: Manage NPM dependency installation, updates, and removal
RESPONSIBILITY: Handle all dependency-related operations
PATTERNS: Strategy pattern, Command pattern, Dispatch table

This module manages all dependency operations including installation,
updates, and removal, with support for npm, yarn, and pnpm.
"""

from pathlib import Path
from typing import Optional, Callable, Dict, List
import logging

from artemis_exceptions import wrap_exception
from build_system_exceptions import (
    DependencyInstallError,
    BuildExecutionError
)
from build_manager_base import BuildResult

from .models import PackageManager


class DependencyManager:
    """
    Manage NPM dependencies.

    WHY: Centralize dependency management logic
    RESPONSIBILITY: Install, update, and manage dependencies
    PATTERNS: Strategy pattern for different package managers, Dispatch table

    This class handles all dependency operations with support for different
    package managers (npm, yarn, pnpm).
    """

    def __init__(
        self,
        project_dir: Path,
        execute_command: Callable[..., BuildResult],
        package_manager: PackageManager,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize dependency manager.

        WHY: Setup dependencies for command execution
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

        # Dispatch table for package manager commands
        self._install_commands = {
            PackageManager.NPM: "install",
            PackageManager.YARN: "add",
            PackageManager.PNPM: "add"
        }

        self._dev_flags = {
            PackageManager.NPM: "--save-dev",
            PackageManager.YARN: "--dev",
            PackageManager.PNPM: "--dev"
        }

    @wrap_exception(DependencyInstallError, "Failed to install dependency")
    def install_dependency(
        self,
        package: str,
        version: Optional[str] = None,
        dev: bool = False,
        **kwargs
    ) -> bool:
        """
        Install a dependency.

        WHY: Add single package to project dependencies
        PATTERNS: Strategy pattern for different package managers

        Args:
            package: Package name
            version: Package version (optional)
            dev: Install as dev dependency

        Returns:
            True if successful

        Raises:
            DependencyInstallError: If installation fails

        Example:
            manager.install_dependency("react", version="18.2.0")
            manager.install_dependency("typescript", dev=True)
        """
        cmd = self._build_install_command(package, version, dev)

        result = self.execute_command(
            cmd,
            timeout=120,
            error_type=DependencyInstallError,
            error_message=f"Failed to install {package}"
        )

        self.logger.info(f"Installed {package}")
        return True

    def _build_install_command(
        self,
        package: str,
        version: Optional[str],
        dev: bool
    ) -> List[str]:
        """
        Build install command for package manager.

        WHY: Encapsulate package manager differences
        PATTERNS: Strategy pattern, Dispatch table

        Args:
            package: Package name
            version: Package version (optional)
            dev: Install as dev dependency

        Returns:
            Command list
        """
        cmd = [self.package_manager.value]

        # Add install/add verb
        install_cmd = self._install_commands[self.package_manager]
        cmd.append(install_cmd)

        # Add package with version
        package_spec = f"{package}@{version}" if version else package
        cmd.append(package_spec)

        # Add dev flag if needed
        if dev:
            dev_flag = self._dev_flags[self.package_manager]
            cmd.append(dev_flag)

        return cmd

    @wrap_exception(BuildExecutionError, "Install failed")
    def install_dependencies(self, production: bool = False) -> BuildResult:
        """
        Install all dependencies from package.json.

        WHY: Install all project dependencies at once
        PATTERNS: Command pattern

        Args:
            production: Install only production dependencies

        Returns:
            BuildResult

        Raises:
            BuildExecutionError: If install fails

        Example:
            manager.install_dependencies(production=True)
        """
        cmd = [self.package_manager.value, "install"]

        if production:
            cmd.append("--production")

        return self.execute_command(
            cmd,
            timeout=300,
            error_type=BuildExecutionError,
            error_message="Dependency installation failed"
        )

    @wrap_exception(DependencyInstallError, "Failed to remove dependency")
    def remove_dependency(
        self,
        package: str,
        **kwargs
    ) -> bool:
        """
        Remove a dependency.

        WHY: Uninstall package from project
        PATTERNS: Strategy pattern for different package managers

        Args:
            package: Package name

        Returns:
            True if successful

        Raises:
            DependencyInstallError: If removal fails

        Example:
            manager.remove_dependency("lodash")
        """
        cmd = self._build_remove_command(package)

        result = self.execute_command(
            cmd,
            timeout=60,
            error_type=DependencyInstallError,
            error_message=f"Failed to remove {package}"
        )

        self.logger.info(f"Removed {package}")
        return True

    def _build_remove_command(self, package: str) -> List[str]:
        """
        Build remove command for package manager.

        WHY: Encapsulate package manager differences
        PATTERNS: Strategy pattern, Dispatch table

        Args:
            package: Package name

        Returns:
            Command list
        """
        cmd = [self.package_manager.value]

        # Remove/uninstall verb differs by package manager
        remove_commands = {
            PackageManager.NPM: "uninstall",
            PackageManager.YARN: "remove",
            PackageManager.PNPM: "remove"
        }

        remove_cmd = remove_commands[self.package_manager]
        cmd.extend([remove_cmd, package])

        return cmd


__all__ = [
    'DependencyManager'
]
