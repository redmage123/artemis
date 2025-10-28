#!/usr/bin/env python3
"""
Reasoning Strategy Factory

WHY: Centralized strategy creation using Factory pattern with dictionary dispatch,
     ensuring extensibility and avoiding lengthy if/elif chains.

RESPONSIBILITY:
    - Create reasoning strategy instances based on strategy type
    - Provide type-safe strategy selection
    - Dispatch to appropriate strategy class using dictionary mapping
    - Validate strategy types and parameters

PATTERNS:
    - Factory Pattern: Centralized object creation
    - Dictionary Dispatch: O(1) lookup instead of if/elif chains
    - Strategy Pattern: Create strategy implementations
    - Guard Clauses: Input validation
"""

from typing import Dict, Any
import logging

from .models import ReasoningStrategy, ReasoningStrategyBase
from .chain_of_thought import ChainOfThoughtStrategy
from .tree_of_thought import TreeOfThoughtsStrategy
from .logic_of_thought import LogicOfThoughtsStrategy
from .self_consistency import SelfConsistencyStrategy


class ReasoningStrategyFactory:
    """
    Factory for creating reasoning strategies.

    WHY: Provides centralized strategy creation using dictionary dispatch pattern
    RESPONSIBILITY: Create and return appropriate reasoning strategy instances
    PATTERNS: Factory pattern with Strategy pattern (dictionary mapping)

    Example:
        factory = ReasoningStrategyFactory()
        strategy = factory.create(ReasoningStrategy.CHAIN_OF_THOUGHT)
        prompt = strategy.generate_prompt("Solve this problem...")
    """

    # Strategy Pattern: Dictionary mapping (avoid if/elif chain)
    # WHY: O(1) lookup, extensible without modifying factory code
    _STRATEGY_MAP: Dict[ReasoningStrategy, type] = {
        ReasoningStrategy.CHAIN_OF_THOUGHT: ChainOfThoughtStrategy,
        ReasoningStrategy.TREE_OF_THOUGHTS: TreeOfThoughtsStrategy,
        ReasoningStrategy.LOGIC_OF_THOUGHTS: LogicOfThoughtsStrategy,
        ReasoningStrategy.SELF_CONSISTENCY: SelfConsistencyStrategy,
    }

    @staticmethod
    def create(
        strategy_type: ReasoningStrategy,
        **kwargs: Any
    ) -> ReasoningStrategyBase:
        """
        Create reasoning strategy instance.

        WHY: Dictionary dispatch pattern ensures extensibility (Open/Closed principle)
        PERFORMANCE: O(1) dictionary lookup instead of sequential if/elif checks
        PATTERNS: Guard clause for validation

        Args:
            strategy_type: Type of reasoning strategy to create
            **kwargs: Strategy-specific parameters (e.g., branching_factor, num_samples)

        Returns:
            Reasoning strategy instance

        Raises:
            ValueError: If strategy_type is not supported

        Examples:
            # Chain of Thought (no extra params needed)
            cot = factory.create(ReasoningStrategy.CHAIN_OF_THOUGHT)

            # Tree of Thoughts with custom branching
            tot = factory.create(
                ReasoningStrategy.TREE_OF_THOUGHTS,
                branching_factor=5,
                max_depth=3
            )

            # Self-Consistency with sample count
            sc = factory.create(
                ReasoningStrategy.SELF_CONSISTENCY,
                num_samples=10
            )
        """
        # Dictionary dispatch pattern (avoid if/elif chain)
        strategy_class = ReasoningStrategyFactory._STRATEGY_MAP.get(strategy_type)

        # Guard clause: Validate strategy type
        if not strategy_class:
            raise ValueError(
                f"Unknown reasoning strategy: {strategy_type}. "
                f"Supported strategies: {list(ReasoningStrategyFactory._STRATEGY_MAP.keys())}"
            )

        # Create and return strategy instance with provided kwargs
        return strategy_class(**kwargs)

    @staticmethod
    def list_available_strategies() -> list[ReasoningStrategy]:
        """
        List all available reasoning strategies.

        WHY: Discoverability - help users know what's available
        RESPONSIBILITY: Enumerate supported strategies

        Returns:
            List of supported strategy types
        """
        return list(ReasoningStrategyFactory._STRATEGY_MAP.keys())

    @staticmethod
    def get_strategy_info(strategy_type: ReasoningStrategy) -> Dict[str, Any]:
        """
        Get information about a specific strategy.

        WHY: Provide metadata about strategies for users
        RESPONSIBILITY: Return strategy details
        PATTERNS: Guard clause for validation

        Args:
            strategy_type: Strategy type to get info for

        Returns:
            Dictionary with strategy information

        Raises:
            ValueError: If strategy_type is not supported
        """
        # Guard clause: Validate strategy type
        strategy_class = ReasoningStrategyFactory._STRATEGY_MAP.get(strategy_type)
        if not strategy_class:
            raise ValueError(
                f"Unknown reasoning strategy: {strategy_type}"
            )

        # Dispatch table for strategy metadata
        # WHY: Dictionary provides O(1) lookup for strategy details
        _STRATEGY_INFO: Dict[ReasoningStrategy, Dict[str, Any]] = {
            ReasoningStrategy.CHAIN_OF_THOUGHT: {
                "name": "Chain of Thought",
                "description": "Step-by-step reasoning with explicit intermediate steps",
                "best_for": "Complex problems requiring sequential reasoning",
                "parameters": {
                    "logger": "Optional logging.Logger instance"
                }
            },
            ReasoningStrategy.TREE_OF_THOUGHTS: {
                "name": "Tree of Thoughts",
                "description": "Explores multiple reasoning paths in parallel",
                "best_for": "Problems with multiple solution approaches",
                "parameters": {
                    "branching_factor": "Number of branches per node (default: 3)",
                    "max_depth": "Maximum tree depth (default: 4)",
                    "logger": "Optional logging.Logger instance"
                }
            },
            ReasoningStrategy.LOGIC_OF_THOUGHTS: {
                "name": "Logic of Thoughts",
                "description": "Formal logical reasoning with premises and deductions",
                "best_for": "Problems requiring logical proofs or formal reasoning",
                "parameters": {
                    "logger": "Optional logging.Logger instance"
                }
            },
            ReasoningStrategy.SELF_CONSISTENCY: {
                "name": "Self-Consistency",
                "description": "Multiple samples with majority voting",
                "best_for": "Improving reliability through consensus",
                "parameters": {
                    "num_samples": "Number of samples to collect (default: 5)",
                    "logger": "Optional logging.Logger instance"
                }
            }
        }

        return _STRATEGY_INFO[strategy_type]


