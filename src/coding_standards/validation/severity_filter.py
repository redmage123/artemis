#!/usr/bin/env python3
"""
WHY: Filter violations by severity threshold
RESPONSIBILITY: Apply severity-based filtering
PATTERNS: Filter (predicate-based selection), Dispatch Table

Severity filter enables pipeline stages to control validation strictness.
"""

from typing import Dict, List
from code_standards_scanner import Violation


class SeverityFilter:
    """
    Filters violations by severity level.

    WHY: Different stages need different strictness (critical for review, info for analysis).
    PATTERNS: Filter pattern, Dispatch table (severity levels).
    """

    # Dispatch table for severity levels
    SEVERITY_LEVELS = {
        'info': 1,
        'warning': 2,
        'critical': 3
    }

    def filter_by_severity(
        self,
        violations_by_type: Dict[str, List[Violation]],
        severity_threshold: str
    ) -> Dict[str, List[Violation]]:
        """
        Filter violations to only those meeting severity threshold.

        WHY: Allows stages to control validation strictness.

        Args:
            violations_by_type: Violations grouped by type
            severity_threshold: Minimum severity ("info", "warning", "critical")

        Returns:
            Filtered violations dict

        Example:
            >>> filter = SeverityFilter()
            >>> filtered = filter.filter_by_severity(violations, "critical")
            # Only critical violations remain
        """
        # Guard clause - normalize invalid thresholds
        if severity_threshold not in self.SEVERITY_LEVELS:
            severity_threshold = "warning"

        threshold_level = self.SEVERITY_LEVELS[severity_threshold]

        # Filter using comprehension
        filtered = {}
        for v_type, violations in violations_by_type.items():
            filtered_list = [
                v for v in violations
                if self.SEVERITY_LEVELS[v.severity] >= threshold_level
            ]

            # Only include types with violations
            if filtered_list:
                filtered[v_type] = filtered_list

        return filtered
