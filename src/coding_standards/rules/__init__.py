#!/usr/bin/env python3
"""
Coding standards rules package.

WHY: Provides a clean, modular API for accessing coding standards and rules.

RESPONSIBILITY:
    - Export public API for coding standards access
    - Maintain backward compatibility with original rules.py
    - Provide organized access to rules repository and constants

PATTERNS:
    - Facade pattern - simplifies access to underlying modules
    - Single point of entry for package
    - Explicit public API exports

Example:
    from coding_standards.rules import rules_repository, RulesRepository
    from coding_standards.rules import CODING_STANDARDS_ALL_LANGUAGES

    # Use singleton instance
    standards = rules_repository.get_all_standards()

    # Or create new instance
    repo = RulesRepository()
    python_standards = repo.get_standards_for_language('python')
"""

# Import from submodules for public API
from .constants import (
    CODING_STANDARDS_ALL_LANGUAGES,
    SUPPORTED_LANGUAGES,
)
from .repository import (
    RulesRepository,
    rules_repository,
)

# Explicit public API
__all__ = [
    # Constants
    'CODING_STANDARDS_ALL_LANGUAGES',
    'SUPPORTED_LANGUAGES',

    # Repository class and singleton
    'RulesRepository',
    'rules_repository',
]
