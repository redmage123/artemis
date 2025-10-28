#!/usr/bin/env python3
"""
BACKWARD COMPATIBILITY WRAPPER

This module maintains backward compatibility while the codebase migrates
to the new modular structure in build_managers/factory/.

All functionality has been refactored into:
- build_managers/factory/enums.py - BuildSystem enum
- build_managers/factory/registry.py - BuildManagerRegistry
- build_managers/factory/detector.py - BuildSystemDetector with detection map
- build_managers/factory/factory.py - BuildManagerFactory (Singleton + Factory)
- build_managers/factory/decorators.py - register_build_manager decorator

To migrate your code:
    OLD: from build_manager_factory import BuildManagerFactory, BuildSystem
    NEW: from build_managers.factory import BuildManagerFactory, BuildSystem

No breaking changes - all imports remain identical.
"""

# Re-export all public APIs from the modular package
from build_managers.factory import (
    BuildSystem,
    BuildManagerFactory,
    get_build_manager_factory,
    register_build_manager,
)

__all__ = [
    'BuildSystem',
    'BuildManagerFactory',
    'get_build_manager_factory',
    'register_build_manager',
]
