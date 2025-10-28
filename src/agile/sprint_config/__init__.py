#!/usr/bin/env python3
"""
Sprint Configuration Package - Modular Sprint Workflow Configuration

WHY: Provides type-safe, validated access to sprint workflow configuration
     with support for multiple sources (Hydra, dict) and easy testing.
RESPONSIBILITY: Export public API for sprint configuration access.
PATTERNS: Facade pattern, factory methods, immutable value objects

This package consolidates sprint configuration management into focused,
testable modules following SOLID principles and functional programming patterns.

Package Structure:
    - models.py: Immutable configuration dataclasses
    - validators.py: Pure validation functions
    - hydra_loader.py: Hydra/OmegaConf integration
    - dict_loader.py: Plain dictionary support for testing
    - accessor.py: Main facade for unified access

Usage:
    from agile.sprint_config import SprintConfigAccessor

    # From Hydra
    config = SprintConfigAccessor.from_hydra(cfg)
    velocity = config.sprint_planning.team_velocity

    # From dict (testing)
    config = SprintConfigAccessor.from_dict(config_dict)
    risk_score = config.get_risk_score('high')
"""

# Export main public API
from agile.sprint_config.accessor import SprintConfigAccessor

# Export models for type hints and direct instantiation
from agile.sprint_config.models import (
    SprintPlanningConfig,
    ProjectReviewConfig,
    UIUXEvaluationConfig,
    RetrospectiveConfig
)

# Export validators for custom validation scenarios
from agile.sprint_config.validators import (
    validate_config,
    validate_planning_config,
    validate_review_config,
    validate_retrospective_config,
    validate_weights_sum_to_one,
    validate_weights_sum_to_hundred
)

__all__ = [
    # Main accessor (primary interface)
    'SprintConfigAccessor',

    # Models
    'SprintPlanningConfig',
    'ProjectReviewConfig',
    'UIUXEvaluationConfig',
    'RetrospectiveConfig',

    # Validators
    'validate_config',
    'validate_planning_config',
    'validate_review_config',
    'validate_retrospective_config',
    'validate_weights_sum_to_one',
    'validate_weights_sum_to_hundred',
]
