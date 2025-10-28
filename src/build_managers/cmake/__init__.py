#!/usr/bin/env python3
"""
WHY: Provide public API for CMake build management
RESPONSIBILITY: Export main classes for CMake operations
PATTERNS: Facade (simplified package interface)

CMake build manager package provides enterprise-grade C/C++ build support.
"""

from build_managers.cmake.manager import CMakeManager
from build_managers.cmake.models import CMakeGenerator, BuildType, CMakeProjectInfo

__all__ = [
    'CMakeManager',
    'CMakeGenerator',
    'BuildType',
    'CMakeProjectInfo',
]
