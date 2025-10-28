#!/usr/bin/env python3
"""
Hydra Configuration Loader - OmegaConf to Model Conversion

WHY: Separates Hydra/OmegaConf integration from core business logic,
     enabling easier testing and alternative configuration sources.
RESPONSIBILITY: Load sprint configuration from Hydra DictConfig objects.
PATTERNS: Factory pattern for config creation, pure functions for extraction

This module handles the complexity of extracting nested configuration
values from OmegaConf and converting them to immutable domain models.
"""

from typing import Dict, Any
from omegaconf import DictConfig

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


def extract_sprint_planning(cfg: DictConfig) -> SprintPlanningConfig:
    """
    Extract sprint planning configuration from Hydra config.

    WHY: Centralizes extraction logic for sprint planning settings.
    PERFORMANCE: O(n) where n is number of config entries.

    Args:
        cfg: Hydra DictConfig with sprint_planning section

    Returns:
        SprintPlanningConfig with validated settings

    Raises:
        ConfigurationError: If validation fails or required keys missing
    """
    sp_cfg = cfg.sprint_planning

    config = SprintPlanningConfig(
        team_velocity=float(sp_cfg.team_velocity),
        sprint_duration_days=int(sp_cfg.sprint_duration_days),
        risk_scores=dict(sp_cfg.risk_scores),
        priority_weights=dict(sp_cfg.priority_weights),
        planning_poker_agents=list(sp_cfg.planning_poker.agents),
        fibonacci_scale=list(sp_cfg.planning_poker.fibonacci_scale)
    )

    validate_planning_config(config)
    return config


def extract_project_review(cfg: DictConfig) -> ProjectReviewConfig:
    """
    Extract project review configuration from Hydra config.

    WHY: Centralizes extraction logic for project review settings.
    PERFORMANCE: O(n) where n is number of config entries.

    Args:
        cfg: Hydra DictConfig with project_review section

    Returns:
        ProjectReviewConfig with validated settings

    Raises:
        ConfigurationError: If validation fails or required keys missing
    """
    pr_cfg = cfg.project_review

    config = ProjectReviewConfig(
        review_weights=dict(pr_cfg.review_weights),
        approval_threshold=float(pr_cfg.thresholds.approval),
        conditional_approval_threshold=float(pr_cfg.thresholds.conditional_approval),
        rejection_threshold=float(pr_cfg.thresholds.rejection),
        max_iterations=int(pr_cfg.max_iterations),
        overcommitted_threshold=float(pr_cfg.capacity.overcommitted_threshold),
        underutilized_threshold=float(pr_cfg.capacity.underutilized_threshold),
        max_sprint1_points=int(pr_cfg.capacity.max_sprint1_points)
    )

    validate_review_config(config)
    return config


def extract_uiux_evaluation(cfg: DictConfig) -> UIUXEvaluationConfig:
    """
    Extract UI/UX evaluation configuration from Hydra config.

    WHY: Centralizes extraction logic for UI/UX evaluation settings.
    PERFORMANCE: O(n) where n is number of config entries.

    Args:
        cfg: Hydra DictConfig with uiux_evaluation section

    Returns:
        UIUXEvaluationConfig with settings

    Raises:
        KeyError: If required keys missing
    """
    uiux_cfg = cfg.uiux_evaluation

    return UIUXEvaluationConfig(
        score_deductions=dict(uiux_cfg.score_deductions),
        critical_accessibility_issues_threshold=int(
            uiux_cfg.thresholds.critical_accessibility_issues
        )
    )


def extract_retrospective(cfg: DictConfig) -> RetrospectiveConfig:
    """
    Extract retrospective configuration from Hydra config.

    WHY: Centralizes extraction logic for retrospective settings.
    PERFORMANCE: O(n) where n is number of config entries.

    Args:
        cfg: Hydra DictConfig with retrospective section

    Returns:
        RetrospectiveConfig with validated settings

    Raises:
        ConfigurationError: If validation fails or required keys missing
    """
    retro_cfg = cfg.retrospective

    config = RetrospectiveConfig(
        health_weights=dict(retro_cfg.health_weights),
        velocity_thresholds=dict(retro_cfg.thresholds.velocity),
        test_quality_thresholds=dict(retro_cfg.thresholds.test_quality),
        health_score_thresholds=dict(retro_cfg.thresholds.health_score),
        historical_sprints_to_analyze=int(retro_cfg.historical_sprints_to_analyze)
    )

    validate_retrospective_config(config)
    return config


# Strategy pattern: Map config types to their extractors
EXTRACTOR_STRATEGIES = {
    'sprint_planning': extract_sprint_planning,
    'project_review': extract_project_review,
    'uiux_evaluation': extract_uiux_evaluation,
    'retrospective': extract_retrospective
}


def load_config_section(cfg: DictConfig, section: str) -> Any:
    """
    Load a specific configuration section using strategy pattern.

    WHY: Provides unified loading interface with strategy dispatch.
    PATTERNS: Strategy pattern - dispatch to appropriate extractor.
    PERFORMANCE: O(1) dictionary lookup + O(n) extraction.

    Args:
        cfg: Hydra DictConfig object
        section: Section name ('sprint_planning', 'project_review', etc.)

    Returns:
        Appropriate config model instance

    Raises:
        ValueError: If section name is unknown
    """
    extractor = EXTRACTOR_STRATEGIES.get(section)

    if not extractor:
        raise ValueError(
            f"Unknown config section: {section}. "
            f"Supported: {list(EXTRACTOR_STRATEGIES.keys())}"
        )

    return extractor(cfg)
