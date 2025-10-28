#!/usr/bin/env python3
"""
Environment Detection Module

WHY: Detects disk type, Python environment, and system hostname.
RESPONSIBILITY: Provides disk I/O characteristics and Python runtime information.
PATTERNS: Strategy pattern with dispatch tables for OS-specific disk detection.

This module provides:
- Disk type detection (SSD, HDD, Unknown)
- Disk space detection
- Python version and implementation
- Hostname detection
"""

import platform
import psutil
import subprocess
from pathlib import Path
from typing import Dict, Any, Callable, Optional


class DiskDetector:
    """
    Detects disk type and storage information.

    WHY: Disk type (SSD vs HDD) affects I/O performance recommendations.
    RESPONSIBILITY: Detect disk type and available storage.
    PATTERNS: Strategy pattern with OS-specific detection methods via dispatch table.
    """

    def __init__(self):
        """Initialize disk detector with OS-specific dispatch table."""
        # Dispatch table: Map OS to disk type detection method
        self._disk_type_detectors: Dict[str, Callable[[], str]] = {
            'Linux': self._detect_disk_type_linux,
            'Darwin': self._detect_disk_type_macos,
            'Windows': self._detect_disk_type_windows,
        }

    def detect_disk_type(self) -> str:
        """
        Detect if disk is SSD or HDD.

        WHY: SSD vs HDD affects I/O performance recommendations.
        PERFORMANCE: O(1) dictionary lookup, early return on detection.

        Returns:
            "SSD", "HDD", or "Unknown"
        """
        try:
            system = platform.system()
            detector = self._disk_type_detectors.get(system)

            # Guard clause: No detector for this OS
            if not detector:
                return "Unknown"

            return detector()

        except Exception:
            # Catch all detection errors - return Unknown rather than crash
            return "Unknown"

    def detect_total_disk_gb(self) -> float:
        """
        Detect total disk space in GB.

        WHY: Total disk space determines storage capacity.
        PERFORMANCE: Single psutil call.

        Returns:
            Total disk space in gigabytes
        """
        disk = psutil.disk_usage('/')
        return disk.total / (1024 ** 3)

    def detect_available_disk_gb(self) -> float:
        """
        Detect available disk space in GB.

        WHY: Available disk space determines storage operations.
        PERFORMANCE: Single psutil call.

        Returns:
            Available disk space in gigabytes
        """
        disk = psutil.disk_usage('/')
        return disk.free / (1024 ** 3)

    def detect_all(self) -> Dict[str, Any]:
        """
        Detect all disk information.

        WHY: Provides single call to get all disk characteristics.

        Returns:
            Dictionary with total_disk_gb, available_disk_gb, disk_type
        """
        return {
            'total_disk_gb': self.detect_total_disk_gb(),
            'available_disk_gb': self.detect_available_disk_gb(),
            'disk_type': self.detect_disk_type(),
        }

    def _detect_disk_type_linux(self) -> str:
        """
        Detect disk type on Linux systems.

        WHY: Reads /sys/block/*/queue/rotational (0=SSD, 1=HDD).
        PERFORMANCE: Early continue for non-disk devices, early return on first match.

        Returns:
            "SSD", "HDD", or "Unknown"
        """
        # Guard clause: /sys/block doesn't exist
        sys_block = Path("/sys/block")
        if not sys_block.exists():
            return "Unknown"

        for device in sys_block.iterdir():
            # Guard clause: Skip non-disk devices
            if not device.name.startswith(('sd', 'nvme', 'vd')):
                continue

            rotational_file = device / "queue" / "rotational"

            # Guard clause: Skip if rotational file doesn't exist
            if not rotational_file.exists():
                continue

            # Read rotational status (0=SSD, 1=HDD)
            with open(rotational_file) as f:
                content = f.read().strip()
                # Early return: Found disk type
                return "SSD" if content == "0" else "HDD"

        # No disk found
        return "Unknown"

    def _detect_disk_type_macos(self) -> str:
        """
        Detect disk type on macOS systems.

        WHY: Uses diskutil command to query disk information.
        PERFORMANCE: Single subprocess call, early returns for each case.

        Returns:
            "SSD", "HDD", or "Unknown"
        """
        try:
            result = subprocess.run(
                ["diskutil", "info", "/"],
                capture_output=True,
                text=True,
                timeout=5
            )

            # Early return: SSD detected
            if "Solid State: Yes" in result.stdout:
                return "SSD"

            # Early return: HDD detected
            if "Solid State: No" in result.stdout:
                return "HDD"

            # Default: Unknown disk type
            return "Unknown"

        except Exception:
            return "Unknown"

    def _detect_disk_type_windows(self) -> str:
        """
        Detect disk type on Windows systems.

        WHY: Uses PowerShell Get-PhysicalDisk to query disk media type.
        PERFORMANCE: Single subprocess call, early returns for each case.

        Returns:
            "SSD", "HDD", or "Unknown"
        """
        try:
            result = subprocess.run(
                ["powershell", "-Command", "Get-PhysicalDisk | Select-Object MediaType"],
                capture_output=True,
                text=True,
                timeout=5
            )

            # Early return: SSD detected
            if "SSD" in result.stdout:
                return "SSD"

            # Early return: HDD detected
            if "HDD" in result.stdout:
                return "HDD"

            # Default: Unknown disk type
            return "Unknown"

        except Exception:
            return "Unknown"


