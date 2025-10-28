#!/usr/bin/env python3
"""
WHY: Define data models for validation failure analysis
RESPONSIBILITY: Provide failure categories and analysis result structure
PATTERNS: Value Object (immutable enums and dataclasses)

Models:
- FailureCategory: Enum of validation failure types
- FailureAnalysis: Analysis result with category, constraints, severity
"""

from dataclasses import dataclass, field
from typing import List, Dict
from enum import Enum


class FailureCategory(Enum):
    """
    Categories of validation failures

    WHY: Enables targeted prompt refinement strategies.
         Each category requires different refinement approach.
    """
    MISSING_IMPORTS = "missing_imports"
    INCOMPLETE_IMPLEMENTATION = "incomplete_implementation"
    INCORRECT_SIGNATURE = "incorrect_signature"
    MISSING_DOCSTRINGS = "missing_docstrings"
    FORBIDDEN_PATTERNS = "forbidden_patterns"
    TEST_FAILURES = "test_failures"
    RAG_MISMATCH = "rag_mismatch"
    STREAMING_STOPPED = "streaming_stopped"
    UNKNOWN = "unknown"


@dataclass
class FailureAnalysis:
    """
    Result of failure analysis

    Attributes:
        category: Primary failure category
        constraints: List of specific constraints to add to prompt
        code_issues: Specific code locations/patterns that failed
        severity: How severe the failure is (0.0-1.0)
        retry_recommended: Whether retry with refinement is recommended
    """
    category: FailureCategory
    constraints: List[str] = field(default_factory=list)
    code_issues: List[Dict] = field(default_factory=list)
    severity: float = 0.5
    retry_recommended: bool = True

    def __post_init__(self):
        """Validate severity is in range [0.0, 1.0]"""
        # Guard clause - clamp severity to valid range
        if not 0.0 <= self.severity <= 1.0:
            self.severity = max(0.0, min(1.0, self.severity))
