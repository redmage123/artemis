"""
NPM Build Manager - Version Manager

WHY: Detect and validate package manager installation and versions
RESPONSIBILITY: Manage package manager detection and version validation
PATTERNS: Strategy pattern, Guard clauses, Dispatch table

This module handles package manager detection from lock files and validates
that the appropriate package manager is installed.
"""

from pathlib import Path
from typing import Optional, Callable, Any
import logging

from artemis_exceptions import wrap_exception
from build_system_exceptions import BuildSystemNotFoundError
from build_manager_base import BuildResult

from .models import PackageManager


class VersionManager:
    """
    Manage package manager detection and version validation.

    WHY: Centralize package manager detection and validation logic
    RESPONSIBILITY: Detect package manager and validate installation
    PATTERNS: Strategy pattern for different package managers, Guard clauses

    This class handles auto-detection of package managers from lock files
    and validates that the detected package manager is installed.
    """

    def __init__(
        self,
        execute_command: Callable[..., BuildResult],
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize version manager.

        WHY: Setup command executor and logger
        PATTERNS: Dependency injection for execute command

        Args:
            execute_command: Command executor function
            logger: Logger instance
        """
        self.execute_command = execute_command
        self.logger = logger or logging.getLogger(__name__)

    def detect_package_manager(self, project_dir: Path) -> PackageManager:
        """
        Auto-detect package manager from lock files.

        WHY: Determine which package manager the project uses
        PATTERNS: Guard clauses for lock file detection

        Args:
            project_dir: Project directory

        Returns:
            PackageManager enum
        """
        # Check lock files (most specific first)
        if (project_dir / "pnpm-lock.yaml").exists():
            self.logger.info("Detected pnpm from pnpm-lock.yaml")
            return PackageManager.PNPM

        if (project_dir / "yarn.lock").exists():
            self.logger.info("Detected yarn from yarn.lock")
            return PackageManager.YARN

        # Default to npm
        self.logger.info("Using npm (default)")
        return PackageManager.NPM

    @wrap_exception(BuildSystemNotFoundError, "Package manager not found")
    def validate_installation(
        self,
        package_manager: PackageManager
    ) -> str:
        """
        Validate package manager is installed.

        WHY: Early validation to fail fast if package manager missing
        PATTERNS: Guard clause, Exception wrapping

        Args:
            package_manager: Package manager to validate

        Returns:
            Version string

        Raises:
            BuildSystemNotFoundError: If package manager not in PATH
        """
        cmd = package_manager.value
        result = self.execute_command(
            [cmd, "--version"],
            timeout=10,
            error_type=BuildSystemNotFoundError,
            error_message=f"{cmd} not installed or not in PATH"
        )

        version = result.output.strip()
        self.logger.info(f"Using {cmd} version: {version}")
        return version


__all__ = [
    'VersionManager'
]
