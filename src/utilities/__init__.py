#!/usr/bin/env python3
"""
Package: utilities

WHY: Modular utilities package providing reusable cross-cutting concerns.
     Extracted from monolithic artemis_utilities.py (755 lines) to improve
     maintainability, testability, and adherence to Single Responsibility Principle.

RESPONSIBILITY:
- Export all utility classes and functions for backward compatibility
- Provide clean package interface for utility imports
- Support both old-style imports (from artemis_utilities) and new-style imports
  (from utilities.retry_utilities)

PATTERNS:
- Facade Pattern: Package interface hides internal module structure
- Namespace Pattern: Organized imports by responsibility
- Backward Compatibility Pattern: Re-exports maintain existing API

Benefits:
- Focused modules (~150-250 lines each) vs monolithic file (755 lines)
- Easier to test individual utility components
- Clear separation of concerns (retry, validation, error handling, file ops)
- Maintains backward compatibility with existing code

Integration: Used by ALL pipeline stages, developer agents, and orchestrator components.
             Core shared infrastructure for the entire Artemis system.
"""

# Retry utilities
from utilities.retry_utilities import (
    RetryConfig,
    RetryStrategy,
    retry_with_backoff,
    retry_operation
)

# Validation utilities
from utilities.validation_utilities import (
    Validator,
    validate_required
)

# Error handling utilities
from utilities.error_utilities import (
    ErrorHandler,
    safe_execute
)

# File operation utilities
from utilities.file_utilities import (
    FileOperations
)


# Expose all utilities at package level for backward compatibility
__all__ = [
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
