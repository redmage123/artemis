#!/usr/bin/env python3
"""
Platform Detection Package

WHY: Provides modular platform detection and resource allocation capabilities.
RESPONSIBILITY: Export public API for platform detection.
PATTERNS: Package initialization with explicit exports.

This package provides:
- PlatformInfo: Platform information dataclass
- ResourceAllocation: Resource allocation recommendations dataclass
- PlatformDetector: Main platform detection class
- get_platform_summary: Human-readable platform summary
- OS, CPU, Memory, Disk, Python detection utilities

Usage:
    from platform_pkg import PlatformDetector, PlatformInfo, ResourceAllocation

    detector = PlatformDetector()
    info = detector.detect_platform()
    allocation = detector.calculate_resource_allocation(info)
"""

# Core models
from platform_pkg.models import PlatformInfo, ResourceAllocation

# Main detector
from platform_pkg.detector_core import PlatformDetector, get_platform_summary

# Individual detectors (for advanced use cases)
from platform_pkg.os_detector import OSDetector, detect_os_type, detect_os_name, detect_os_info
from platform_pkg.arch_detector import (
    ArchDetector,
    MemoryDetector,
    detect_architecture,
    detect_cpu_info,
    detect_memory_info,
)
from platform_pkg.env_detector import (
    DiskDetector,
    PythonDetector,
    HostnameDetector,
    detect_disk_type,
    detect_disk_info,
    detect_python_info,
    detect_hostname,
)

# Public API
__all__ = [
    # Core models
    'PlatformInfo',
    'ResourceAllocation',
    # Main detector
    'PlatformDetector',
    'get_platform_summary',
    # OS detection
    'OSDetector',
    'detect_os_type',
    'detect_os_name',
    'detect_os_info',
    # CPU/Memory detection
    'ArchDetector',
    'MemoryDetector',
    'detect_architecture',
    'detect_cpu_info',
    'detect_memory_info',
    # Environment detection
    'DiskDetector',
    'PythonDetector',
    'HostnameDetector',
    'detect_disk_type',
    'detect_disk_info',
    'detect_python_info',
    'detect_hostname',
]

# Package metadata
__version__ = '1.0.0'
__author__ = 'Artemis Team'
__description__ = 'Platform detection and resource allocation module'
