#!/usr/bin/env python3
"""
Architecture Stage - Backward Compatibility Wrapper

WHY: Maintain backward compatibility with existing code
RESPONSIBILITY: Re-export refactored components
PATTERNS: Facade Pattern, Deprecation Warning

This file provides backward compatibility for code that imports from
the old architecture_stage.py file. All functionality has been moved
to the stages/architecture/ package.

DEPRECATED: Import from stages.architecture instead
"""

import warnings

# Re-export all components from the refactored package
from stages.architecture import (
    ArchitectureStage,
    ADRFileManager,
    ADRGenerator,
    UserStoryGenerator,
    KGArchitectureStorage,
    RAGArchitectureStorage,
)

# Show deprecation warning when this module is imported
warnings.warn(
    "Importing from architecture_stage.py is deprecated. "
    "Please import from stages.architecture instead.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = [
    'ArchitectureStage',
    'ADRFileManager',
    'ADRGenerator',
    'UserStoryGenerator',
    'KGArchitectureStorage',
    'RAGArchitectureStorage',
]
