"""
Module: managers/build_managers/cargo/version_detector.py

WHY: Detect and validate Rust/Cargo installation.
RESPONSIBILITY: Check Cargo availability and extract version information.
PATTERNS: Guard Clauses, Exception Wrapping, Regex Pattern Matching.

This module contains:
- Cargo installation validation
- Version extraction
- Rust toolchain detection

EXTRACTED FROM: cargo_manager.py (lines 113-133)
"""

import logging
import re
from typing import Callable, Optional

from artemis_exceptions import wrap_exception
from build_system_exceptions import BuildSystemNotFoundError


class VersionDetector:
    """
    Detects Cargo/Rust version and validates installation.

    WHY: Ensure Cargo is available before operations.
    RESPONSIBILITY: Validate installation and extract version.
    """

    def __init__(
        self,
        execute_command: Callable,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize version detector.

        Args:
            execute_command: Command execution function
            logger: Logger instance
        """
        self.execute_command = execute_command
        self.logger = logger or logging.getLogger(__name__)

    @wrap_exception(BuildSystemNotFoundError, "Cargo not found")
    def validate_installation(self) -> str:
        """
        Validate Cargo is installed and get version.

        WHY: Fail fast if Cargo is not available.
        RESPONSIBILITY: Check for cargo in PATH and extract version.

        Returns:
            Cargo version string

        Raises:
            BuildSystemNotFoundError: If Cargo not in PATH

        Example:
            version = detector.validate_installation()
            # Returns: "1.75.0"
        """
        result = self.execute_command(
            ["cargo", "--version"],
            timeout=10,
            error_type=BuildSystemNotFoundError,
            error_message="Cargo not installed or not in PATH"
        )

        # Extract version
        version_match = re.search(r"cargo ([\d.]+)", result.output)

        if not version_match:
            self.logger.warning("Could not extract Cargo version from output")
            return "unknown"

        version = version_match.group(1)
        self.logger.info(f"Using Cargo version: {version}")
        return version

    def get_rustc_version(self) -> Optional[str]:
        """
        Get rustc compiler version.

        WHY: Provide detailed toolchain information.
        RESPONSIBILITY: Query rustc version.

        Returns:
            Rustc version string or None if unavailable

        Example:
            version = detector.get_rustc_version()
            # Returns: "1.75.0"
        """
        try:
            result = self.execute_command(
                ["rustc", "--version"],
                timeout=10,
                error_type=BuildSystemNotFoundError,
                error_message="rustc not found"
            )

            version_match = re.search(r"rustc ([\d.]+)", result.output)
            if version_match:
                return version_match.group(1)

        except Exception as e:
            self.logger.debug(f"Could not get rustc version: {e}")

        return None

    def check_tool_installed(self, tool_name: str) -> bool:
        """
        Check if a Cargo tool is installed.

        WHY: Verify optional tools (clippy, rustfmt) are available.
        RESPONSIBILITY: Check tool availability.

        Args:
            tool_name: Tool to check (e.g., "clippy", "rustfmt")

        Returns:
            True if tool is installed

        Example:
            has_clippy = detector.check_tool_installed("clippy")
        """
        try:
            result = self.execute_command(
                ["cargo", tool_name, "--version"],
                timeout=10,
                error_type=BuildSystemNotFoundError,
                error_message=f"cargo-{tool_name} not found"
            )
            return result.success
        except Exception:
            return False


__all__ = [
    "VersionDetector",
]
