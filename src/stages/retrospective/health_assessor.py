#!/usr/bin/env python3
"""
Sprint Health Assessor

WHY: Assess overall sprint health based on multiple factors
RESPONSIBILITY: Calculate health score and determine sprint status
PATTERNS: Single Responsibility, Guard Clauses, Dispatch Tables
"""

from typing import Dict, List, Any, Callable

from .retrospective_models import SprintMetrics


class HealthAssessor:
    """
    Assess overall sprint health

    WHY: Provide unified health assessment
    RESPONSIBILITY: Calculate weighted health score from metrics
    PATTERNS: Single Responsibility, Dispatch tables
    """

    # Dispatch table for health status determination
    HEALTH_STATUS_THRESHOLDS: Dict[str, int] = {
        'healthy': 80,
        'needs_attention': 50,
        'critical': 0
    }

    def assess_sprint_health(self, metrics: SprintMetrics) -> str:
        """
        Assess overall sprint health

        Args:
            metrics: Sprint metrics

        Returns:
            Health status: "healthy", "needs_attention", or "critical"

        WHY: Provide single health indicator
        RESPONSIBILITY: Calculate weighted health score
        PATTERNS: Guard clauses, Dispatch table
        """
        health_score = self._calculate_health_score(metrics)
        return self._determine_health_status(health_score)

    def analyze_velocity_trend(
        self,
        current_metrics: SprintMetrics,
        historical_data: List[Dict[str, Any]]
    ) -> str:
        """
        Analyze velocity trend across sprints

        Args:
            current_metrics: Current sprint metrics
            historical_data: Historical sprint data

        Returns:
            Trend: "improving", "declining", or "stable"

        WHY: Track velocity changes over time
        RESPONSIBILITY: Determine velocity direction
        PATTERNS: Guard clause, Dispatch table
        """
        # Guard: No historical data means stable
        if not historical_data:
            return "stable"

        current_velocity = current_metrics.velocity

        # Dispatch table for trend determination
        if current_velocity >= 90:
            return "improving"

        if current_velocity < 70:
            return "declining"

        return "stable"

    def _calculate_health_score(self, metrics: SprintMetrics) -> int:
        """
        Calculate weighted health score

        WHY: Combine multiple metrics into single score
        RESPONSIBILITY: Apply weighted scoring algorithm
        PATTERNS: Guard clauses for each metric
        """
        health_score = 0

        # Velocity (40% weight)
        health_score += self._score_velocity(metrics.velocity)

        # Test quality (30% weight)
        health_score += self._score_test_quality(metrics.tests_passing)

        # Blockers (20% weight)
        health_score += self._score_blockers(metrics.blockers_encountered)

        # Bug management (10% weight)
        health_score += self._score_bug_management(metrics.bugs_found, metrics.bugs_fixed)

        return health_score

    def _score_velocity(self, velocity: float) -> int:
        """
        Score velocity component (40% weight)

        WHY: Velocity is primary health indicator
        RESPONSIBILITY: Calculate velocity score
        PATTERNS: Guard clauses instead of nested ifs
        """
        if velocity >= 90:
            return 40

        if velocity >= 70:
            return 25

        return 10

    def _score_test_quality(self, tests_passing: float) -> int:
        """
        Score test quality component (30% weight)

        WHY: Test quality indicates code health
        RESPONSIBILITY: Calculate test quality score
        PATTERNS: Guard clauses
        """
        if tests_passing >= 95:
            return 30

        if tests_passing >= 80:
            return 20

        return 5

    def _score_blockers(self, blockers_encountered: int) -> int:
        """
        Score blockers component (20% weight)

        WHY: Blockers impact sprint flow
        RESPONSIBILITY: Calculate blocker score
        PATTERNS: Guard clauses
        """
        if blockers_encountered == 0:
            return 20

        if blockers_encountered <= 2:
            return 10

        return 0

    def _score_bug_management(self, bugs_found: int, bugs_fixed: int) -> int:
        """
        Score bug management component (10% weight)

        WHY: Bug management indicates quality control
        RESPONSIBILITY: Calculate bug management score
        PATTERNS: Guard clauses
        """
        if bugs_fixed >= bugs_found:
            return 10

        if bugs_fixed >= bugs_found * 0.75:
            return 5

        return 0

    def _determine_health_status(self, health_score: int) -> str:
        """
        Determine health status from score

        Args:
            health_score: Calculated health score (0-100)

        Returns:
            Health status string

        WHY: Convert numeric score to status
        RESPONSIBILITY: Apply threshold dispatch
        PATTERNS: Guard clauses instead of if-elif chain
        """
        if health_score >= self.HEALTH_STATUS_THRESHOLDS['healthy']:
            return "healthy"

        if health_score >= self.HEALTH_STATUS_THRESHOLDS['needs_attention']:
            return "needs_attention"

        return "critical"
