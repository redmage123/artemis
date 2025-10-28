#!/usr/bin/env python3
"""
Review Result Aggregator

WHY: Aggregate and analyze results from multiple code reviews
RESPONSIBILITY: Calculate metrics and determine passing scores
PATTERNS: Aggregator Pattern, Single Responsibility, Guard Clauses
"""

from typing import Dict, List

from artemis_stage_interface import LoggerInterface


class ReviewResultAggregator:
    """
    Aggregate results from multiple code reviews.

    WHY: Separate aggregation logic from review execution
    RESPONSIBILITY: Calculate totals, averages, and determine pass/fail
    PATTERNS: Aggregator Pattern, Reduce Pattern
    """

    def __init__(self, logger: LoggerInterface):
        """
        Initialize review aggregator.

        Args:
            logger: Logger interface
        """
        self.logger = logger

    def aggregate_reviews(self, review_results: List[Dict]) -> Dict:
        """
        Aggregate multiple review results into summary statistics.

        WHY: Provide single source of truth for aggregated metrics
        RESPONSIBILITY: Calculate totals and determine overall pass/fail
        PATTERN: Aggregator Pattern, Guard Clauses

        Args:
            review_results: List of individual review results

        Returns:
            Dict with aggregated metrics:
                - review_count: Number of reviews
                - total_critical_issues: Sum of critical issues
                - total_high_issues: Sum of high issues
                - all_reviews_pass: True if all reviews passed
                - average_score: Average review score
                - failed_reviews: List of failed review names
        """
        if not review_results:
            return self._empty_aggregation()

        total_critical_issues = 0
        total_high_issues = 0
        all_reviews_pass = True
        total_score = 0
        failed_reviews = []

        for result in review_results:
            # Extract metrics
            review_status = result.get('review_status', 'FAIL')
            critical_issues = result.get('critical_issues', 0)
            high_issues = result.get('high_issues', 0)
            overall_score = result.get('overall_score', 0)
            developer_name = result.get('developer_name', 'unknown')

            # Accumulate totals
            total_critical_issues += critical_issues
            total_high_issues += high_issues
            total_score += overall_score

            # Track failures
            if review_status == "FAIL":
                all_reviews_pass = False
                failed_reviews.append(developer_name)

        # Calculate average score
        average_score = total_score / len(review_results) if review_results else 0

        return {
            'review_count': len(review_results),
            'total_critical_issues': total_critical_issues,
            'total_high_issues': total_high_issues,
            'all_reviews_pass': all_reviews_pass,
            'average_score': average_score,
            'failed_reviews': failed_reviews
        }

    def _empty_aggregation(self) -> Dict:
        """
        Return empty aggregation result.

        WHY: Provide consistent return structure for empty input
        PATTERN: Null Object Pattern
        """
        return {
            'review_count': 0,
            'total_critical_issues': 0,
            'total_high_issues': 0,
            'all_reviews_pass': True,
            'average_score': 0,
            'failed_reviews': []
        }

    def determine_passing_score(self, aggregated: Dict, threshold: int = 70) -> bool:
        """
        Determine if aggregated results meet passing criteria.

        WHY: Centralized pass/fail logic with configurable threshold
        RESPONSIBILITY: Apply business rules for passing reviews
        PATTERN: Strategy Pattern

        Args:
            aggregated: Aggregated review results
            threshold: Minimum average score required (default: 70)

        Returns:
            True if reviews pass, False otherwise
        """
        # Must have no critical issues
        if aggregated['total_critical_issues'] > 0:
            return False

        # All reviews must pass
        if not aggregated['all_reviews_pass']:
            return False

        # Average score must meet threshold
        if aggregated['average_score'] < threshold:
            return False

        return True

    def get_summary_report(self, aggregated: Dict) -> str:
        """
        Generate human-readable summary report.

        WHY: Provide formatted output for logging/display
        RESPONSIBILITY: Format aggregated data for human consumption
        PATTERN: Formatter Pattern

        Args:
            aggregated: Aggregated review results

        Returns:
            Formatted summary string
        """
        lines = [
            "=" * 60,
            "CODE REVIEW SUMMARY",
            "=" * 60,
            f"Total Reviews: {aggregated['review_count']}",
            f"Average Score: {aggregated['average_score']:.1f}/100",
            f"Critical Issues: {aggregated['total_critical_issues']}",
            f"High Issues: {aggregated['total_high_issues']}",
            f"All Passed: {'Yes' if aggregated['all_reviews_pass'] else 'No'}",
        ]

        if aggregated['failed_reviews']:
            lines.append(f"\nFailed Reviews: {', '.join(aggregated['failed_reviews'])}")

        lines.append("=" * 60)

        return "\n".join(lines)
