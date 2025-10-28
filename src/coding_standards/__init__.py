#!/usr/bin/env python3
"""
WHY: Package initialization and public API exports for coding standards.

RESPONSIBILITY:
    - Export all public components for external use
    - Maintain backward compatibility with original module
    - Provide convenient access to standards content

PATTERNS:
    - Facade pattern for simplified access
    - Explicit exports to control public API
"""

from typing import List

from .models import (
    CodingRule,
    LanguageCategory,
    LanguageStandard,
    StandardCategory,
    StandardsMetadata,
)
from .rules import (
    CODING_STANDARDS_ALL_LANGUAGES,
    RulesRepository,
    rules_repository,
)

# Public API - maintain backward compatibility
__all__: List[str] = [
    # Main constant - backward compatibility
    'CODING_STANDARDS_ALL_LANGUAGES',
    # Models
    'CodingRule',
    'LanguageCategory',
    'LanguageStandard',
    'StandardCategory',
    'StandardsMetadata',
    # Repository
    'RulesRepository',
    'rules_repository',
]

# Version information
__version__ = '2.0.0'
