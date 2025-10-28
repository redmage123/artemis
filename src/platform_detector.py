#!/usr/bin/env python3
"""
Platform Detection and Resource Allocation Module (Backward Compatibility Wrapper)

WHY: Maintains backward compatibility while delegating to refactored platform_pkg/ package.
RESPONSIBILITY: Re-export all public APIs from platform_pkg package.
PATTERNS: Facade pattern for backward compatibility.

MIGRATION NOTE:
This module is a backward compatibility wrapper. All implementation has been
moved to the platform_pkg/ package. Please update imports to use:
    from platform_pkg import PlatformDetector, PlatformInfo, ResourceAllocation

Original file: platform_detector.py.backup (508 lines)
Wrapper: platform_detector.py (current file)
Refactored package: platform_pkg/
"""

# Import all public APIs from refactored platform_pkg package
from platform_pkg.models import PlatformInfo, ResourceAllocation
from platform_pkg.detector_core import PlatformDetector, get_platform_summary

# Re-export for backward compatibility
__all__ = [
    'PlatformInfo',
    'ResourceAllocation',
    'PlatformDetector',
    'get_platform_summary',
]
