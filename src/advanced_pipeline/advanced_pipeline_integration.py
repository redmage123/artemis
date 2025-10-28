#!/usr/bin/env python3
"""
Module: advanced_pipeline_integration.py

WHY this module exists:
    Main facade for advanced pipeline integration. Provides top-level interface
    for using advanced pipeline features and simplifies integration.

RESPONSIBILITY:
    - Provide simple API for complex functionality
    - Hide details of configuration, mode selection, and feature coordination
    - Offer factory methods for common configurations
    - Expose configuration manager and performance summaries

PATTERNS:
    - Facade Pattern: Simple interface for complex functionality
    - Factory Pattern: Create pre-configured instances
"""

from typing import Dict, Any, Optional

from pipeline_observer import PipelineObservable
from advanced_pipeline.pipeline_config import AdvancedPipelineConfig
from advanced_pipeline.advanced_pipeline_strategy import AdvancedPipelineStrategy
from advanced_pipeline.configuration_manager import ConfigurationManager


class AdvancedPipelineIntegration:
    """
    Main facade for advanced pipeline integration.

    WHAT: Top-level interface for using advanced pipeline features.
    Simplifies integration with ArtemisOrchestrator.

    WHY: Provides simple API for complex functionality. Hides details
    of configuration, mode selection, and feature coordination.

    Design pattern: Facade

    Usage:
        # Create integration with default config
        integration = AdvancedPipelineIntegration.create_default()

        # Use as drop-in replacement for StandardPipelineStrategy
        orchestrator = ArtemisOrchestrator(
            card_id="TASK-001",
            board=board,
            messenger=messenger,
            rag=rag,
            strategy=integration.get_strategy()
        )
    """

    def __init__(
        self,
        config: Optional[AdvancedPipelineConfig] = None,
        observable: Optional[PipelineObservable] = None
    ):
        """
        Initialize advanced pipeline integration.

        Args:
            config: Pipeline configuration
            observable: Pipeline observable for events
        """
        self.config = config or AdvancedPipelineConfig()
        self.observable = observable

        # Create strategy (this is what orchestrator uses)
        self.strategy = AdvancedPipelineStrategy(
            config=self.config,
            observable=observable
        )

    def get_strategy(self) -> AdvancedPipelineStrategy:
        """
        Get pipeline strategy for orchestrator.

        WHY: Orchestrator expects PipelineStrategy object. This method
        returns configured AdvancedPipelineStrategy.

        Returns:
            AdvancedPipelineStrategy instance
        """
        return self.strategy

    def get_config_manager(self) -> ConfigurationManager:
        """
        Get configuration manager for runtime config changes.

        Returns:
            ConfigurationManager instance
        """
        return self.strategy.config_manager

    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get performance summary.

        Returns:
            Performance metrics summary
        """
        return self.strategy.get_performance_summary()

    @staticmethod
    def create_default(
        observable: Optional[PipelineObservable] = None
    ) -> 'AdvancedPipelineIntegration':
        """
        Create integration with default configuration.

        WHY: Factory method for common case - default configuration.
        Simplifies usage for standard scenarios.

        Args:
            observable: Pipeline observable

        Returns:
            Configured AdvancedPipelineIntegration
        """
        return AdvancedPipelineIntegration(
            config=AdvancedPipelineConfig(),
            observable=observable
        )

    @staticmethod
    def create_conservative(
        observable: Optional[PipelineObservable] = None
    ) -> 'AdvancedPipelineIntegration':
        """
        Create integration with conservative configuration.

        WHY: For production rollout - only enable most stable features.

        Args:
            observable: Pipeline observable

        Returns:
            Configured AdvancedPipelineIntegration with conservative settings
        """
        config = AdvancedPipelineConfig(
            enable_dynamic_pipeline=True,  # Stable feature
            enable_two_pass=False,         # More experimental
            enable_thermodynamic=True,     # Stable, useful
            auto_mode_selection=False      # Manual control
        )

        return AdvancedPipelineIntegration(
            config=config,
            observable=observable
        )

    @staticmethod
    def create_experimental(
        observable: Optional[PipelineObservable] = None
    ) -> 'AdvancedPipelineIntegration':
        """
        Create integration with all experimental features enabled.

        WHY: For testing and evaluation - enables everything.

        Args:
            observable: Pipeline observable

        Returns:
            Configured AdvancedPipelineIntegration with all features
        """
        config = AdvancedPipelineConfig(
            enable_dynamic_pipeline=True,
            enable_two_pass=True,
            enable_thermodynamic=True,
            auto_mode_selection=True,
            parallel_execution_enabled=True,
            enable_temperature_annealing=True
        )

        return AdvancedPipelineIntegration(
            config=config,
            observable=observable
        )
