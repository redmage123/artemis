#!/usr/bin/env python3
"""
WHY: Parse CTest output for test statistics
RESPONSIBILITY: Extract pass/fail counts from test output
PATTERNS: Parser (regex-based), Pure function

Test stats parser extracts structured data from CTest's text output.
"""

import re
from typing import Dict


class TestStatsParser:
    """
    Parses CTest output for statistics.

    WHY: Convert text output into structured metrics.
    PATTERNS: Parser pattern (regex extraction).
    """

    def extract_test_stats(self, output: str) -> Dict[str, int]:
        """
        Extract test statistics from CTest output.

        WHY: Provides structured test metrics for reporting.

        Args:
            output: CTest output

        Returns:
            Dict with test statistics

        Example:
            >>> parser = TestStatsParser()
            >>> stats = parser.extract_test_stats(
            ...     "100% tests passed, 0 tests failed out of 10"
            ... )
            >>> stats["tests_passed"]
            10
        """
        stats = {
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'tests_skipped': 0
        }

        # CTest summary: "100% tests passed, 0 tests failed out of 10"
        summary_match = re.search(
            r"(\d+)%\s+tests\s+passed,\s+(\d+)\s+tests\s+failed\s+out\s+of\s+(\d+)",
            output
        )

        # Guard clause - return empty stats if no match
        if not summary_match:
            return stats

        failed = int(summary_match.group(2))
        total = int(summary_match.group(3))
        passed = total - failed

        stats['tests_run'] = total
        stats['tests_passed'] = passed
        stats['tests_failed'] = failed

        return stats
