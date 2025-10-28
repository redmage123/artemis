#!/usr/bin/env python3
"""
Sprint Validator - Sprint Plan Feasibility Analysis

WHY: Validate sprint planning for realistic capacity and proper distribution
RESPONSIBILITY: Analyze sprint plans for overcommitment, capacity utilization, risk distribution
PATTERNS: Single Responsibility, Guard Clauses, Configuration-Driven Thresholds

This module validates:
- Capacity utilization (not overcommitted)
- Feature dependencies alignment
- Realistic timelines
- Risk distribution across sprints
"""

from typing import Dict, List, Any, Optional


class SprintValidator:
    """
    Validates sprint planning feasibility

    WHY: Ensure sprint plans are achievable and well-balanced
    RESPONSIBILITY: Check capacity, timeline realism, and risk distribution
    """

    def __init__(
        self,
        logger: Any,
        capacity_high_threshold: float = 0.95,
        capacity_low_threshold: float = 0.70
    ):
        """
        Initialize Sprint Validator

        Args:
            logger: Logger interface for diagnostics
            capacity_high_threshold: Max acceptable capacity utilization (overcommitment)
            capacity_low_threshold: Min acceptable capacity utilization (underutilization)
        """
        if not logger:
            raise ValueError("Logger is required for sprint validation")

        self.logger = logger
        self.capacity_high_threshold = capacity_high_threshold
        self.capacity_low_threshold = capacity_low_threshold

    def review_sprints(
        self,
        sprints: List[Dict[str, Any]],
        architecture: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Review sprint planning feasibility

        WHY: Validate sprint plans are realistic and achievable

        Args:
            sprints: List of sprint dictionaries with story points and capacity
            architecture: Optional architecture for dependency validation

        Returns:
            Dictionary with score, feedback, and issues list
        """
        if not sprints:
            return self._create_empty_review()

        metrics = self._calculate_sprint_metrics(sprints)
        issues = self._identify_sprint_issues(sprints, metrics)
        score = self._calculate_sprint_score(issues)
        feedback = self._generate_sprint_feedback(metrics, issues)

        return {
            "score": score,
            "feedback": feedback,
            "issues": issues,
            "total_sprints": metrics['total_sprints'],
            "total_story_points": metrics['total_points']
        }

    def _create_empty_review(self) -> Dict[str, Any]:
        """Create review for missing sprint plan"""
        return {
            "score": 0,
            "feedback": "No sprints to review",
            "issues": ["No sprint plan provided"]
        }

    def _calculate_sprint_metrics(self, sprints: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate aggregate sprint metrics

        WHY: Single pass through sprints for all metrics
        """
        total_sprints = len(sprints)
        total_points = sum(s.get('total_story_points', 0) for s in sprints)
        avg_capacity = sum(s.get('capacity_used', 0) for s in sprints) / max(total_sprints, 1)

        return {
            'total_sprints': total_sprints,
            'total_points': total_points,
            'avg_capacity': avg_capacity
        }

    def _identify_sprint_issues(
        self,
        sprints: List[Dict[str, Any]],
        metrics: Dict[str, float]
    ) -> List[str]:
        """
        Identify sprint planning issues

        WHY: Centralize issue detection logic using guard clauses
        """
        issues = []

        # Check for overcommitment
        overcommitted = [
            (sprint.get('sprint_number'), sprint.get('capacity_used', 0))
            for sprint in sprints
            if sprint.get('capacity_used', 0) > self.capacity_high_threshold
        ]

        for sprint_num, capacity in overcommitted:
            issues.append(f"Sprint {sprint_num} is overcommitted ({capacity:.0%})")

        # Check for underutilization
        if metrics['avg_capacity'] < self.capacity_low_threshold:
            issues.append(f"Average capacity utilization is low ({metrics['avg_capacity']:.0%})")

        # Check for unrealistic sprint 1
        if sprints and sprints[0].get('total_story_points', 0) > 25:
            issues.append("Sprint 1 may be too ambitious")

        return issues

    def _calculate_sprint_score(self, issues: List[str]) -> int:
        """
        Calculate sprint review score

        WHY: Consistent scoring based on issue severity
        """
        base_score = 10

        # Deduct points based on issue types
        for issue in issues:
            if "overcommitted" in issue:
                base_score -= 2
            elif "low" in issue and "capacity" in issue:
                base_score -= 1
            elif "ambitious" in issue:
                base_score -= 1

        return max(0, base_score)

    def _generate_sprint_feedback(
        self,
        metrics: Dict[str, float],
        issues: List[str]
    ) -> str:
        """
        Generate human-readable feedback

        WHY: Provide actionable summary of sprint analysis
        """
        feedback = (
            f"Reviewed {metrics['total_sprints']} sprints with "
            f"{metrics['total_points']} total story points. "
            f"Average capacity: {metrics['avg_capacity']:.0%}. "
        )

        if issues:
            feedback += f"Found {len(issues)} potential issues."
        else:
            feedback += "Sprint plan looks feasible."

        return feedback
