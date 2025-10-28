#!/usr/bin/env python3
"""
WHY: Select and create appropriate reasoning strategies based on configuration.

RESPONSIBILITY: Factory for reasoning strategy instances with proper initialization.

PATTERNS:
- Factory Pattern: Create strategy instances
- Strategy Pattern: Select different reasoning approaches
- Guard Clauses: Early validation and returns
"""

from typing import Optional, Dict, Any
import logging

from reasoning_strategies import (
    ReasoningStrategy,
    ReasoningStrategyBase,
    ReasoningStrategyFactory,
    ChainOfThoughtStrategy,
    TreeOfThoughtsStrategy,
    LogicOfThoughtsStrategy,
    SelfConsistencyStrategy
)
from reasoning.models import ReasoningConfig, ReasoningType


class StrategySelector:
    """
    Select and create reasoning strategies based on configuration.

    WHY: Centralize strategy creation logic with proper parameter handling.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize strategy selector.

        Args:
            logger: Logger instance for diagnostics
        """
        self.logger = logger or logging.getLogger(self.__class__.__name__)

    def create_strategy(self, config: ReasoningConfig) -> ReasoningStrategyBase:
        """
        Create reasoning strategy from configuration.

        WHY: Factory method that handles strategy-specific initialization.

        Args:
            config: Reasoning configuration

        Returns:
            Initialized reasoning strategy instance

        Pattern: Factory Method with guard clauses
        """
        # Guard clause: Validate config
        if not config:
            self.logger.warning("No config provided, using default CoT")
            return self._create_default_strategy()

        # Guard clause: Check if strategy is enabled
        if not config.enabled:
            self.logger.debug("Reasoning disabled in config")
            return self._create_default_strategy()

        # Build kwargs based on strategy type
        kwargs = self._build_strategy_kwargs(config)

        # Create strategy using factory
        try:
            strategy_enum = self._convert_to_strategy_enum(config.strategy)
            return ReasoningStrategyFactory.create(strategy_enum, **kwargs)
        except Exception as e:
            self.logger.error(f"Failed to create strategy: {e}")
            return self._create_default_strategy()

    def _build_strategy_kwargs(self, config: ReasoningConfig) -> Dict[str, Any]:
        """
        Build kwargs for strategy creation based on config.

        WHY: Isolate parameter extraction logic.

        Args:
            config: Reasoning configuration

        Returns:
            Dictionary of kwargs for strategy constructor

        Pattern: Dispatch table for different strategy types
        """
        base_kwargs = {"logger": self.logger}

        # Dispatch table for strategy-specific parameters
        strategy_params_map: Dict[ReasoningType, Dict[str, Any]] = {
            ReasoningType.TREE_OF_THOUGHTS: {
                "branching_factor": config.tot_branching_factor,
                "max_depth": config.tot_max_depth
            },
            ReasoningType.SELF_CONSISTENCY: {
                "num_samples": config.sc_num_samples
            },
            ReasoningType.CHAIN_OF_THOUGHT: {},
            ReasoningType.LOGIC_OF_THOUGHTS: {}
        }

        specific_params = strategy_params_map.get(config.strategy, {})
        return {**base_kwargs, **specific_params}

    def _convert_to_strategy_enum(self, reasoning_type: ReasoningType) -> ReasoningStrategy:
        """
        Convert ReasoningType to ReasoningStrategy enum.

        WHY: Bridge between new and legacy enum types.

        Args:
            reasoning_type: ReasoningType enum value

        Returns:
            ReasoningStrategy enum value

        Pattern: Dispatch table for enum conversion
        """
        # Dispatch table for enum conversion
        conversion_map: Dict[ReasoningType, ReasoningStrategy] = {
            ReasoningType.CHAIN_OF_THOUGHT: ReasoningStrategy.CHAIN_OF_THOUGHT,
            ReasoningType.TREE_OF_THOUGHTS: ReasoningStrategy.TREE_OF_THOUGHTS,
            ReasoningType.LOGIC_OF_THOUGHTS: ReasoningStrategy.LOGIC_OF_THOUGHTS,
            ReasoningType.SELF_CONSISTENCY: ReasoningStrategy.SELF_CONSISTENCY
        }

        return conversion_map.get(
            reasoning_type,
            ReasoningStrategy.CHAIN_OF_THOUGHT
        )

    def _create_default_strategy(self) -> ReasoningStrategyBase:
        """
        Create default Chain of Thought strategy.

        WHY: Fallback when configuration is invalid or disabled.

        Returns:
            Default ChainOfThoughtStrategy instance
        """
        return ChainOfThoughtStrategy(logger=self.logger)


def select_strategy(config: ReasoningConfig) -> ReasoningStrategyBase:
    """
    Convenience function to select and create strategy.

    WHY: Simple function API for one-off strategy creation.

    Args:
        config: Reasoning configuration

    Returns:
        Initialized reasoning strategy

    Example:
        strategy = select_strategy(config)
        prompt = strategy.generate_prompt(task="Solve problem")
    """
    selector = StrategySelector()
    return selector.create_strategy(config)
