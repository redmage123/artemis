#!/usr/bin/env python3
"""
Planning Poker Estimator

WHY: Calculates story point estimates, confidence levels, and risk assessments
for features based on Planning Poker voting rounds.

RESPONSIBILITY:
- Calculate overall confidence from voting rounds
- Assess risk level based on story points and confidence
- Convert story points to estimated hours
- Apply penalties for forced consensus and multiple rounds

PATTERNS:
- Strategy Pattern: Risk assessment rules as predicates
- Functional Programming: Rule-based evaluation
- Guard Clauses: Early returns for edge cases
- Dispatch Tables: Risk rules as condition/result pairs
"""

from typing import List, Tuple, Callable
from statistics import mean

from .models import EstimationRound, EstimationConfig


class Estimator:
    """
    Calculates estimates and risk from voting rounds

    WHY: Centralizes estimation calculations and risk assessment
    """

    def __init__(self, team_velocity: float = 20.0):
        """
        Initialize estimator

        Args:
            team_velocity: Team's average story points per sprint
        """
        self.team_velocity = team_velocity

        # Risk assessment rules as (condition, risk_level) pairs
        # Evaluated in order, first match wins
        self.risk_rules: List[Tuple[Callable[[int, float], bool], str]] = [
            (
                lambda sp, conf: (
                    sp >= EstimationConfig.HIGH_RISK_POINTS_THRESHOLD and
                    conf < EstimationConfig.HIGH_RISK_CONFIDENCE_THRESHOLD
                ),
                "high"
            ),
            (
                lambda sp, conf: (
                    sp >= EstimationConfig.MEDIUM_RISK_POINTS_THRESHOLD and
                    conf < EstimationConfig.MEDIUM_RISK_CONFIDENCE_THRESHOLD
                ),
                "medium"
            ),
            (
                lambda sp, conf: sp >= EstimationConfig.HIGH_RISK_POINTS_THRESHOLD,
                "medium"
            ),
            (lambda sp, conf: True, "low")  # Default case
        ]

    def calculate_confidence(self, rounds: List[EstimationRound]) -> float:
        """
        Calculate overall confidence in estimate

        WHY: Quantifies estimation quality considering consensus difficulty

        Confidence factors:
        - Base: Average agent confidence from last round
        - Penalty: Multiple rounds indicate disagreement
        - Penalty: Forced consensus indicates unresolved concerns

        Args:
            rounds: List of estimation rounds

        Returns:
            Confidence value (0.0 to 1.0)
        """
        # Guard clause: no rounds
        if not rounds:
            return 0.0

        last_round = rounds[-1]

        # Guard clause: no votes in last round
        if not last_round.votes:
            return 0.0

        # Start with average agent confidence
        avg_confidence = mean(v.confidence for v in last_round.votes)

        # Penalize if many rounds needed
        round_penalty = EstimationConfig.ROUND_PENALTY_FACTOR * (len(rounds) - 1)

        # Penalize if forced consensus
        forced_penalty = (
            EstimationConfig.FORCED_CONSENSUS_PENALTY
            if not last_round.consensus_reached
            else 0.0
        )

        final_confidence = max(0.0, avg_confidence - round_penalty - forced_penalty)

        return final_confidence

    def assess_risk(self, story_points: int, confidence: float) -> str:
        """
        Assess risk level based on estimate and confidence

        WHY: Identifies high-risk features requiring additional planning

        Risk factors:
        - High story points = complex feature
        - Low confidence = unclear requirements
        - Both = very high risk

        Args:
            story_points: Estimated story points
            confidence: Confidence in estimate (0.0 to 1.0)

        Returns:
            Risk level: "low", "medium", or "high"
        """
        # Find first matching risk rule
        return next(
            risk_level
            for condition, risk_level in self.risk_rules
            if condition(story_points, confidence)
        )

    def calculate_estimated_hours(self, story_points: int) -> float:
        """
        Convert story points to estimated hours

        WHY: Provides concrete time estimate for project planning

        Uses team velocity to convert story points to hours:
        hours = (story_points / team_velocity) * hours_per_sprint

        Args:
            story_points: Estimated story points

        Returns:
            Estimated hours
        """
        # Guard clause: zero or negative story points
        if story_points <= 0:
            return 0.0

        # Guard clause: zero team velocity (avoid division by zero)
        if self.team_velocity <= 0:
            return float(story_points)  # Fallback: 1 hour per point

        estimated_hours = (
            (story_points / self.team_velocity) *
            EstimationConfig.HOURS_PER_SPRINT
        )

        return estimated_hours

    def calculate_sprint_capacity(
        self,
        estimates: List[int]
    ) -> Tuple[float, float]:
        """
        Calculate total story points and sprint capacity usage

        WHY: Helps determine if estimates fit within sprint capacity

        Args:
            estimates: List of story point estimates

        Returns:
            Tuple of (total_points, capacity_percentage)
        """
        # Guard clause: no estimates
        if not estimates:
            return 0.0, 0.0

        total_points = sum(estimates)
        capacity_percentage = (total_points / self.team_velocity) * 100

        return float(total_points), capacity_percentage

    def should_split_story(
        self,
        story_points: int,
        confidence: float
    ) -> bool:
        """
        Determine if story should be split into smaller stories

        WHY: Large or uncertain stories should be decomposed

        Args:
            story_points: Estimated story points
            confidence: Confidence in estimate

        Returns:
            True if story should be split
        """
        # Story is too large
        if story_points >= EstimationConfig.HIGH_RISK_POINTS_THRESHOLD:
            return True

        # Story is uncertain and medium-large
        if (
            story_points >= EstimationConfig.MEDIUM_RISK_POINTS_THRESHOLD and
            confidence < EstimationConfig.HIGH_RISK_CONFIDENCE_THRESHOLD
        ):
            return True

        return False

    def get_complexity_description(self, story_points: int) -> str:
        """
        Get human-readable complexity description

        WHY: Provides intuitive understanding of story size

        Args:
            story_points: Estimated story points

        Returns:
            Complexity description string
        """
        # Dispatch table for complexity descriptions
        complexity_map = {
            1: "Trivial - Quick fix or minor change",
            2: "Small - Single component change",
            3: "Medium - Standard feature work",
            5: "Large - Significant feature",
            8: "Huge - Major feature requiring multiple components",
            13: "Enormous - Epic-level work, consider splitting",
            21: "Epic - Must be split into smaller stories",
            100: "Unknown - Too complex to estimate, needs research"
        }

        # Find closest Fibonacci value
        fibonacci_values = [1, 2, 3, 5, 8, 13, 21, 100]
        closest = min(fibonacci_values, key=lambda x: abs(x - story_points))

        return complexity_map.get(closest, "Unknown complexity")
