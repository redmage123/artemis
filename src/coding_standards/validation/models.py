#!/usr/bin/env python3
"""
WHY: Define data structures for validation results
RESPONSIBILITY: Immutable result models
PATTERNS: Value Object (immutable dataclass)

Validation models provide structured representations of code standards checks.
"""

from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class ValidationResult:
    """
    Result of code standards validation.

    WHY: Provides structured output for pipeline integration.
    PATTERNS: Value Object (immutable data structure).
    """
    is_valid: bool
    violation_count: int
    violations: List[Dict[str, Any]]
    files_scanned: int
    summary: str
