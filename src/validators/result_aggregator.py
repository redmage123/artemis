#!/usr/bin/env python3
"""
WHY: Aggregate and analyze validation results for reporting.

RESPONSIBILITY: Provide analysis and reporting capabilities for validation
history, including pass rates, trends, and stage-specific statistics.

PATTERNS:
- Aggregator pattern for collecting and summarizing results
- Guard clauses for safe data access
- Single Responsibility - focused on result analysis
"""

from typing import List, Dict, Optional, Tuple
from .models import (
    StageValidationResult,
    ValidationStage,
    ValidationSummary
)


class ResultAggregator:
    """
    WHY: Aggregate validation results for analysis and reporting.

    RESPONSIBILITY: Analyze validation history, calculate statistics,
    and provide insights into validation performance.

    Usage:
        aggregator = ResultAggregator()
        aggregator.add_result(result)
        summary = aggregator.get_summary()
        pass_rate = summary.pass_rate
    """

    def __init__(self):
        """Initialize result aggregator."""
        self.results: List[StageValidationResult] = []

    def add_result(self, result: StageValidationResult) -> None:
        """
        WHY: Add a validation result to the aggregator.

        Args:
            result: Validation result to add
        """
        self.results.append(result)

    def add_results(self, results: List[StageValidationResult]) -> None:
        """
        WHY: Add multiple validation results at once.

        Args:
            results: List of validation results
        """
        self.results.extend(results)

    def get_summary(self) -> ValidationSummary:
        """
        WHY: Get comprehensive summary of validation results.

        Returns:
            ValidationSummary with statistics and history
        """
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed

        by_stage = self._calculate_stage_statistics()

        pass_rate = passed / total if total > 0 else 0.0

        return ValidationSummary(
            total_validations=total,
            passed=passed,
            failed=failed,
            pass_rate=pass_rate,
            by_stage=by_stage,
            history=self.results.copy()
        )

    def _calculate_stage_statistics(self) -> Dict[str, Dict[str, int]]:
        """
        WHY: Calculate statistics broken down by stage.

        Returns:
            Dictionary mapping stage names to their statistics
        """
        by_stage: Dict[str, Dict[str, int]] = {}

        for result in self.results:
            stage_name = result.stage.value

            # Initialize stage stats if needed
            if stage_name not in by_stage:
                by_stage[stage_name] = {'passed': 0, 'failed': 0}

            # Update counts
            if result.passed:
                by_stage[stage_name]['passed'] += 1
            else:
                by_stage[stage_name]['failed'] += 1

        return by_stage

    def get_stage_results(self, stage: ValidationStage) -> List[StageValidationResult]:
        """
        WHY: Get all results for a specific stage.

        Args:
            stage: Validation stage to filter by

        Returns:
            List of results for that stage
        """
        return [r for r in self.results if r.stage == stage]

    def get_failed_results(self) -> List[StageValidationResult]:
        """
        WHY: Get all failed validation results.

        Returns:
            List of failed results
        """
        return [r for r in self.results if not r.passed]

    def get_passed_results(self) -> List[StageValidationResult]:
        """
        WHY: Get all passed validation results.

        Returns:
            List of passed results
        """
        return [r for r in self.results if r.passed]

    def get_critical_failures(self) -> List[StageValidationResult]:
        """
        WHY: Get results with critical severity failures.

        Returns:
            List of critical failure results
        """
        return [r for r in self.results if r.has_critical_failures()]

    def get_pass_rate(self) -> float:
        """
        WHY: Calculate overall pass rate.

        Returns:
            Pass rate as float (0.0 to 1.0)
        """
        # Guard: No results
        if not self.results:
            return 0.0

        passed = sum(1 for r in self.results if r.passed)
        return passed / len(self.results)

    def get_stage_pass_rate(self, stage: ValidationStage) -> float:
        """
        WHY: Calculate pass rate for specific stage.

        Args:
            stage: Validation stage

        Returns:
            Pass rate for stage as float (0.0 to 1.0)
        """
        stage_results = self.get_stage_results(stage)

        # Guard: No results for stage
        if not stage_results:
            return 0.0

        passed = sum(1 for r in stage_results if r.passed)
        return passed / len(stage_results)

    def get_most_common_failures(self, top_n: int = 5) -> List[Tuple[str, int]]:
        """
        WHY: Identify most common validation failures.

        Args:
            top_n: Number of top failures to return

        Returns:
            List of (check_name, count) tuples
        """
        failure_counts: Dict[str, int] = {}

        for result in self.results:
            # Guard: Result passed
            if result.passed:
                continue

            # Count failed checks
            for check_name in result.get_failed_checks():
                failure_counts[check_name] = failure_counts.get(check_name, 0) + 1

        # Sort by count descending
        sorted_failures = sorted(
            failure_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return sorted_failures[:top_n]

    def get_validation_trend(self, window_size: int = 10) -> List[float]:
        """
        WHY: Calculate validation success rate over time.

        Args:
            window_size: Size of rolling window

        Returns:
            List of pass rates for each window
        """
        # Guard: Not enough results
        if len(self.results) < window_size:
            return [self.get_pass_rate()]

        trends = []

        for i in range(len(self.results) - window_size + 1):
            window = self.results[i:i + window_size]
            passed = sum(1 for r in window if r.passed)
            rate = passed / window_size
            trends.append(rate)

        return trends

    def clear(self) -> None:
        """
        WHY: Clear all stored results.

        Useful for starting fresh analysis.
        """
        self.results = []

    def get_result_count(self) -> int:
        """
        WHY: Get total number of results stored.

        Returns:
            Count of results
        """
        return len(self.results)

    def has_results(self) -> bool:
        """
        WHY: Check if aggregator has any results.

        Returns:
            True if results exist
        """
        return len(self.results) > 0

    def get_feedback_summary(self, max_items: int = 10) -> List[str]:
        """
        WHY: Get aggregated feedback from all failed validations.

        Args:
            max_items: Maximum number of feedback items to return

        Returns:
            List of unique feedback messages
        """
        feedback_set = set()

        for result in self.get_failed_results():
            feedback_set.update(result.feedback)

        # Convert to sorted list
        feedback_list = sorted(feedback_set)

        return feedback_list[:max_items]

    def get_stage_statistics(self) -> Dict[str, Dict[str, any]]:
        """
        WHY: Get detailed statistics for each validation stage.

        Returns:
            Dictionary with stage-level metrics
        """
        statistics = {}

        for stage in ValidationStage:
            stage_results = self.get_stage_results(stage)

            # Guard: No results for stage
            if not stage_results:
                continue

            passed = sum(1 for r in stage_results if r.passed)
            failed = len(stage_results) - passed
            pass_rate = passed / len(stage_results) if stage_results else 0.0

            statistics[stage.value] = {
                'total': len(stage_results),
                'passed': passed,
                'failed': failed,
                'pass_rate': pass_rate,
                'critical_failures': sum(1 for r in stage_results if r.has_critical_failures())
            }

        return statistics


class ValidationMetrics:
    """
    WHY: Calculate advanced metrics from validation results.

    RESPONSIBILITY: Provide statistical analysis and quality metrics
    for validation performance.
    """

    @staticmethod
    def calculate_quality_score(summary: ValidationSummary) -> float:
        """
        WHY: Calculate overall quality score (0-100).

        Args:
            summary: ValidationSummary to analyze

        Returns:
            Quality score from 0.0 to 100.0
        """
        # Guard: No validations
        if summary.total_validations == 0:
            return 0.0

        # Base score from pass rate (70% weight)
        base_score = summary.pass_rate * 70

        # Bonus for no critical failures (30% weight)
        critical_failures = sum(
            1 for r in summary.history if r.has_critical_failures()
        )
        critical_penalty = min(critical_failures * 5, 30)
        critical_score = 30 - critical_penalty

        return base_score + critical_score

    @staticmethod
    def get_reliability_rating(pass_rate: float) -> str:
        """
        WHY: Convert pass rate to human-readable reliability rating.

        Args:
            pass_rate: Pass rate from 0.0 to 1.0

        Returns:
            Rating string
        """
        # Guard clauses for rating tiers
        if pass_rate >= 0.95:
            return "Excellent"

        if pass_rate >= 0.85:
            return "Good"

        if pass_rate >= 0.70:
            return "Fair"

        if pass_rate >= 0.50:
            return "Poor"

        return "Critical"

    @staticmethod
    def calculate_improvement_needed(summary: ValidationSummary) -> List[str]:
        """
        WHY: Identify areas needing improvement based on validation history.

        Args:
            summary: ValidationSummary to analyze

        Returns:
            List of improvement recommendations
        """
        recommendations = []

        # Check overall pass rate
        if summary.pass_rate < 0.80:
            recommendations.append(
                f"Overall pass rate is low ({summary.pass_rate:.1%}). "
                "Review validation failures and improve code quality."
            )

        # Check individual stages
        for stage_name, stats in summary.by_stage.items():
            total = stats['passed'] + stats['failed']
            stage_rate = stats['passed'] / total if total > 0 else 0.0

            if stage_rate < 0.70:
                recommendations.append(
                    f"Stage '{stage_name}' has low pass rate ({stage_rate:.1%}). "
                    "Focus on improving this stage."
                )

        # Guard: No recommendations needed
        if not recommendations:
            recommendations.append("Validation quality is good. Keep up the good work!")

        return recommendations
