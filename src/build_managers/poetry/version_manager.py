"""
Poetry Build Manager - Version Management

WHY: Isolate Poetry version detection and validation logic
RESPONSIBILITY: Detect, parse, and validate Poetry installation version
PATTERNS: Single Responsibility, Guard Clauses, Regex Patterns

This module handles Poetry version detection, parsing, and validation to ensure
compatibility with project requirements.
"""

from typing import Optional, Callable
import re
import logging

from artemis_exceptions import wrap_exception
from build_system_exceptions import BuildSystemNotFoundError
from build_manager_base import BuildResult


class VersionManager:
    """
    Manages Poetry version detection and validation.

    WHY: Centralize version-related operations
    RESPONSIBILITY: Detect and validate Poetry installation
    PATTERNS: Single Responsibility, Dependency Injection
    """

    def __init__(
        self,
        execute_command: Callable[..., BuildResult],
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize version manager.

        WHY: Inject command executor to decouple from execution details
        PATTERNS: Dependency Injection for testability

        Args:
            execute_command: Command execution callable
            logger: Logger instance
        """
        self.execute_command = execute_command
        self.logger = logger or logging.getLogger(__name__)
        self._cached_version: Optional[str] = None

    @wrap_exception(BuildSystemNotFoundError, "Poetry not found")
    def validate_installation(self) -> None:
        """
        Validate Poetry is installed.

        WHY: Early detection of missing Poetry prevents cryptic errors
        PATTERNS: Guard clause - fail fast if Poetry unavailable

        Raises:
            BuildSystemNotFoundError: If Poetry not in PATH
        """
        result = self.execute_command(
            ["poetry", "--version"],
            timeout=10,
            error_type=BuildSystemNotFoundError,
            error_message="Poetry not installed or not in PATH"
        )

        # Extract and cache version
        version = self._extract_version(result.output)
        if version:
            self._cached_version = version
            self.logger.info(f"Using Poetry version: {version}")

    @staticmethod
    def _extract_version(output: str) -> Optional[str]:
        """
        Extract version number from Poetry --version output.

        WHY: Parse version for compatibility checks and logging
        PATTERNS: Regex pattern matching, static method (no state)

        Args:
            output: Output from 'poetry --version'

        Returns:
            Version string (e.g., "1.7.1") or None if not found

        Example:
            >>> VersionManager._extract_version("Poetry (version 1.7.1)")
            "1.7.1"
        """
        version_match = re.search(r"Poetry (?:version )?(\d+\.\d+\.\d+)", output)
        if not version_match:
            return None
        return version_match.group(1)

    def get_version(self) -> Optional[str]:
        """
        Get cached Poetry version.

        WHY: Avoid repeated version checks
        PATTERNS: Lazy initialization with caching

        Returns:
            Cached version string or None if not yet validated
        """
        return self._cached_version

    def is_version_compatible(self, min_version: str) -> bool:
        """
        Check if installed Poetry version meets minimum requirement.

        WHY: Ensure Poetry version compatibility with project requirements
        PATTERNS: Version comparison with tuple unpacking

        Args:
            min_version: Minimum required version (e.g., "1.5.0")

        Returns:
            True if installed version >= min_version, False otherwise

        Example:
            if not manager.is_version_compatible("1.5.0"):
                raise Error("Poetry 1.5.0 or higher required")
        """
        if not self._cached_version:
            return False

        def parse_version(version: str) -> tuple:
            """Parse version string to comparable tuple"""
            return tuple(int(x) for x in version.split('.'))

        try:
            installed = parse_version(self._cached_version)
            required = parse_version(min_version)
            return installed >= required
        except (ValueError, AttributeError):
            return False


__all__ = [
    'VersionManager'
]
