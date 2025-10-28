#!/usr/bin/env python3
"""
Sprint Configuration Models - Type-Safe Dataclasses

WHY: Provides immutable, type-safe configuration models for sprint workflows.
RESPONSIBILITY: Define dataclass models for sprint planning, project review,
                UI/UX evaluation, and retrospective configurations.
PATTERNS: Immutable dataclasses (frozen=True), value objects

This module contains the core domain models representing different aspects
of sprint configuration. All models are immutable to prevent accidental
modifications and ensure thread safety.
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class SprintPlanningConfig:
    """
    Type-safe sprint planning configuration model.

    WHY: Encapsulates all sprint planning parameters in an immutable structure.
    RESPONSIBILITY: Store and provide access to sprint planning settings.

    Attributes:
        team_velocity: Expected story points per sprint
        sprint_duration_days: Length of sprint in days
        risk_scores: Mapping of risk levels (low/medium/high) to numeric scores
        priority_weights: Weights for different priority factors (must sum to 1.0)
        planning_poker_agents: List of agent names participating in estimation
        fibonacci_scale: Valid story point values for estimation
    """

    team_velocity: float
    sprint_duration_days: int
    risk_scores: Dict[str, int]
    priority_weights: Dict[str, float]
    planning_poker_agents: List[str]
    fibonacci_scale: List[int]

    def get_risk_score(self, risk_level: str) -> int:
        """
        Get risk score for a given risk level.

        WHY: Provides safe access with fallback to medium risk level.
        PERFORMANCE: O(1) dictionary lookup.

        Args:
            risk_level: Risk level identifier (low/medium/high)

        Returns:
            Numeric risk score, defaults to medium if level not found
        """
        return self.risk_scores.get(risk_level, self.risk_scores.get('medium', 0))


@dataclass(frozen=True)
class ProjectReviewConfig:
    """
    Type-safe project review configuration model.

    WHY: Encapsulates project review thresholds and capacity settings.
    RESPONSIBILITY: Store review weights, thresholds, and capacity constraints.

    Attributes:
        review_weights: Weights for different review aspects (must sum to 1.0)
        approval_threshold: Minimum score for automatic approval
        conditional_approval_threshold: Minimum score for conditional approval
        rejection_threshold: Maximum score before rejection
        max_iterations: Maximum number of review iterations allowed
        overcommitted_threshold: Percentage threshold for overcommitment detection
        underutilized_threshold: Percentage threshold for underutilization detection
        max_sprint1_points: Maximum story points allowed in first sprint
    """

    review_weights: Dict[str, float]
    approval_threshold: float
    conditional_approval_threshold: float
    rejection_threshold: float
    max_iterations: int
    overcommitted_threshold: float
    underutilized_threshold: float
    max_sprint1_points: int


@dataclass(frozen=True)
class UIUXEvaluationConfig:
    """
    Type-safe UI/UX evaluation configuration model.

    WHY: Encapsulates UI/UX evaluation criteria and thresholds.
    RESPONSIBILITY: Store score deductions and accessibility issue thresholds.

    Attributes:
        score_deductions: Mapping of issue types to point deductions
        critical_accessibility_issues_threshold: Maximum allowed critical issues
    """

    score_deductions: Dict[str, int]
    critical_accessibility_issues_threshold: int


@dataclass(frozen=True)
class RetrospectiveConfig:
    """
    Type-safe retrospective configuration model.

    WHY: Encapsulates retrospective analysis parameters and thresholds.
    RESPONSIBILITY: Store health weights, quality thresholds, and analysis settings.

    Attributes:
        health_weights: Weights for different health metrics (must sum to 100)
        velocity_thresholds: Thresholds for velocity assessment
        test_quality_thresholds: Thresholds for test quality metrics
        health_score_thresholds: Thresholds for overall health scoring
        historical_sprints_to_analyze: Number of past sprints to include in analysis
    """

    health_weights: Dict[str, int]
    velocity_thresholds: Dict[str, float]
    test_quality_thresholds: Dict[str, float]
    health_score_thresholds: Dict[str, int]
    historical_sprints_to_analyze: int
