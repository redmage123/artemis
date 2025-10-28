#!/usr/bin/env python3
"""
WHY: Data models and enumerations for coding standards representation.

RESPONSIBILITY:
    - Define data structures for coding rules and standards
    - Provide enumerations for programming languages and rule categories
    - Support type-safe access to coding standard components

PATTERNS:
    - Enum pattern for fixed sets of values
    - Dataclass pattern for immutable data containers
    - Type hints for all data structures
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Dict, Any, Optional


class LanguageCategory(Enum):
    """Programming language categories for standards application."""
    COMPILED = auto()
    INTERPRETED = auto()
    FUNCTIONAL = auto()
    SYSTEMS = auto()
    WEB = auto()
    DATABASE = auto()
    MARKUP = auto()


class StandardCategory(Enum):
    """Categories of coding standards."""
    API_VERIFICATION = auto()
    EXCEPTION_HANDLING = auto()
    SOLID_PRINCIPLES = auto()
    ANTI_PATTERNS = auto()
    FUNCTIONAL_PROGRAMMING = auto()
    CODE_QUALITY = auto()
    DESIGN_PATTERNS = auto()
    ARCHITECTURE = auto()
    ERROR_RESILIENCE = auto()
    CONCURRENCY = auto()
    TESTING = auto()
    SECURITY = auto()
    OBSERVABILITY = auto()
    API_DESIGN = auto()
    DATA_MANAGEMENT = auto()
    PERFORMANCE = auto()
    LANGUAGE_SPECIFIC = auto()


@dataclass(frozen=True)
class CodingRule:
    """Immutable representation of a single coding rule."""
    category: StandardCategory
    title: str
    description: str
    priority: int  # 1 (critical) to 5 (nice-to-have)
    applies_to: List[str]  # Language names or 'ALL'
    examples: List[str]


@dataclass(frozen=True)
class LanguageStandard:
    """Language-specific coding standards."""
    language: str
    rules: List[CodingRule]
    best_practices: List[str]
    anti_patterns: List[str]
    tooling: List[str]


@dataclass(frozen=True)
class StandardsMetadata:
    """Metadata about the coding standards collection."""
    version: str
    total_languages: int
    total_rules: int
    last_updated: str
