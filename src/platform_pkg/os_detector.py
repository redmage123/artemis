#!/usr/bin/env python3
"""
Operating System Detection Module

WHY: Detects operating system type, name, version, and release information.
RESPONSIBILITY: Provides OS-specific detection logic with dispatch tables.
PATTERNS: Strategy pattern for OS-specific name detection.

This module provides:
- OS type detection (Linux, Darwin, Windows)
- Friendly OS name resolution
- Version and release information
"""

import platform
from typing import Callable, Dict, Optional, Any


class OSDetector:
    """
    Detects operating system information.

    WHY: Centralizes OS detection logic for reuse across platform detection.
    RESPONSIBILITY: Detect OS type, name, version, and release.
    PATTERNS: Dispatch tables for OS-specific operations.
    """

    def __init__(self):
        """Initialize OS detector with dispatch tables."""
        # Dispatch table for OS name detection
        self._name_detectors: Dict[str, Callable[[], str]] = {
            'Linux': self._get_linux_name,
            'Darwin': self._get_darwin_name,
            'Windows': self._get_windows_name,
        }

    def detect_os_type(self) -> str:
        """
        Detect operating system type.

        WHY: Returns normalized OS type for platform-specific logic.
        PERFORMANCE: Single platform.system() call.

        Returns:
            OS type in lowercase (linux, darwin, windows)
        """
        return platform.system().lower()

    def detect_os_name(self) -> str:
        """
        Get friendly operating system name.

        WHY: Provides human-readable OS names for reporting.
        PERFORMANCE: O(1) dictionary lookup using dispatch table.

        Returns:
            Human-readable OS name (e.g., "Ubuntu 22.04", "macOS 14.0")
        """
        system = platform.system()

        # Guard clause: Use detector if available
        detector = self._name_detectors.get(system)
        if not detector:
            return system

        return detector()

    def detect_os_version(self) -> str:
        """
        Detect operating system version.

        WHY: Provides version information for compatibility checks.

        Returns:
            OS version string
        """
        return platform.version()

    def detect_os_release(self) -> str:
        """
        Detect operating system release.

        WHY: Provides release information for kernel/build identification.

        Returns:
            OS release string
        """
        return platform.release()

    def detect_os_info(self) -> Dict[str, str]:
        """
        Detect all OS information.

        WHY: Provides single call to get all OS details.

        Returns:
            Dictionary with os_type, os_name, os_version, os_release
        """
        return {
            'os_type': self.detect_os_type(),
            'os_name': self.detect_os_name(),
            'os_version': self.detect_os_version(),
            'os_release': self.detect_os_release(),
        }

    def _get_linux_name(self) -> str:
        """
        Get Linux distribution name.

        WHY: Linux has many distributions; use distro library for accurate detection.
        PERFORMANCE: Single library call with fallback.

        Returns:
            Linux distribution name
        """
        try:
            import distro
            return distro.name(pretty=True)
        except ImportError:
            return f"Linux {platform.release()}"

    def _get_darwin_name(self) -> str:
        """
        Get macOS name.

        WHY: Darwin is the underlying OS; macOS is the user-facing name.
        PERFORMANCE: Single platform.mac_ver() call.

        Returns:
            macOS version string
        """
        return f"macOS {platform.mac_ver()[0]}"

    def _get_windows_name(self) -> str:
        """
        Get Windows name.

        WHY: Provides Windows version for compatibility checks.
        PERFORMANCE: Single platform.release() call.

        Returns:
            Windows version string
        """
        return f"Windows {platform.release()}"


def detect_os_type() -> str:
    """
    Convenience function to detect OS type.

    WHY: Provides simple function interface for common use case.

    Returns:
        OS type in lowercase
    """
    detector = OSDetector()
    return detector.detect_os_type()


def detect_os_name() -> str:
    """
    Convenience function to detect OS name.

    WHY: Provides simple function interface for common use case.

    Returns:
        Human-readable OS name
    """
    detector = OSDetector()
    return detector.detect_os_name()


def detect_os_info() -> Dict[str, str]:
    """
    Convenience function to detect all OS information.

    WHY: Provides single call to get all OS details.

    Returns:
        Dictionary with os_type, os_name, os_version, os_release
    """
    detector = OSDetector()
    return {
        'os_type': detector.detect_os_type(),
        'os_name': detector.detect_os_name(),
        'os_version': detector.detect_os_version(),
        'os_release': detector.detect_os_release(),
    }
