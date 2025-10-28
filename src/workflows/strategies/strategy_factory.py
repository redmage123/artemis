#!/usr/bin/env python3
"""
Pipeline Strategy Factory.

WHY: Centralize strategy creation with dispatch table pattern.
RESPONSIBILITY: Create strategy instances by name with type safety.
PATTERNS: Factory Pattern, Dispatch Table Pattern.

Dependencies: typing, base_strategy, concrete strategies
"""

from typing import Dict, Type, Any, Callable

from .base_strategy import PipelineStrategy
from .standard_strategy import StandardPipelineStrategy
from .fast_strategy import FastPipelineStrategy
from .parallel_strategy import ParallelPipelineStrategy
from .checkpoint_strategy import CheckpointPipelineStrategy


# Dispatch table: strategy name -> strategy class
STRATEGY_REGISTRY: Dict[str, Type[PipelineStrategy]] = {
    "standard": StandardPipelineStrategy,
    "fast": FastPipelineStrategy,
    "parallel": ParallelPipelineStrategy,
    "checkpoint": CheckpointPipelineStrategy
}


def get_strategy(
    strategy_name: str,
    verbose: bool = True,
    **kwargs
) -> PipelineStrategy:
    """
    Factory function to create pipeline strategy by name.

    WHY: Decouple strategy creation from usage with clean API.
    RESPONSIBILITY: Validate strategy name and instantiate strategy.
    PATTERNS: Factory Pattern - centralized object creation.

    Args:
        strategy_name: Strategy name ("standard", "fast", "parallel", "checkpoint")
        verbose: Enable verbose logging
        **kwargs: Strategy-specific parameters:
            - FastPipelineStrategy: skip_stages (List[str])
            - ParallelPipelineStrategy: max_workers (int)
            - CheckpointPipelineStrategy: checkpoint_dir (str)

    Returns:
        PipelineStrategy instance

    Raises:
        ValueError: If strategy_name is unknown

    Examples:
        # Standard strategy
        strategy = get_strategy("standard")

        # Fast strategy with custom skip list
        strategy = get_strategy("fast", skip_stages=["architecture"])

        # Parallel strategy with custom worker count
        strategy = get_strategy("parallel", max_workers=8)

        # Checkpoint strategy with custom directory
        strategy = get_strategy("checkpoint", checkpoint_dir="/tmp/my_checkpoints")
    """
    # Guard: Validate strategy name
    if not isinstance(strategy_name, str):
        raise TypeError("strategy_name must be a string")

    if not strategy_name:
        raise ValueError("strategy_name cannot be empty")

    # Guard: Check strategy exists
    if strategy_name not in STRATEGY_REGISTRY:
        available = ", ".join(STRATEGY_REGISTRY.keys())
        raise ValueError(
            f"Unknown strategy: {strategy_name}. "
            f"Available: {available}"
        )

    # Create strategy instance
    strategy_class = STRATEGY_REGISTRY[strategy_name]
    return strategy_class(verbose=verbose, **kwargs)


def list_strategies() -> list[str]:
    """
    Get list of available strategy names.

    WHY: Provide discovery mechanism for available strategies.
    RESPONSIBILITY: Return registered strategy names.

    Returns:
        List of strategy names
    """
    return list(STRATEGY_REGISTRY.keys())


def register_strategy(name: str, strategy_class: Type[PipelineStrategy]):
    """
    Register a custom strategy.

    WHY: Enable extension with custom strategies.
    RESPONSIBILITY: Add strategy to registry with validation.

    Args:
        name: Strategy name
        strategy_class: Strategy class (must extend PipelineStrategy)

    Raises:
        TypeError: If strategy_class doesn't extend PipelineStrategy
        ValueError: If name already registered
    """
    # Guard: Validate inputs
    if not isinstance(name, str):
        raise TypeError("name must be a string")

    if not name:
        raise ValueError("name cannot be empty")

    if not issubclass(strategy_class, PipelineStrategy):
        raise TypeError("strategy_class must extend PipelineStrategy")

    if name in STRATEGY_REGISTRY:
        raise ValueError(f"Strategy '{name}' already registered")

    # Register strategy
    STRATEGY_REGISTRY[name] = strategy_class


def unregister_strategy(name: str):
    """
    Unregister a custom strategy.

    WHY: Enable cleanup of custom strategies.
    RESPONSIBILITY: Remove strategy from registry.

    Args:
        name: Strategy name to unregister

    Raises:
        ValueError: If strategy not found
    """
    # Guard: Validate name
    if name not in STRATEGY_REGISTRY:
        raise ValueError(f"Strategy '{name}' not registered")

    # Remove strategy
    del STRATEGY_REGISTRY[name]
