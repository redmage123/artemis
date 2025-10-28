#!/usr/bin/env python3
"""
Sprint Configuration Validators - Weight and Threshold Validation

WHY: Ensures configuration integrity by validating that weights and values
     meet expected constraints before use in sprint workflows.
RESPONSIBILITY: Validate configuration weights, thresholds, and relationships.
PATTERNS: Pure functions, strategy pattern for validation types

All validators are pure functions that return boolean results without side effects.
"""

from typing import Dict, Callable, Any
from artemis_exceptions import ConfigurationError


# Validation tolerance for floating point comparisons
FLOAT_TOLERANCE = 0.001


def validate_weights_sum_to_one(weights: Dict[str, float]) -> bool:
    """
    Validate that weight values sum to 1.0.

    WHY: Priority and review weights represent percentages that must sum to 100%.
    PERFORMANCE: O(n) where n is number of weight entries.

    Args:
        weights: Dictionary of weight names to values

    Returns:
        True if weights sum to 1.0 within tolerance, False otherwise
    """
    total = sum(weights.values())
    return abs(total - 1.0) < FLOAT_TOLERANCE


def validate_weights_sum_to_hundred(weights: Dict[str, int]) -> bool:
    """
    Validate that weight values sum to 100.

    WHY: Health weights represent percentages that must sum to 100.
    PERFORMANCE: O(n) where n is number of weight entries.

    Args:
        weights: Dictionary of weight names to integer values

    Returns:
        True if weights sum to 100, False otherwise
    """
    return sum(weights.values()) == 100


def validate_threshold_ordering(
    low: float,
    medium: float,
    high: float
) -> bool:
    """
    Validate that thresholds are ordered low < medium < high.

    WHY: Threshold values must be properly ordered for range checks to work.
    PERFORMANCE: O(1) - simple comparison.

    Args:
        low: Low threshold value
        medium: Medium threshold value
        high: High threshold value

    Returns:
        True if thresholds are properly ordered, False otherwise
    """
    return low < medium < high


def validate_positive_value(value: float) -> bool:
    """
    Validate that a value is positive.

    WHY: Values like velocity, duration, and points must be positive.
    PERFORMANCE: O(1) - simple comparison.

    Args:
        value: Value to validate

    Returns:
        True if value is greater than zero, False otherwise
    """
    return value > 0


def validate_planning_config(config: Any) -> None:
    """
    Validate SprintPlanningConfig integrity.

    WHY: Catches configuration errors early before they cause runtime failures.
    PERFORMANCE: O(n) where n is number of weights.

    Args:
        config: SprintPlanningConfig instance to validate

    Raises:
        ConfigurationError: If validation fails with detailed context
    """
    if not validate_weights_sum_to_one(config.priority_weights):
        raise ConfigurationError(
            "Sprint planning priority weights must sum to 1.0",
            context={
                'weights': config.priority_weights,
                'actual_sum': sum(config.priority_weights.values())
            }
        )

    if not validate_positive_value(config.team_velocity):
        raise ConfigurationError(
            "Team velocity must be positive",
            context={'team_velocity': config.team_velocity}
        )

    if not validate_positive_value(config.sprint_duration_days):
        raise ConfigurationError(
            "Sprint duration must be positive",
            context={'sprint_duration_days': config.sprint_duration_days}
        )


def validate_review_config(config: Any) -> None:
    """
    Validate ProjectReviewConfig integrity.

    WHY: Ensures review thresholds and weights are properly configured.
    PERFORMANCE: O(n) where n is number of weights.

    Args:
        config: ProjectReviewConfig instance to validate

    Raises:
        ConfigurationError: If validation fails with detailed context
    """
    if not validate_weights_sum_to_one(config.review_weights):
        raise ConfigurationError(
            "Project review weights must sum to 1.0",
            context={
                'weights': config.review_weights,
                'actual_sum': sum(config.review_weights.values())
            }
        )

    if not (config.rejection_threshold <
            config.conditional_approval_threshold <
            config.approval_threshold):
        raise ConfigurationError(
            "Review thresholds must be ordered: rejection < conditional < approval",
            context={
                'rejection': config.rejection_threshold,
                'conditional': config.conditional_approval_threshold,
                'approval': config.approval_threshold
            }
        )


def validate_retrospective_config(config: Any) -> None:
    """
    Validate RetrospectiveConfig integrity.

    WHY: Ensures health weights sum to 100 and historical range is valid.
    PERFORMANCE: O(n) where n is number of weights.

    Args:
        config: RetrospectiveConfig instance to validate

    Raises:
        ConfigurationError: If validation fails with detailed context
    """
    if not validate_weights_sum_to_hundred(config.health_weights):
        raise ConfigurationError(
            "Retrospective health weights must sum to 100",
            context={
                'weights': config.health_weights,
                'actual_sum': sum(config.health_weights.values())
            }
        )

    if not validate_positive_value(config.historical_sprints_to_analyze):
        raise ConfigurationError(
            "Historical sprints to analyze must be positive",
            context={'historical_sprints': config.historical_sprints_to_analyze}
        )


# Strategy pattern: Map config types to their validators
VALIDATOR_STRATEGIES: Dict[str, Callable[[Any], None]] = {
    'SprintPlanningConfig': validate_planning_config,
    'ProjectReviewConfig': validate_review_config,
    'RetrospectiveConfig': validate_retrospective_config,
}


def validate_config(config: Any) -> None:
    """
    Validate configuration using strategy pattern.

    WHY: Provides unified validation interface using strategy pattern.
    PATTERNS: Strategy pattern - dispatch to appropriate validator.
    PERFORMANCE: O(1) dictionary lookup + O(n) validation.

    Args:
        config: Configuration instance to validate

    Raises:
        ConfigurationError: If validation fails or unknown config type
    """
    config_type = config.__class__.__name__
    validator = VALIDATOR_STRATEGIES.get(config_type)

    if not validator:
        raise ConfigurationError(
            f"Unknown configuration type: {config_type}",
            context={'type': config_type, 'supported': list(VALIDATOR_STRATEGIES.keys())}
        )

    validator(config)
