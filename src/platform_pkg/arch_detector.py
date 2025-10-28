#!/usr/bin/env python3
"""
CPU Architecture Detection Module

WHY: Detects CPU architecture and hardware characteristics.
RESPONSIBILITY: Provides CPU core count, frequency, and architecture detection.
PATTERNS: Guard clauses for missing/optional information.

This module provides:
- CPU architecture detection (x86_64, arm64, aarch64)
- Physical and logical core counts
- CPU frequency detection
"""

import platform
import psutil
from typing import Dict, Any, Optional


class ArchDetector:
    """
    Detects CPU architecture and hardware information.

    WHY: Centralizes CPU/hardware detection for resource allocation decisions.
    RESPONSIBILITY: Detect CPU characteristics including cores, frequency, architecture.
    PATTERNS: Guard clauses for optional hardware information.
    """

    def detect_architecture(self) -> str:
        """
        Detect CPU architecture.

        WHY: Architecture affects binary compatibility and performance characteristics.
        PERFORMANCE: Single platform.machine() call.

        Returns:
            CPU architecture (e.g., x86_64, arm64, aarch64)
        """
        return platform.machine()

    def detect_physical_cores(self) -> int:
        """
        Detect number of physical CPU cores.

        WHY: Physical cores determine true parallel processing capability.
        PERFORMANCE: Single psutil call with fallback.

        Returns:
            Number of physical CPU cores (minimum 1)
        """
        cores = psutil.cpu_count(logical=False)
        # Guard clause: Fallback to 1 if detection fails
        if cores is None:
            return 1
        return cores

    def detect_logical_cores(self) -> int:
        """
        Detect number of logical CPU cores.

        WHY: Logical cores include hyperthreading for scheduling decisions.
        PERFORMANCE: Single psutil call with fallback.

        Returns:
            Number of logical CPU cores (minimum 1)
        """
        cores = psutil.cpu_count(logical=True)
        # Guard clause: Fallback to 1 if detection fails
        if cores is None:
            return 1
        return cores

    def detect_cpu_frequency(self) -> float:
        """
        Detect current CPU frequency in MHz.

        WHY: CPU frequency affects performance estimates.
        PERFORMANCE: Single psutil call with fallback.

        Returns:
            CPU frequency in MHz (0.0 if unavailable)
        """
        freq = psutil.cpu_freq()
        # Guard clause: Return 0.0 if detection fails
        if freq is None:
            return 0.0
        return freq.current

    def detect_all(self) -> Dict[str, Any]:
        """
        Detect all CPU/architecture information.

        WHY: Provides single call to get all CPU characteristics.

        Returns:
            Dictionary with architecture, cores, frequency
        """
        return {
            'cpu_architecture': self.detect_architecture(),
            'cpu_count_physical': self.detect_physical_cores(),
            'cpu_count_logical': self.detect_logical_cores(),
            'cpu_frequency_mhz': self.detect_cpu_frequency(),
        }


class MemoryDetector:
    """
    Detects memory (RAM) information.

    WHY: Memory availability affects resource allocation decisions.
    RESPONSIBILITY: Detect total and available memory.
    PATTERNS: Guard clauses for memory detection.
    """

    def detect_total_memory_gb(self) -> float:
        """
        Detect total system memory in GB.

        WHY: Total memory determines maximum resource allocation.
        PERFORMANCE: Single psutil call.

        Returns:
            Total memory in gigabytes
        """
        memory = psutil.virtual_memory()
        return memory.total / (1024 ** 3)

    def detect_available_memory_gb(self) -> float:
        """
        Detect available system memory in GB.

        WHY: Available memory determines current resource allocation.
        PERFORMANCE: Single psutil call.

        Returns:
            Available memory in gigabytes
        """
        memory = psutil.virtual_memory()
        return memory.available / (1024 ** 3)

    def detect_all(self) -> Dict[str, float]:
        """
        Detect all memory information.

        WHY: Provides single call to get all memory characteristics.

        Returns:
            Dictionary with total and available memory
        """
        return {
            'total_memory_gb': self.detect_total_memory_gb(),
            'available_memory_gb': self.detect_available_memory_gb(),
        }


def detect_architecture() -> str:
    """
    Convenience function to detect CPU architecture.

    WHY: Provides simple function interface for common use case.

    Returns:
        CPU architecture
    """
    detector = ArchDetector()
    return detector.detect_architecture()


def detect_cpu_info() -> Dict[str, Any]:
    """
    Convenience function to detect all CPU information.

    WHY: Provides simple function interface for common use case.

    Returns:
        Dictionary with all CPU characteristics
    """
    detector = ArchDetector()
    return detector.detect_all()


def detect_memory_info() -> Dict[str, float]:
    """
    Convenience function to detect all memory information.

    WHY: Provides simple function interface for common use case.

    Returns:
        Dictionary with all memory characteristics
    """
    detector = MemoryDetector()
    return detector.detect_all()
