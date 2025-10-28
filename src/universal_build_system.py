#!/usr/bin/env python3
"""
BACKWARD COMPATIBILITY WRAPPER for universal_build_system.py

WHY: This module has been refactored and moved to build_managers/ package.
     This wrapper maintains backward compatibility for existing imports while
     the codebase transitions to the new modular structure.

DEPRECATED: This module is deprecated. Use the new modular structure instead:
    OLD: from universal_build_system import UniversalBuildSystem
    NEW: from build_managers import UniversalBuildSystem

MIGRATION PATH:
    1. Update imports from universal_build_system to build_managers
    2. Update usage of enums (BuildSystem, Language, ProjectType)
    3. All functionality remains the same - just import paths changed

NEW STRUCTURE:
    build_managers/
    ├── __init__.py                    # Package exports
    ├── models.py                      # Core enums and data classes
    ├── detector.py                    # Build system detection
    ├── recommender.py                 # Build system recommendations
    ├── cli.py                         # Command-line interface
    └── universal/
        ├── __init__.py
        └── orchestrator.py            # Universal orchestration

ORIGINAL FILE: 803 lines
NEW STRUCTURE: 6 focused modules (~700 lines total)
REDUCTION: 13% reduction + improved modularity

This wrapper will be removed in a future version after all dependent code
has been updated to use the new structure.
"""

import warnings
from pathlib import Path
from typing import Optional
import logging

# Re-export all components from new location
from build_managers.models import (
    BuildSystem,
    Language,
    ProjectType,
    BuildSystemDetection,
    BuildSystemRecommendation,
    BuildResult
)
from build_managers.universal import UniversalBuildSystem

# Emit deprecation warning
warnings.warn(
    "universal_build_system module is deprecated. "
    "Use 'from build_managers import UniversalBuildSystem' instead. "
    "This wrapper will be removed in a future version.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export all public API
__all__ = [
    # Core models
    'BuildSystem',
    'Language',
    'ProjectType',
    'BuildSystemDetection',
    'BuildSystemRecommendation',
    'BuildResult',

    # Main class
    'UniversalBuildSystem',
]


# ============================================================================
# COMMAND-LINE INTERFACE (Backward Compatibility)
# ============================================================================

if __name__ == "__main__":
    # Delegate to new CLI module
    from build_managers.cli import main
    main()
