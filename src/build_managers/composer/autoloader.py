#!/usr/bin/env python3
"""
Composer Autoloader Manager

WHY: Isolated autoloader generation and optimization logic
RESPONSIBILITY: Handle PHP autoloader generation and optimization
PATTERNS:
- Single Responsibility: Only handles autoloader operations
- Guard clauses: Validate before execution
- Command builder pattern: Construct command arrays
"""

from pathlib import Path
from typing import Optional, Callable
import logging

from artemis_exceptions import wrap_exception
from build_system_exceptions import BuildExecutionError
from build_manager_base import BuildResult


class AutoloaderManager:
    """
    Manages Composer autoloader operations.

    WHY: Separate autoloader logic from main manager
    RESPONSIBILITY: Generate and optimize PHP autoloader files
    """

    def __init__(
        self,
        project_dir: Path,
        execute_command: Callable,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize autoloader manager.

        Args:
            project_dir: Project directory
            execute_command: Command execution function from parent manager
            logger: Logger instance
        """
        self.project_dir = project_dir
        self._execute_command = execute_command
        self.logger = logger or logging.getLogger(__name__)

    @wrap_exception(BuildExecutionError, "Failed to dump autoload")
    def dump_autoload(self, optimize: bool = False) -> BuildResult:
        """
        Regenerate autoloader files.

        WHY: Update autoloader after file structure changes
        RESPONSIBILITY: Generate vendor/autoload.php with current class mappings

        Args:
            optimize: Generate optimized class map for production

        Returns:
            BuildResult with generation status

        Raises:
            BuildExecutionError: If autoloader generation fails

        Example:
            result = autoloader.dump_autoload(optimize=True)
        """
        cmd = self._build_dump_autoload_command(optimize)

        return self._execute_command(
            cmd,
            timeout=60,
            error_type=BuildExecutionError,
            error_message="dump-autoload failed"
        )

    def _build_dump_autoload_command(self, optimize: bool) -> list[str]:
        """
        Build dump-autoload command array.

        WHY: Separate command construction from execution
        RESPONSIBILITY: Construct command with optimization flag

        Args:
            optimize: Whether to optimize autoloader

        Returns:
            Command array for composer dump-autoload
        """
        cmd = ["composer", "dump-autoload"]

        if optimize:
            cmd.append("--optimize")

        return cmd

    @wrap_exception(BuildExecutionError, "Failed to validate autoloader")
    def validate_autoloader(self) -> bool:
        """
        Check if autoloader exists and is valid.

        WHY: Verify autoloader before application execution
        RESPONSIBILITY: Check vendor/autoload.php existence

        Returns:
            True if autoloader exists and is valid

        Raises:
            BuildExecutionError: If validation fails
        """
        autoloader_path = self.project_dir / "vendor" / "autoload.php"

        if not autoloader_path.exists():
            self.logger.warning("Autoloader not found at vendor/autoload.php")
            return False

        # Check if file is readable and not empty
        try:
            with open(autoloader_path, 'r') as f:
                content = f.read()
                if not content.strip():
                    self.logger.warning("Autoloader file is empty")
                    return False

            self.logger.info("Autoloader validated successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to validate autoloader: {e}")
            return False

    def get_autoloader_path(self) -> Path:
        """
        Get path to autoloader file.

        WHY: Provide consistent autoloader path for integration
        RESPONSIBILITY: Return standard Composer autoloader location

        Returns:
            Path to vendor/autoload.php
        """
        return self.project_dir / "vendor" / "autoload.php"
