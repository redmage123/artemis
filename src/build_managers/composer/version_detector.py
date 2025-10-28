#!/usr/bin/env python3
"""
PHP and Composer Version Detector

WHY: Isolated version detection and validation logic
RESPONSIBILITY: Detect and validate PHP and Composer versions
PATTERNS:
- Single Responsibility: Only handles version detection
- Guard clauses: Validate outputs before parsing
- Regex pattern matching for version extraction
"""

from pathlib import Path
from typing import Optional, Callable
import logging
import re

from artemis_exceptions import wrap_exception
from build_system_exceptions import BuildSystemNotFoundError
from build_manager_base import BuildResult


class VersionDetector:
    """
    Detects PHP and Composer versions.

    WHY: Centralize version detection logic
    RESPONSIBILITY: Extract and validate tool versions for compatibility checks
    """

    def __init__(
        self,
        execute_command: Callable,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize version detector.

        Args:
            execute_command: Command execution function from parent manager
            logger: Logger instance
        """
        self._execute_command = execute_command
        self.logger = logger or logging.getLogger(__name__)

    @wrap_exception(BuildSystemNotFoundError, "Composer not found")
    def detect_composer_version(self) -> str:
        """
        Detect installed Composer version.

        WHY: Verify Composer availability and version compatibility
        RESPONSIBILITY: Execute version command and parse output

        Returns:
            Composer version string (e.g., "2.5.8")

        Raises:
            BuildSystemNotFoundError: If Composer not installed or not in PATH

        Example:
            version = detector.detect_composer_version()
            # Returns: "2.5.8"
        """
        result = self._execute_command(
            ["composer", "--version"],
            timeout=10,
            error_type=BuildSystemNotFoundError,
            error_message="Composer not installed or not in PATH"
        )

        version = self._parse_composer_version(result.output)

        if not version:
            self.logger.warning("Could not parse Composer version from output")
            return "unknown"

        self.logger.info(f"Detected Composer version: {version}")
        return version

    def _parse_composer_version(self, output: str) -> Optional[str]:
        """
        Parse Composer version from command output.

        WHY: Extract version number from verbose output
        RESPONSIBILITY: Use regex to extract semantic version

        Args:
            output: Output from composer --version

        Returns:
            Version string or None if not found

        Example output:
            "Composer version 2.5.8 2023-06-09 17:13:21"
        """
        version_match = re.search(r"Composer version ([\d.]+)", output)

        if not version_match:
            return None

        return version_match.group(1)

    def detect_php_version(self) -> Optional[str]:
        """
        Detect installed PHP version.

        WHY: Verify PHP availability and version compatibility
        RESPONSIBILITY: Execute PHP version command and parse output

        Returns:
            PHP version string (e.g., "8.2.10") or None if not available

        Example:
            version = detector.detect_php_version()
            # Returns: "8.2.10"
        """
        try:
            result = self._execute_command(
                ["php", "--version"],
                timeout=10,
                error_type=BuildSystemNotFoundError,
                error_message="PHP not installed or not in PATH"
            )

            version = self._parse_php_version(result.output)

            if version:
                self.logger.info(f"Detected PHP version: {version}")
            else:
                self.logger.warning("Could not parse PHP version from output")

            return version

        except BuildSystemNotFoundError:
            self.logger.warning("PHP not found in PATH")
            return None

    def _parse_php_version(self, output: str) -> Optional[str]:
        """
        Parse PHP version from command output.

        WHY: Extract version number from verbose output
        RESPONSIBILITY: Use regex to extract semantic version

        Args:
            output: Output from php --version

        Returns:
            Version string or None if not found

        Example output:
            "PHP 8.2.10 (cli) (built: Sep 13 2023 10:53:18) (NTS)"
        """
        version_match = re.search(r"PHP ([\d.]+)", output)

        if not version_match:
            return None

        return version_match.group(1)

    def check_version_compatibility(
        self,
        required_version: str,
        actual_version: str
    ) -> bool:
        """
        Check if actual version meets requirement.

        WHY: Validate version compatibility before operations
        RESPONSIBILITY: Compare versions using simple string comparison

        Args:
            required_version: Required version (e.g., ">=7.4")
            actual_version: Actual version (e.g., "8.2.10")

        Returns:
            True if compatible, False otherwise

        Note:
            This is a simplified check. For production use, consider
            using packaging.version or similar for proper semantic versioning.
        """
        # Remove comparison operators from required version
        clean_required = re.sub(r'^[><=^~]+', '', required_version)

        # Simple major.minor comparison
        try:
            req_parts = [int(x) for x in clean_required.split('.')[:2]]
            act_parts = [int(x) for x in actual_version.split('.')[:2]]

            # Check major version
            if act_parts[0] > req_parts[0]:
                return True
            if act_parts[0] < req_parts[0]:
                return False

            # Check minor version if major matches
            return act_parts[1] >= req_parts[1]

        except (ValueError, IndexError) as e:
            self.logger.warning(f"Version comparison failed: {e}")
            return True  # Assume compatible if can't parse
