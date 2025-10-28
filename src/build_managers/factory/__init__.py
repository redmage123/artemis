#!/usr/bin/env python3
"""
WHY: Provide public API for build manager factory
RESPONSIBILITY: Export factory classes and utilities
PATTERNS: Facade (simplified package interface)

Factory package provides dynamic build manager creation and auto-detection.
"""

from build_managers.factory.enums import BuildSystem
from build_managers.factory.factory import BuildManagerFactory, get_build_manager_factory
from build_managers.factory.decorators import register_build_manager

__all__ = [
    'BuildSystem',
    'BuildManagerFactory',
    'get_build_manager_factory',
    'register_build_manager',
]
