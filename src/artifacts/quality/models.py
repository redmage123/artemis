#!/usr/bin/env python3
"""
WHY: Define validation result model
RESPONSIBILITY: Represent validation outcome with score and feedback
PATTERNS: Value Object (immutable validation result)

ValidationResult provides structured validation outcome.
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class ValidationResult:
    """
    Result of quality validation.

    WHY: Structured result enables consistent validation reporting.
    RESPONSIBILITY: Carry validation outcome, score, criteria, and feedback.
    PATTERNS: Value Object (immutable data).
    """
    passed: bool
    score: float  # 0.0 to 1.0
    criteria_results: Dict[str, bool]  # criterion -> passed
    feedback: List[str]  # Specific feedback items

    def __str__(self) -> str:
        """
        String representation.

        WHY: Human-readable validation status.

        Returns:
            Status string with score
        """
        status = "✅ PASSED" if self.passed else "❌ FAILED"
        return f"{status} (score: {self.score:.2f})"
