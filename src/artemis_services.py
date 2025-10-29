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
from services.core import TestRunner, HTMLValidator, PipelineLogger, FileManager, create_test_runner, create_html_validator, create_logger, create_silent_logger, create_file_manager, ServiceRegistry, create_default_services, initialize_services

def _issue_deprecation_warning():
    """Issue deprecation warning when this module is imported."""
    warnings.warn("artemis_services.py is deprecated. Please use 'from services.core import TestRunner, HTMLValidator, PipelineLogger, FileManager' instead. This module will be removed in a future version.", DeprecationWarning, stacklevel=3)
_issue_deprecation_warning()
__all__ = ['TestRunner', 'HTMLValidator', 'PipelineLogger', 'FileManager', 'create_test_runner', 'create_html_validator', 'create_logger', 'create_silent_logger', 'create_file_manager', 'ServiceRegistry', 'create_default_services', 'initialize_services']
_MIGRATION_GUIDE = '\nMIGRATION GUIDE: artemis_services.py -> services.core\n\nOLD IMPORT (deprecated):\n    from artemis_services import TestRunner, PipelineLogger, FileManager\n\nNEW IMPORT (recommended):\n    from services.core import TestRunner, PipelineLogger, FileManager\n\nBENEFITS OF MIGRATION:\n1. Modular structure (easier to navigate and maintain)\n2. Enhanced features (strict validation, custom formatters, etc.)\n3. Better documentation (WHY/RESPONSIBILITY/PATTERNS headers)\n4. Improved testability (factory functions, service registry)\n5. Future-proof (new features will only be in services.core)\n\nSTEP-BY-STEP MIGRATION:\n1. Replace import statement (see above)\n2. Code works unchanged (100% backward compatible)\n3. Optionally use new features:\n   - Factory functions for dependency injection\n   - ServiceRegistry for centralized service management\n   - Enhanced service capabilities (strict mode, etc.)\n\nEXAMPLE - BASIC MIGRATION:\n    # Before\n    from artemis_services import PipelineLogger\n    logger = PipelineLogger(verbose=True)\n\n    # After\n    from services.core import PipelineLogger\n    logger = PipelineLogger(verbose=True)\n\nEXAMPLE - USING NEW FEATURES:\n    # Use factory functions\n    from services.core import create_logger\n    logger = create_logger(verbose=True)\n\n    # Use service registry\n    from services.core import initialize_services, ServiceRegistry\n    initialize_services(verbose=True)\n    logger = ServiceRegistry.get(\'logger\')\n    logger.info("Services initialized!")\n\nFor questions or issues, consult:\n- services/core/__init__.py (package documentation)\n- Individual module files (detailed implementation docs)\n- REFACTORING_REPORT.md (this refactoring\'s metrics and patterns)\n'

def print_migration_guide():
    """Print migration guide to console."""
    
    logger.log(_MIGRATION_GUIDE, 'INFO')
__doc__ += '\n\n' + _MIGRATION_GUIDE