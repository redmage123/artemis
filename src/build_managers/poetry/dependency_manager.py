"""
Poetry Build Manager - Dependency Management

WHY: Isolate all dependency-related operations
RESPONSIBILITY: Install, update, and manage Poetry dependencies
PATTERNS: Single Responsibility, Command Execution Delegation, Guard Clauses

This module handles dependency operations including installation, updates,
package additions, and package information queries.
"""

from pathlib import Path
from typing import Optional, Callable, Any
import logging

from artemis_exceptions import wrap_exception
from build_system_exceptions import (
    DependencyInstallError,
    BuildExecutionError
)
from build_manager_base import BuildResult


class DependencyManager:
    """
    Manages Poetry dependency operations.

    WHY: Centralize dependency management logic
    RESPONSIBILITY: Execute all dependency-related Poetry commands
    PATTERNS: Single Responsibility, Guard Clauses, Dependency Injection
    """

    def __init__(
        self,
        project_dir: Path,
        execute_command: Callable[..., BuildResult],
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize dependency manager.

        WHY: Inject command executor to decouple from execution details
        PATTERNS: Dependency Injection for testability

        Args:
            project_dir: Project directory path
            execute_command: Command execution callable
            logger: Logger instance
        """
        self.project_dir = project_dir
        self.execute_command = execute_command
        self.logger = logger or logging.getLogger(__name__)

    @wrap_exception(DependencyInstallError, "Failed to add dependency")
    def install_dependency(
        self,
        package: str,
        version: Optional[str] = None,
        group: str = "main",
        **kwargs
    ) -> bool:
        """
        Add a dependency to pyproject.toml.

        WHY: Programmatically manage project dependencies
        PATTERNS: Guard clauses for parameter validation

        Args:
            package: Package name
            version: Package version (optional)
            group: Dependency group (main, dev, test, docs)

        Returns:
            True if successful

        Raises:
            DependencyInstallError: If installation fails

        Example:
            manager.install_dependency("requests", version="^2.28.0")
            manager.install_dependency("pytest", group="dev")
        """
        cmd = ["poetry", "add", package]

        if version:
            cmd[-1] = f"{package}@{version}"

        if group == "dev":
            cmd.append("--group=dev")
        elif group != "main":
            cmd.append(f"--group={group}")

        result = self.execute_command(
            cmd,
            timeout=120,
            error_type=DependencyInstallError,
            error_message=f"Failed to add package {package}"
        )

        self.logger.info(f"Added package {package}")
        return True

    @wrap_exception(BuildExecutionError, "Failed to install dependencies")
    def install_dependencies(
        self,
        no_dev: bool = False,
        sync: bool = False
    ) -> BuildResult:
        """
        Install all dependencies from pyproject.toml.

        WHY: Bootstrap project environment with required packages
        PATTERNS: Boolean flags for operation modes

        Args:
            no_dev: Skip dev dependencies
            sync: Remove packages not in lock file

        Returns:
            BuildResult with installation output

        Raises:
            BuildExecutionError: If install fails

        Example:
            manager.install_dependencies()
            manager.install_dependencies(no_dev=True, sync=True)
        """
        cmd = ["poetry", "install"]

        if no_dev:
            cmd.append("--no-dev")

        if sync:
            cmd.append("--sync")

        return self.execute_command(
            cmd,
            timeout=300,
            error_type=BuildExecutionError,
            error_message="Dependency installation failed"
        )

    @wrap_exception(BuildExecutionError, "Failed to update dependencies")
    def update_dependencies(
        self,
        package: Optional[str] = None,
        dry_run: bool = False
    ) -> BuildResult:
        """
        Update dependencies.

        WHY: Keep dependencies current with latest compatible versions
        PATTERNS: Optional parameter for targeted vs. bulk updates

        Args:
            package: Specific package to update (None = all)
            dry_run: Show what would be updated without updating

        Returns:
            BuildResult with update output

        Raises:
            BuildExecutionError: If update fails

        Example:
            manager.update_dependencies()  # Update all
            manager.update_dependencies(package="requests")  # Specific
            manager.update_dependencies(dry_run=True)  # Preview
        """
        cmd = ["poetry", "update"]

        if package:
            cmd.append(package)

        if dry_run:
            cmd.append("--dry-run")

        return self.execute_command(
            cmd,
            timeout=300,
            error_type=BuildExecutionError,
            error_message="Dependency update failed"
        )

    @wrap_exception(BuildExecutionError, "Failed to show package info")
    def show_package_info(self, package: str) -> BuildResult:
        """
        Show information about a package.

        WHY: Inspect package details for debugging and analysis
        PATTERNS: Simple query wrapper

        Args:
            package: Package name

        Returns:
            BuildResult with package information

        Raises:
            BuildExecutionError: If command fails

        Example:
            result = manager.show_package_info("requests")
        """
        cmd = ["poetry", "show", package]

        return self.execute_command(
            cmd,
            timeout=30,
            error_type=BuildExecutionError,
            error_message=f"Failed to show info for {package}"
        )


__all__ = [
    'DependencyManager'
]
