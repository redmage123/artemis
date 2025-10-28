#!/usr/bin/env python3
"""
Module: artemis_services.py (DEPRECATED - Use services.core instead)

BACKWARD COMPATIBILITY WRAPPER

Purpose: Maintains backward compatibility for existing imports while code migrates
         to the new modular services.core package structure.

Why: Allows gradual migration to new modular structure without breaking existing code.
     Preserves the SOLID principles mentioned in the original docstring while
     pointing to the new, more maintainable implementation.

DEPRECATION NOTICE:
This module is deprecated and will be removed in a future version.
Please update your imports to use:
    from services.core import TestRunner, HTMLValidator, PipelineLogger, FileManager

Migration Status: Phase 1 - Core services moved to src/services/core/
Next Steps: Update all imports across codebase to use new location.

REFACTORING SUMMARY:
- Original file: 283 lines (4 classes in one file)
- New structure: 4 modules + 1 package init (modular, focused)
- Line reduction per module: ~70-100 lines each (better maintainability)
- Patterns applied:
  * Service Layer pattern
  * Factory Method pattern
  * Service Locator pattern
  * Interface Segregation
  * Dependency Injection

ARCHITECTURE IMPROVEMENTS:
1. Each service in its own module (Single Responsibility)
2. Enhanced documentation (WHY/RESPONSIBILITY/PATTERNS headers)
3. Guard clauses throughout (max 1 level nesting)
4. Dispatch tables for log levels and parsers (no if/elif chains)
5. Factory functions for dependency injection
6. Service registry for centralized management
7. Complete type hints on all methods
8. Extended functionality (strict validation, line operations, etc.)

NEW FEATURES IN REFACTORED VERSION:
- TestRunner: Configurable pytest arguments, better error handling
- HTMLValidator: Strict validation mode, multiple parser support
- PipelineLogger: Extended log levels (SUCCESS, STAGE, etc.), custom formatters
- FileManager: Line operations, append, file existence checks, size queries

Patterns:
- Facade Pattern: Re-exports services from new location
- Adapter Pattern: Provides compatibility shim during migration
- Proxy Pattern: Transparent forwarding to new implementations
"""

import warnings

# Import from new location and re-export
from services.core import (
    TestRunner,
    HTMLValidator,
    PipelineLogger,
    FileManager,
    create_test_runner,
    create_html_validator,
    create_logger,
    create_silent_logger,
    create_file_manager,
    ServiceRegistry,
    create_default_services,
    initialize_services
)


# Issue deprecation warning on import
def _issue_deprecation_warning():
    """Issue deprecation warning when this module is imported."""
    warnings.warn(
        "artemis_services.py is deprecated. "
        "Please use 'from services.core import TestRunner, HTMLValidator, "
        "PipelineLogger, FileManager' instead. "
        "This module will be removed in a future version.",
        DeprecationWarning,
        stacklevel=3
    )


# Issue warning on module import
_issue_deprecation_warning()


# Export for backward compatibility
__all__ = [
    # Original service classes (100% compatible)
    "TestRunner",
    "HTMLValidator",
    "PipelineLogger",
    "FileManager",

    # New factory functions (optional, for enhanced usage)
    "create_test_runner",
    "create_html_validator",
    "create_logger",
    "create_silent_logger",
    "create_file_manager",

    # New service management (optional, for advanced usage)
    "ServiceRegistry",
    "create_default_services",
    "initialize_services",
]


# Migration guide for developers
_MIGRATION_GUIDE = """
MIGRATION GUIDE: artemis_services.py -> services.core

OLD IMPORT (deprecated):
    from artemis_services import TestRunner, PipelineLogger, FileManager

NEW IMPORT (recommended):
    from services.core import TestRunner, PipelineLogger, FileManager

BENEFITS OF MIGRATION:
1. Modular structure (easier to navigate and maintain)
2. Enhanced features (strict validation, custom formatters, etc.)
3. Better documentation (WHY/RESPONSIBILITY/PATTERNS headers)
4. Improved testability (factory functions, service registry)
5. Future-proof (new features will only be in services.core)

STEP-BY-STEP MIGRATION:
1. Replace import statement (see above)
2. Code works unchanged (100% backward compatible)
3. Optionally use new features:
   - Factory functions for dependency injection
   - ServiceRegistry for centralized service management
   - Enhanced service capabilities (strict mode, etc.)

EXAMPLE - BASIC MIGRATION:
    # Before
    from artemis_services import PipelineLogger
    logger = PipelineLogger(verbose=True)

    # After
    from services.core import PipelineLogger
    logger = PipelineLogger(verbose=True)

EXAMPLE - USING NEW FEATURES:
    # Use factory functions
    from services.core import create_logger
    logger = create_logger(verbose=True)

    # Use service registry
    from services.core import initialize_services, ServiceRegistry
    initialize_services(verbose=True)
    logger = ServiceRegistry.get('logger')
    logger.info("Services initialized!")

For questions or issues, consult:
- services/core/__init__.py (package documentation)
- Individual module files (detailed implementation docs)
- REFACTORING_REPORT.md (this refactoring's metrics and patterns)
"""


def print_migration_guide():
    """Print migration guide to console."""
    print(_MIGRATION_GUIDE)


# Add migration guide to module docstring for help()
__doc__ += "\n\n" + _MIGRATION_GUIDE