class StrategyBuilder:
    """
    Builder for creating strategies with fluent interface.

    WHY: Provide convenient, readable strategy construction
    RESPONSIBILITY: Chainable configuration and creation
    PATTERNS: Builder Pattern with fluent interface

    Example:
        strategy = (
            StrategyBuilder()
            .with_type(ReasoningStrategy.TREE_OF_THOUGHTS)
            .with_branching_factor(5)
            .with_max_depth(3)
            .build()
        )
    """

    def __init__(self):
        """Initialize builder with default values."""
        self._strategy_type: ReasoningStrategy = ReasoningStrategy.CHAIN_OF_THOUGHT
        self._kwargs: Dict[str, Any] = {}

    def with_type(self, strategy_type: ReasoningStrategy) -> 'StrategyBuilder':
        """
        Set strategy type.

        Args:
            strategy_type: Strategy type to create

        Returns:
            Self for method chaining
        """
        self._strategy_type = strategy_type
        return self

    def with_branching_factor(self, factor: int) -> 'StrategyBuilder':
        """
        Set branching factor (for Tree of Thoughts).

        Args:
            factor: Number of branches per node

        Returns:
            Self for method chaining
        """
        self._kwargs['branching_factor'] = factor
        return self

    def with_max_depth(self, depth: int) -> 'StrategyBuilder':
        """
        Set maximum depth (for Tree of Thoughts).

        Args:
            depth: Maximum tree depth

        Returns:
            Self for method chaining
        """
        self._kwargs['max_depth'] = depth
        return self

    def with_num_samples(self, samples: int) -> 'StrategyBuilder':
        """
        Set number of samples (for Self-Consistency).

        Args:
            samples: Number of samples to collect

        Returns:
            Self for method chaining
        """
        self._kwargs['num_samples'] = samples
        return self

    def with_logger(self, logger: logging.Logger) -> 'StrategyBuilder':
        """
        Set logger instance.

        Args:
            logger: Logger instance

        Returns:
            Self for method chaining
        """
        self._kwargs['logger'] = logger
        return self

    def build(self) -> ReasoningStrategyBase:
        """
        Build the configured strategy.

        Returns:
            Constructed reasoning strategy

        Raises:
            ValueError: If strategy type is invalid
        """
        return ReasoningStrategyFactory.create(
            self._strategy_type,
            **self._kwargs
        )
