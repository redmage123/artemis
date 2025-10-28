#!/usr/bin/env python3
"""
WHY: Aggregate validation check results
RESPONSIBILITY: Combine multiple check results into final ValidationResult
PATTERNS: Aggregator (combining results), Strategy (scoring)

Result aggregation enables consistent scoring across validators.
"""

from typing import List, Dict
from artifacts.quality.models import ValidationResult


class ResultAggregator:
    """
    Aggregates validation check results.

    WHY: Multiple validators share aggregation logic (DRY principle).
    RESPONSIBILITY: Calculate score, combine feedback, determine pass/fail.
    PATTERNS: Aggregator pattern.
    """

    @staticmethod
    def aggregate(checks: List[Dict], pass_threshold: float = 0.8) -> ValidationResult:
        """
        Aggregate check results into final ValidationResult.

        WHY: Centralizes scoring logic to ensure consistency.

        Args:
            checks: List of check dicts with 'name', 'passed', 'feedback'
            pass_threshold: Minimum score to pass (default 0.8 = 80%)

        Returns:
            ValidationResult with aggregated outcome

        Example:
            >>> checks = [
            ...     {'name': 'check1', 'passed': True, 'feedback': None},
            ...     {'name': 'check2', 'passed': False, 'feedback': 'Missing X'}
            ... ]
            >>> result = ResultAggregator.aggregate(checks)
            >>> result.score
            0.5
        """
        # Guard clause - no checks means perfect score
        if not checks:
            return ValidationResult(
                passed=True,
                score=1.0,
                criteria_results={},
                feedback=[]
            )

        # Extract criteria results
        criteria_results = {c['name']: c['passed'] for c in checks}

        # Collect feedback (filter None values)
        feedback = [c['feedback'] for c in checks if c.get('feedback')]

        # Calculate score
        passed_count = sum(1 for c in checks if c['passed'])
        score = passed_count / len(checks)

        # Determine pass/fail based on threshold
        passed = score >= pass_threshold

        return ValidationResult(
            passed=passed,
            score=score,
            criteria_results=criteria_results,
            feedback=feedback
        )
