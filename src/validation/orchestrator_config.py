#!/usr/bin/env python3
"""
Anti-Hallucination Orchestrator Configuration

WHY: Provide configurable control over intelligent validation strategy selection
RESPONSIBILITY: Define configuration options for orchestrator behavior
PATTERNS: Configuration Object, Factory

This module provides configuration options to control how the orchestrator
selects validation strategies. Users can customize:
- Risk thresholds
- Profile selection behavior
- Technique preferences
- Time budget defaults
- Learning behavior

Example:
    from validation.orchestrator_config import OrchestratorConfig

    # Custom configuration
    config = OrchestratorConfig(
        enable_intelligent_selection=True,
        default_profile='thorough',
        prefer_speed_over_thoroughness=False
    )

    # Use with integration
    integration = ArtemisValidationIntegration(logger, config=config)
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field

from artemis_exceptions import (
    ConfigurationError,
    wrap_exception,
)


@dataclass
class OrchestratorConfig:
    """
    Configuration for Anti-Hallucination Orchestrator.

    WHY: Centralize all configuration options for orchestrator
    RESPONSIBILITY: Store and validate configuration settings
    PATTERNS: Configuration Object
    """

    # Enable/disable intelligent selection
    enable_intelligent_selection: bool = True

    # Default validation profile if not auto-selected
    default_profile: str = 'standard'  # minimal, standard, thorough, critical

    # Risk assessment thresholds
    complexity_low_threshold: int = 50
    complexity_medium_threshold: int = 200
    complexity_high_threshold: int = 500
    dependencies_medium_threshold: int = 5
    dependencies_high_threshold: int = 10

    # Profile selection behavior
    prefer_speed_over_thoroughness: bool = False
    always_use_critical_for_security: bool = True
    downgrade_on_time_constraint: bool = True

    # Technique preferences (optional overrides)
    always_enable_techniques: Set[str] = field(default_factory=lambda: {'chain_of_thought'})
    never_enable_techniques: Set[str] = field(default_factory=set)
    preferred_techniques: List[str] = field(default_factory=list)

    # Time budget defaults (milliseconds)
    default_time_budget_ms: Optional[float] = None
    max_time_budget_ms: float = 10000
    min_time_budget_ms: float = 200

    # Historical learning
    enable_historical_learning: bool = True
    max_historical_failures_stored: int = 1000

    # Logging
    log_strategy_selection: bool = True
    log_technique_selection: bool = True
    log_risk_assessment: bool = True

    # Advanced options
    allow_profile_override: bool = True
    use_probabilistic_reduction: bool = True
    adapt_to_framework: bool = True

    def validate(self) -> bool:
        """
        Validate configuration settings.

        WHY: Ensure configuration values are sensible
        RESPONSIBILITY: Check ranges and dependencies

        Returns:
            True if valid

        Raises:
            ConfigurationError: If configuration is invalid
        """
        try:
            # Guard: Invalid profile
            valid_profiles = {'minimal', 'standard', 'thorough', 'critical'}
            if self.default_profile not in valid_profiles:
                raise ConfigurationError(
                    f"Invalid default_profile: {self.default_profile}",
                    context={"valid_profiles": list(valid_profiles)}
                )

            # Guard: Invalid complexity thresholds
            if not (0 < self.complexity_low_threshold < self.complexity_medium_threshold < self.complexity_high_threshold):
                raise ConfigurationError(
                    "Complexity thresholds must be in ascending order",
                    context={
                        "low": self.complexity_low_threshold,
                        "medium": self.complexity_medium_threshold,
                        "high": self.complexity_high_threshold
                    }
                )

            # Guard: Invalid dependency thresholds
            if not (0 < self.dependencies_medium_threshold < self.dependencies_high_threshold):
                raise ConfigurationError(
                    "Dependency thresholds must be in ascending order",
                    context={
                        "medium": self.dependencies_medium_threshold,
                        "high": self.dependencies_high_threshold
                    }
                )

            # Guard: Invalid time budgets
            if self.default_time_budget_ms is not None:
                if not (self.min_time_budget_ms <= self.default_time_budget_ms <= self.max_time_budget_ms):
                    raise ConfigurationError(
                        "default_time_budget_ms must be between min and max",
                        context={
                            "min": self.min_time_budget_ms,
                            "default": self.default_time_budget_ms,
                            "max": self.max_time_budget_ms
                        }
                    )

            return True

        except ConfigurationError:
            raise
        except Exception as e:
            raise wrap_exception(
                e,
                ConfigurationError,
                "Configuration validation failed",
                {"default_profile": self.default_profile}
            )

    def get_risk_thresholds(self) -> Dict[str, int]:
        """Get risk assessment thresholds."""
        return {
            'complexity_low': self.complexity_low_threshold,
            'complexity_medium': self.complexity_medium_threshold,
            'complexity_high': self.complexity_high_threshold,
            'dependencies_medium': self.dependencies_medium_threshold,
            'dependencies_high': self.dependencies_high_threshold,
        }

    def should_enable_technique(self, technique_name: str) -> Optional[bool]:
        """
        Check if technique should be enabled/disabled.

        WHY: Allow configuration to override technique selection
        RESPONSIBILITY: Return True/False/None for enable/disable/auto

        Args:
            technique_name: Name of validation technique

        Returns:
            True to force enable, False to force disable, None for auto
        """
        # Guard: Never enable
        if technique_name in self.never_enable_techniques:
            return False

        # Guard: Always enable
        if technique_name in self.always_enable_techniques:
            return True

        # Auto-select
        return None

    def adjust_profile_for_speed(self, profile: str) -> str:
        """
        Adjust profile if speed is preferred.

        WHY: Allow users to prefer faster validation
        RESPONSIBILITY: Downgrade profile if speed preference enabled

        Args:
            profile: Selected profile

        Returns:
            Adjusted profile
        """
        # Guard: Speed not preferred
        if not self.prefer_speed_over_thoroughness:
            return profile

        # Downgrade profile for speed
        downgrades = {
            'critical': 'thorough',
            'thorough': 'standard',
            'standard': 'minimal',
            'minimal': 'minimal'
        }

        return downgrades.get(profile, profile)


# Default configuration instance
DEFAULT_CONFIG = OrchestratorConfig()


# Preset configurations
def get_speed_optimized_config() -> OrchestratorConfig:
    """Get configuration optimized for speed."""
    return OrchestratorConfig(
        default_profile='minimal',
        prefer_speed_over_thoroughness=True,
        complexity_low_threshold=100,
        complexity_medium_threshold=300,
        complexity_high_threshold=700,
        log_strategy_selection=False,
        log_technique_selection=False,
        log_risk_assessment=False,
    )


def get_quality_optimized_config() -> OrchestratorConfig:
    """Get configuration optimized for quality."""
    return OrchestratorConfig(
        default_profile='thorough',
        prefer_speed_over_thoroughness=False,
        complexity_low_threshold=30,
        complexity_medium_threshold=100,
        complexity_high_threshold=300,
        always_use_critical_for_security=True,
        always_enable_techniques={'chain_of_thought', 'static_analysis', 'rag_validation'},
        log_strategy_selection=True,
        log_technique_selection=True,
        log_risk_assessment=True,
    )


def get_balanced_config() -> OrchestratorConfig:
    """Get balanced configuration (default)."""
    return DEFAULT_CONFIG


def get_critical_systems_config() -> OrchestratorConfig:
    """Get configuration for critical systems."""
    return OrchestratorConfig(
        default_profile='critical',
        prefer_speed_over_thoroughness=False,
        complexity_low_threshold=20,
        complexity_medium_threshold=80,
        complexity_high_threshold=200,
        always_use_critical_for_security=True,
        downgrade_on_time_constraint=False,  # Never downgrade for critical systems
        always_enable_techniques={
            'chain_of_thought',
            'static_analysis',
            'rag_validation',
            'self_critique',
            'formal_specs'
        },
        enable_historical_learning=True,
        log_strategy_selection=True,
        log_technique_selection=True,
        log_risk_assessment=True,
    )
