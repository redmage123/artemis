#!/usr/bin/env python3
"""
WHY: Categorize validation failures using pattern matching
RESPONSIBILITY: Map error messages to failure categories using Strategy pattern
PATTERNS: Strategy (pattern→category mapping), Compiled Regex (performance)

Categorizer uses dispatch table to avoid if/elif chains:
- Compiled regex patterns for performance
- Early return on first match
- O(1) lookup for category severity
"""

import re
from typing import List, Dict
from validation.models import FailureCategory


class FailureCategorizer:
    """
    Categorizes validation failures using pattern matching

    Uses Strategy pattern with regex-based dispatch table.
    """

    # Strategy pattern: Failure pattern → Category mapping (no if/elif)
    FAILURE_PATTERNS = {
        r'import.*not found': FailureCategory.MISSING_IMPORTS,
        r'missing import': FailureCategory.MISSING_IMPORTS,
        r'TODO|FIXME|pass\s*$': FailureCategory.INCOMPLETE_IMPLEMENTATION,
        r'NotImplementedError': FailureCategory.INCOMPLETE_IMPLEMENTATION,
        r'signature.*mismatch': FailureCategory.INCORRECT_SIGNATURE,
        r'missing.*parameter': FailureCategory.INCORRECT_SIGNATURE,
        r'missing.*docstring': FailureCategory.MISSING_DOCSTRINGS,
        r'eval\(|exec\(': FailureCategory.FORBIDDEN_PATTERNS,
        r'test.*failed': FailureCategory.TEST_FAILURES,
        r'similarity.*low': FailureCategory.RAG_MISMATCH,
        r'streaming.*stopped': FailureCategory.STREAMING_STOPPED,
    }

    # Severity scores for each category (Strategy pattern)
    CATEGORY_SEVERITY = {
        FailureCategory.FORBIDDEN_PATTERNS: 1.0,  # Critical
        FailureCategory.STREAMING_STOPPED: 0.9,   # Very high
        FailureCategory.MISSING_IMPORTS: 0.7,     # High
        FailureCategory.INCORRECT_SIGNATURE: 0.7, # High
        FailureCategory.INCOMPLETE_IMPLEMENTATION: 0.6,  # Medium-high
        FailureCategory.TEST_FAILURES: 0.5,       # Medium
        FailureCategory.MISSING_DOCSTRINGS: 0.3,  # Low
        FailureCategory.RAG_MISMATCH: 0.4,        # Medium-low
        FailureCategory.UNKNOWN: 0.5,             # Medium
    }

    def __init__(self):
        """Initialize categorizer with compiled regex patterns"""
        # Compile regex patterns once for performance
        self._compiled_patterns = {
            re.compile(pattern, re.IGNORECASE): category
            for pattern, category in self.FAILURE_PATTERNS.items()
        }

    def categorize(self, error_messages: List[str]) -> FailureCategory:
        """
        Categorize failure based on error messages

        Args:
            error_messages: List of error messages from validation

        Returns:
            FailureCategory enum value
        """
        # Guard clause - check if messages exist
        if not error_messages:
            return FailureCategory.UNKNOWN

        # Join messages for pattern matching (performance: single regex search)
        combined_messages = " ".join(error_messages).lower()

        # Strategy pattern: Check each pattern (early return on first match)
        for pattern, category in self._compiled_patterns.items():
            if pattern.search(combined_messages):
                return category

        # Default category if no pattern matches
        return FailureCategory.UNKNOWN

    def get_severity(self, category: FailureCategory) -> float:
        """
        Get severity score for category

        Args:
            category: Failure category

        Returns:
            Severity score (0.0-1.0)
        """
        return self.CATEGORY_SEVERITY.get(category, 0.5)

    def should_retry(self, category: FailureCategory, severity: float) -> bool:
        """
        Determine if retry with refinement is recommended

        Args:
            category: Failure category
            severity: Severity score (0.0-1.0)

        Returns:
            True if retry is recommended
        """
        # Guard clause - don't retry unknown failures
        if category == FailureCategory.UNKNOWN:
            return False

        # Retry if severity is below threshold (not catastrophic)
        return severity < 0.95
