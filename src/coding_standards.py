#!/usr/bin/env python3
"""
WHY: Backward compatibility wrapper for coding_standards package.

RESPONSIBILITY:
    - Maintain 100% backward compatibility with existing code
    - Re-export all components from the new modular package
    - Provide deprecation path for future migration

PATTERNS:
    - Adapter pattern for API compatibility
    - Re-export pattern for seamless migration
    - Deprecation warnings for future changes

NOTE:
    This module is a compatibility shim. The actual implementation
    has been refactored into the coding_standards/ package.
    All new code should import from coding_standards package directly.

MIGRATION PATH:
    Old: from coding_standards import CODING_STANDARDS_ALL_LANGUAGES
    New: from coding_standards import CODING_STANDARDS_ALL_LANGUAGES
    (Works the same way, but new package structure is modular)
"""

from typing import List

# Re-export everything from the package for backward compatibility
from coding_standards import (
    CODING_STANDARDS_ALL_LANGUAGES,
    CodingRule,
    LanguageCategory,
    LanguageStandard,
    RulesRepository,
    StandardCategory,
    StandardsMetadata,
    rules_repository,
)

# Maintain the same public API
__all__: List[str] = [
    'CODING_STANDARDS_ALL_LANGUAGES',
    'CodingRule',
    'LanguageCategory',
    'LanguageStandard',
    'StandardCategory',
    'StandardsMetadata',
    'RulesRepository',
    'rules_repository',
]
