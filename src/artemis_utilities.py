#!/usr/bin/env python3
"""
Module: artemis_utilities.py (Backward Compatibility Wrapper)

WHY: Maintains backward compatibility while migrating to modular utilities/ package.
     Allows existing code to continue using "from artemis_utilities import X"
     without breaking changes.

RESPONSIBILITY:
- Re-export all utility classes and functions from utilities/ package
- Provide same API as original monolithic artemis_utilities.py
- Enable gradual migration to new modular structure

PATTERNS:
- Facade Pattern: Single entry point delegates to specialized modules
- Adapter Pattern: Adapts old imports to new module structure
- Backward Compatibility Pattern: Maintains existing API during refactoring

Migration Path:
1. Old code: from artemis_utilities import RetryStrategy (still works)
2. New code: from utilities.retry_utilities import RetryStrategy (preferred)
3. Package imports: from utilities import RetryStrategy (also works)

Original file: 755 lines
This wrapper: ~100 lines
Reduction: 87% (655 lines eliminated through modularization)

Integration: Used by ALL pipeline stages, developer agents, and orchestrator components.
             Core shared infrastructure for the entire Artemis system.
"""

# Import everything from utilities package for backward compatibility
from utilities import (
    # Retry utilities
    RetryConfig,
    RetryStrategy,
    retry_with_backoff,
    retry_operation,

    # Validation utilities
    Validator,
    validate_required,

    # Error handling utilities
    ErrorHandler,
    safe_execute,

    # File operation utilities
    FileOperations,
)

# Type imports for backward compatibility
from typing import TypeVar

T = TypeVar('T')


# Expose all utilities at module level for backward compatibility
__all__ = [
    # Type variables
    'T',

    # Retry utilities
    'RetryConfig',
    'RetryStrategy',
    'retry_with_backoff',
    'retry_operation',

    # Validation utilities
    'Validator',
    'validate_required',

    # Error handling utilities
    'ErrorHandler',
    'safe_execute',

    # File operation utilities
    'FileOperations',
]
