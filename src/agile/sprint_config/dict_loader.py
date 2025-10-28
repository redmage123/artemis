#!/usr/bin/env python3
"""
Dictionary Configuration Loader - Plain Dict to Model Conversion

WHY: Enables testing and alternative configuration sources without Hydra/OmegaConf.
RESPONSIBILITY: Load sprint configuration from plain Python dictionaries.
PATTERNS: Factory pattern for config creation, pure functions for extraction

This module provides an alternative to Hydra for cases where configuration
comes from JSON, YAML parsing, or programmatic creation in tests.
"""

from typing import Dict, Any

from agile.sprint_config.models import (
    SprintPlanningConfig,
    ProjectReviewConfig,
    UIUXEvaluationConfig,
    RetrospectiveConfig
)
from agile.sprint_config.validators import (
    validate_planning_config,
    validate_review_config,
    validate_retrospective_config
)


def extract_sprint_planning_from_dict(config_dict: Dict[str, Any]) -> SprintPlanningConfig:
    """
    Extract sprint planning configuration from dictionary.

    WHY: Enables testing without Hydra dependency.
    PERFORMANCE: O(n) where n is number of config entries.

    Args:
        config_dict: Dictionary with sprint_planning section

    Returns:
        SprintPlanningConfig with validated settings

    Raises:
        ConfigurationError: If validation fails
        KeyError: If required keys missing
    """
    sp_dict = config_dict['sprint_planning']

    config = SprintPlanningConfig(
        team_velocity=sp_dict['team_velocity'],
        sprint_duration_days=sp_dict['sprint_duration_days'],
        risk_scores=sp_dict['risk_scores'],
        priority_weights=sp_dict['priority_weights'],
        planning_poker_agents=sp_dict['planning_poker']['agents'],
        fibonacci_scale=sp_dict['planning_poker']['fibonacci_scale']
    )

    validate_planning_config(config)
    return config


def extract_project_review_from_dict(config_dict: Dict[str, Any]) -> ProjectReviewConfig:
    """
    Extract project review configuration from dictionary.

    WHY: Enables testing without Hydra dependency.
    PERFORMANCE: O(n) where n is number of config entries.

    Args:
        config_dict: Dictionary with project_review section

    Returns:
        ProjectReviewConfig with validated settings

    Raises:
        ConfigurationError: If validation fails
        KeyError: If required keys missing
    """
    pr_dict = config_dict['project_review']

    config = ProjectReviewConfig(
        review_weights=pr_dict['review_weights'],
        approval_threshold=pr_dict['thresholds']['approval'],
        conditional_approval_threshold=pr_dict['thresholds']['conditional_approval'],
        rejection_threshold=pr_dict['thresholds']['rejection'],
        max_iterations=pr_dict['max_iterations'],
        overcommitted_threshold=pr_dict['capacity']['overcommitted_threshold'],
        underutilized_threshold=pr_dict['capacity']['underutilized_threshold'],
        max_sprint1_points=pr_dict['capacity']['max_sprint1_points']
    )

    validate_review_config(config)
    return config


def extract_uiux_evaluation_from_dict(config_dict: Dict[str, Any]) -> UIUXEvaluationConfig:
    """
    Extract UI/UX evaluation configuration from dictionary.

    WHY: Enables testing without Hydra dependency.
    PERFORMANCE: O(n) where n is number of config entries.

    Args:
        config_dict: Dictionary with uiux_evaluation section

    Returns:
        UIUXEvaluationConfig with settings

    Raises:
        KeyError: If required keys missing
    """
    uiux_dict = config_dict['uiux_evaluation']

    return UIUXEvaluationConfig(
        score_deductions=uiux_dict['score_deductions'],
        critical_accessibility_issues_threshold=uiux_dict['thresholds']['critical_accessibility_issues']
    )


def extract_retrospective_from_dict(config_dict: Dict[str, Any]) -> RetrospectiveConfig:
    """
    Extract retrospective configuration from dictionary.

    WHY: Enables testing without Hydra dependency.
    PERFORMANCE: O(n) where n is number of config entries.

    Args:
        config_dict: Dictionary with retrospective section

    Returns:
        RetrospectiveConfig with validated settings

    Raises:
        ConfigurationError: If validation fails
        KeyError: If required keys missing
    """
    retro_dict = config_dict['retrospective']

    config = RetrospectiveConfig(
        health_weights=retro_dict['health_weights'],
        velocity_thresholds=retro_dict['thresholds']['velocity'],
        test_quality_thresholds=retro_dict['thresholds']['test_quality'],
        health_score_thresholds=retro_dict['thresholds']['health_score'],
        historical_sprints_to_analyze=retro_dict['historical_sprints_to_analyze']
    )

    validate_retrospective_config(config)
    return config


# Strategy pattern: Map config types to their extractors
DICT_EXTRACTOR_STRATEGIES = {
    'sprint_planning': extract_sprint_planning_from_dict,
    'project_review': extract_project_review_from_dict,
    'uiux_evaluation': extract_uiux_evaluation_from_dict,
    'retrospective': extract_retrospective_from_dict
}


def load_config_section_from_dict(config_dict: Dict[str, Any], section: str) -> Any:
    """
    Load a specific configuration section from dictionary using strategy pattern.

    WHY: Provides unified loading interface with strategy dispatch.
    PATTERNS: Strategy pattern - dispatch to appropriate extractor.
    PERFORMANCE: O(1) dictionary lookup + O(n) extraction.

    Args:
        config_dict: Configuration dictionary
        section: Section name ('sprint_planning', 'project_review', etc.)

    Returns:
        Appropriate config model instance

    Raises:
        ValueError: If section name is unknown
    """
    extractor = DICT_EXTRACTOR_STRATEGIES.get(section)

    if not extractor:
        raise ValueError(
            f"Unknown config section: {section}. "
            f"Supported: {list(DICT_EXTRACTOR_STRATEGIES.keys())}"
        )

    return extractor(config_dict)