class PythonDetector:
    """
    Detects Python runtime information.

    WHY: Python version affects feature compatibility and performance.
    RESPONSIBILITY: Detect Python version and implementation.
    """

    def detect_python_version(self) -> str:
        """
        Detect Python version.

        WHY: Version determines available language features.
        PERFORMANCE: Single platform call.

        Returns:
            Python version (e.g., "3.11.5")
        """
        return platform.python_version()

    def detect_python_implementation(self) -> str:
        """
        Detect Python implementation.

        WHY: Implementation (CPython, PyPy) affects performance characteristics.
        PERFORMANCE: Single platform call.

        Returns:
            Python implementation (e.g., "CPython", "PyPy")
        """
        return platform.python_implementation()

    def detect_all(self) -> Dict[str, str]:
        """
        Detect all Python information.

        WHY: Provides single call to get all Python characteristics.

        Returns:
            Dictionary with python_version and python_implementation
        """
        return {
            'python_version': self.detect_python_version(),
            'python_implementation': self.detect_python_implementation(),
        }


class HostnameDetector:
    """
    Detects system hostname.

    WHY: Hostname uniquely identifies the system.
    RESPONSIBILITY: Detect system hostname.
    """

    def detect_hostname(self) -> str:
        """
        Detect system hostname.

        WHY: Hostname provides system identification.
        PERFORMANCE: Single platform call.

        Returns:
            System hostname
        """
        return platform.node()


def detect_disk_type() -> str:
    """
    Convenience function to detect disk type.

    WHY: Provides simple function interface for common use case.

    Returns:
        Disk type (SSD, HDD, Unknown)
    """
    detector = DiskDetector()
    return detector.detect_disk_type()


def detect_disk_info() -> Dict[str, Any]:
    """
    Convenience function to detect all disk information.

    WHY: Provides simple function interface for common use case.

    Returns:
        Dictionary with all disk characteristics
    """
    detector = DiskDetector()
    return detector.detect_all()


def detect_python_info() -> Dict[str, str]:
    """
    Convenience function to detect all Python information.

    WHY: Provides simple function interface for common use case.

    Returns:
        Dictionary with all Python characteristics
    """
    detector = PythonDetector()
    return detector.detect_all()


def detect_hostname() -> str:
    """
    Convenience function to detect hostname.

    WHY: Provides simple function interface for common use case.

    Returns:
        System hostname
    """
    detector = HostnameDetector()
    return detector.detect_hostname()
