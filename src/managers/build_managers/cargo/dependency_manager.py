"""
Module: managers/build_managers/cargo/dependency_manager.py

WHY: Manage Rust crate dependencies via Cargo.
RESPONSIBILITY: Handle dependency installation and management operations.
PATTERNS: Command Pattern, Guard Clauses, Exception Wrapping.

This module contains:
- Crate dependency installation
- Dev dependency management
- Version specification

EXTRACTED FROM: cargo_manager.py (lines 285-327)
"""

import logging
from pathlib import Path
from typing import Callable, Optional

from artemis_exceptions import wrap_exception
from build_manager_base import BuildResult
from build_system_exceptions import DependencyInstallError


class DependencyManager:
    """
    Manages Cargo crate dependencies.

    WHY: Isolate dependency management logic from main manager.
    RESPONSIBILITY: Add, remove, and update crate dependencies.
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
            project_dir: Project root directory
            execute_command: Command execution function
            logger: Logger instance
        """
        self.project_dir = project_dir
        self.execute_command = execute_command
        self.logger = logger or logging.getLogger(__name__)

    @wrap_exception(DependencyInstallError, "Failed to add dependency")
    def install_dependency(
        self,
        crate: str,
        version: Optional[str] = None,
        dev: bool = False,
        **kwargs
    ) -> bool:
        """
        Add a dependency to Cargo.toml.

        WHY: Simplify adding crate dependencies.
        RESPONSIBILITY: Execute cargo add command with proper options.

        Args:
            crate: Crate name
            version: Crate version (optional)
            dev: Add as dev dependency

        Returns:
            True if successful

        Raises:
            DependencyInstallError: If installation fails

        Example:
            dm.install_dependency("serde", version="1.0")
            dm.install_dependency("tokio", dev=True)
        """
        if not crate:
            raise DependencyInstallError(
                "Crate name required",
                {"crate": crate}
            )

        cmd = ["cargo", "add", crate]

        if version:
            cmd.extend(["--vers", version])

        if dev:
            cmd.append("--dev")

        result = self.execute_command(
            cmd,
            timeout=60,
            error_type=DependencyInstallError,
            error_message=f"Failed to add crate {crate}"
        )

        self.logger.info(f"Added crate {crate}")
        return True

    @wrap_exception(DependencyInstallError, "Failed to remove dependency")
    def remove_dependency(self, crate: str) -> bool:
        """
        Remove a dependency from Cargo.toml.

        Args:
            crate: Crate name to remove

        Returns:
            True if successful

        Raises:
            DependencyInstallError: If removal fails

        Example:
            dm.remove_dependency("old-crate")
        """
        if not crate:
            raise DependencyInstallError(
                "Crate name required",
                {"crate": crate}
            )

        cmd = ["cargo", "rm", crate]

        result = self.execute_command(
            cmd,
            timeout=30,
            error_type=DependencyInstallError,
            error_message=f"Failed to remove crate {crate}"
        )

        self.logger.info(f"Removed crate {crate}")
        return True

    def update_dependencies(self) -> BuildResult:
        """
        Update all dependencies to latest compatible versions.

        Returns:
            BuildResult with update status

        Example:
            result = dm.update_dependencies()
        """
        cmd = ["cargo", "update"]

        return self.execute_command(
            cmd,
            timeout=300,
            error_type=DependencyInstallError,
            error_message="Failed to update dependencies"
        )


__all__ = [
    "DependencyManager",
]
