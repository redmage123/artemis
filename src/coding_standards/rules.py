#!/usr/bin/env python3
"""
Backward compatibility wrapper for coding_standards.rules module.

WHY: Maintains 100% backward compatibility after refactoring into package.

RESPONSIBILITY:
    - Re-export all public API from rules package
    - Ensure existing imports continue to work unchanged
    - Provide deprecation path for future migration

PATTERNS:
    - Facade pattern for backward compatibility
    - Re-export pattern to maintain API surface
    - Zero-cost wrapper (just imports, no logic)

MIGRATION NOTE:
    This file is a compatibility wrapper. The actual implementation has been
    refactored into the coding_standards/rules/ package for better modularity.

    Old imports (still work):
        from coding_standards.rules import RulesRepository
        from coding_standards.rules import CODING_STANDARDS_ALL_LANGUAGES

    New imports (recommended):
        from coding_standards.rules import RulesRepository
        from coding_standards.rules import CODING_STANDARDS_ALL_LANGUAGES

    Both import paths are identical and work the same way. The refactoring was
    internal only - the public API remains unchanged.
"""

# Re-export everything from the rules package for backward compatibility
# This ensures existing code continues to work without changes
from coding_standards.rules import (
    CODING_STANDARDS_ALL_LANGUAGES,
    SUPPORTED_LANGUAGES,
    RulesRepository,
    rules_repository,
)

# Preserve __all__ for explicit API
__all__ = [
    'CODING_STANDARDS_ALL_LANGUAGES',
    'SUPPORTED_LANGUAGES',
    'RulesRepository',
    'rules_repository',
]
