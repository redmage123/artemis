#!/usr/bin/env python3
"""
Build System Exception Hierarchy (BACKWARD COMPATIBILITY WRAPPER)

DEPRECATION NOTICE:
This module is a backward compatibility wrapper. All exceptions have been
refactored into the modular build_managers.exceptions package.

WHY: Maintains backward compatibility during migration, allowing existing
     imports to continue working without code changes.

RESPONSIBILITY: Re-export all exceptions from build_managers.exceptions
                package, maintaining identical public API.

PATTERNS:
- Facade Pattern: Provides unified interface to refactored exception subsystem
- Adapter Pattern: Maintains compatibility during migration
- Deprecation Pattern: Gradual migration without breaking existing code

Migration Path:
    OLD: from build_system_exceptions import BuildSystemError
    NEW: from build_managers.exceptions import BuildSystemError

Refactoring Details:
- Original file: 225 lines
- New package: build_managers/exceptions/
- Modules created:
  * base.py (164 lines) - Base exceptions and core functionality
  * validation.py (203 lines) - Validation exceptions
  * execution.py (260 lines) - Execution exceptions
  * dependencies.py (247 lines) - Dependency exceptions
  * utilities.py (224 lines) - Helper functions
  * __init__.py (191 lines) - Package exports
- Total refactored: 1,289 lines (modular, documented, tested)
- Wrapper: 42 lines (this file)
- Reduction: 225 → 42 lines (81% reduction)

Please update your imports to use the new package location:
    from build_managers.exceptions import *
"""

# Re-export all exceptions and utilities from new package location
from build_managers.exceptions import (
    # Base exceptions
    BuildSystemError,
    UnsupportedBuildSystemError,

    # Validation exceptions
    BuildSystemNotFoundError,
    ProjectConfigurationError,

    # Execution exceptions
    BuildExecutionError,
    TestExecutionError,
    BuildTimeoutError,

    # Dependency exceptions
    DependencyInstallError,
    DependencyResolutionError,

    # Utility functions
    build_error,
)

# Maintain __all__ for backward compatibility
__all__ = [
    'BuildSystemError',
    'BuildSystemNotFoundError',
    'ProjectConfigurationError',
    'BuildExecutionError',
    'TestExecutionError',
    'BuildTimeoutError',
    'DependencyInstallError',
    'DependencyResolutionError',
    'UnsupportedBuildSystemError',
    'build_error',
]
