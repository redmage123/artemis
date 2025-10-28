#!/usr/bin/env python3
"""
Module: pipeline_config.py

WHY this module exists:
    Centralized configuration object controlling feature activation, thresholds, and
    behavior parameters. Single source of truth prevents inconsistent settings.

RESPONSIBILITY:
    - Define configuration dataclass for advanced pipeline features
    - Validate configuration values
    - Provide configuration defaults
    - Store feature enable/disable flags and thresholds

PATTERNS:
    - Configuration Object Pattern: Centralized settings management
    - Validation at construction time (fail fast)
"""

from dataclasses import dataclass


@dataclass
class AdvancedPipelineConfig:
    """
    Configuration for advanced pipeline features.

    WHAT: Centralized configuration object controlling feature activation,
    thresholds, and behavior parameters.

    WHY: Single source of truth for configuration prevents inconsistent settings
    across components. Enables configuration persistence, A/B testing, and
    gradual feature rollout.

    Design pattern: Configuration Object

    Responsibilities:
        - Store feature enable/disable flags
        - Define quality/confidence thresholds
        - Configure mode selection behavior
        - Provide validation and defaults
    """
    # Feature enable flags
    enable_dynamic_pipeline: bool = True
    enable_two_pass: bool = False  # More experimental, default off
    enable_thermodynamic: bool = True
    auto_mode_selection: bool = True  # Automatically select mode

    # Quality thresholds
    confidence_threshold: float = 0.7  # Minimum confidence for automated decisions
    quality_improvement_threshold: float = 0.05  # Minimum improvement to keep second pass
    rollback_degradation_threshold: float = -0.1  # Rollback if quality drops 10%+

    # Mode selection thresholds
    simple_task_max_story_points: int = 3  # Tasks <= 3 points use standard mode
    complex_task_min_story_points: int = 8  # Tasks >= 8 points use full mode

    # Dynamic pipeline configuration
    parallel_execution_enabled: bool = False  # Enable parallel stage execution
    max_parallel_workers: int = 4
    stage_result_caching_enabled: bool = True

    # Two-pass configuration
    two_pass_auto_rollback: bool = True  # Rollback if second pass degrades quality
    first_pass_timeout_multiplier: float = 0.3  # First pass gets 30% of stage timeout

    # Thermodynamic configuration
    default_uncertainty_strategy: str = "bayesian"
    enable_temperature_annealing: bool = True
    temperature_schedule: str = "exponential"  # "linear", "exponential", "inverse", "step"
    initial_temperature: float = 1.0
    final_temperature: float = 0.1

    # Performance monitoring
    enable_performance_tracking: bool = True
    performance_metrics_window: int = 10  # Track last N pipeline executions

    def __post_init__(self):
        """
        Validate configuration after initialization.

        WHY: Prevents invalid configurations that could cause runtime errors.
        Better to fail fast at configuration time than during pipeline execution.
        """
        # Guard clause: validate confidence threshold
        if not 0.0 <= self.confidence_threshold <= 1.0:
            raise ValueError(
                f"confidence_threshold must be in [0, 1], got {self.confidence_threshold}"
            )

        # Guard clause: validate quality thresholds
        if self.quality_improvement_threshold < 0:
            raise ValueError(
                f"quality_improvement_threshold must be non-negative, "
                f"got {self.quality_improvement_threshold}"
            )

        # Guard clause: validate rollback threshold
        if self.rollback_degradation_threshold > 0:
            raise ValueError(
                f"rollback_degradation_threshold should be negative (degradation), "
                f"got {self.rollback_degradation_threshold}"
            )

        # Guard clause: validate story points
        if self.simple_task_max_story_points >= self.complex_task_min_story_points:
            raise ValueError(
                f"simple_task_max_story_points ({self.simple_task_max_story_points}) "
                f"must be less than complex_task_min_story_points "
                f"({self.complex_task_min_story_points})"
            )

        # Guard clause: validate uncertainty strategy
        valid_strategies = {"bayesian", "monte_carlo", "ensemble"}
        if self.default_uncertainty_strategy not in valid_strategies:
            raise ValueError(
                f"default_uncertainty_strategy must be one of {valid_strategies}, "
                f"got {self.default_uncertainty_strategy}"
            )
