"""
Go Version Detector

WHY: Separate module for Go installation detection and version extraction
RESPONSIBILITY: Validate Go installation and extract version information
PATTERNS: Single Responsibility, regex parsing, command execution wrapper
"""

import re
import logging
from typing import Optional, Callable, Any

from artemis_exceptions import wrap_exception
from build_system_exceptions import BuildSystemNotFoundError
from build_manager_base import BuildResult


class GoVersionDetector:
    """
    WHY: Centralize Go version detection logic
    RESPONSIBILITY: Check Go installation and extract version
    PATTERNS: Single Responsibility, dependency injection for command executor
    """

    def __init__(
        self,
        execute_command: Callable[..., BuildResult],
        logger: Optional[logging.Logger] = None
    ):
        """
        WHY: Inject command executor for testability
        RESPONSIBILITY: Initialize with required dependencies
        PATTERNS: Dependency injection

        Args:
            execute_command: Command execution function
            logger: Logger instance
        """
        self.execute_command = execute_command
        self.logger = logger or logging.getLogger(__name__)

    @wrap_exception(BuildSystemNotFoundError, "Go not found")
    def validate_installation(self) -> Optional[str]:
        """
        WHY: Verify Go is installed and available
        RESPONSIBILITY: Execute 'go version' and extract version number
        PATTERNS: Guard clause, regex extraction, exception wrapping

        Returns:
            Go version string if found, None otherwise

        Raises:
            BuildSystemNotFoundError: If Go not in PATH
        """
        result = self.execute_command(
            ["go", "version"],
            timeout=10,
            error_type=BuildSystemNotFoundError,
            error_message="Go not installed or not in PATH"
        )

        version = self._extract_version(result.output)

        if version:
            self.logger.info(f"Using Go version: {version}")

        return version

    @staticmethod
    def _extract_version(output: str) -> Optional[str]:
        """
        WHY: Extract version number from 'go version' output
        RESPONSIBILITY: Parse version string using regex
        PATTERNS: Regex parsing, static method for pure function

        Args:
            output: Output from 'go version' command

        Returns:
            Version string or None
        """
        version_match = re.search(r"go version go([\d.]+)", output)
        return version_match.group(1) if version_match else None
