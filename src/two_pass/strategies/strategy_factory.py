"""
Module: two_pass/strategies/strategy_factory.py

WHY: Provides factory for creating pass strategies without coupling to concrete implementations.
RESPONSIBILITY: Strategy instantiation, strategy registration, strategy discovery.
PATTERNS: Factory Pattern, Strategy Pattern, Registry Pattern, Open/Closed Principle.

This module handles:
- StrategyFactory: Factory for creating strategy instances
- Strategy registration for extensibility
- Strategy discovery and listing
- Default strategy configuration

CREATED FOR: Modular refactoring of two_pass/strategies.py
ENABLES: Adding new strategies without modifying factory code (Open/Closed Principle)
"""

from typing import Dict, Type, Optional
from pipeline_observer import PipelineObservable

from two_pass.strategies.base_strategy import PassStrategy
from two_pass.strategies.first_pass_strategy import FirstPassStrategy
from two_pass.strategies.second_pass_strategy import SecondPassStrategy
from artemis_exceptions import ConfigurationError


# Strategy registry (dispatch table - Strategy Pattern + Registry Pattern)
# WHY: Enables adding new strategies without modifying factory code
STRATEGY_REGISTRY: Dict[str, Type[PassStrategy]] = {
    "first": FirstPassStrategy,
    "second": SecondPassStrategy,
    "FirstPass": FirstPassStrategy,
    "SecondPass": SecondPassStrategy,
}


class StrategyFactory:
    """
    Factory for creating pass strategies.

    WHY: Decouples strategy creation from strategy usage. Enables adding new
    strategies without modifying client code.

    RESPONSIBILITY: Create strategy instances, manage strategy registry.

    PATTERNS:
    - Factory Pattern: Centralizes object creation
    - Registry Pattern: Dynamic strategy registration
    - Strategy Pattern: Returns strategy interface, not concrete classes
    - Open/Closed Principle: Open for extension (new strategies), closed for modification

    Example:
        factory = StrategyFactory()
        first_pass = factory.create_strategy("first", observable=my_observable)
        second_pass = factory.create_strategy("second", observable=my_observable)
    """

    @staticmethod
    def create_strategy(
        strategy_name: str,
        observable: Optional[PipelineObservable] = None,
        verbose: bool = True
    ) -> PassStrategy:
        """
        Create strategy instance by name.

        WHY: Factory method enables creating strategies without knowing concrete classes.
        Uses dispatch table (no if/elif chain).

        Args:
            strategy_name: Name of strategy ("first", "second", "FirstPass", "SecondPass")
            observable: Optional observer for event notifications
            verbose: Enable verbose logging

        Returns:
            Strategy instance implementing PassStrategy interface

        Raises:
            ConfigurationError: If strategy_name is unknown

        Example:
            strategy = StrategyFactory.create_strategy("first", observable=obs)
        """
        # Guard clause - validate strategy name exists in registry
        if strategy_name not in STRATEGY_REGISTRY:
            raise ConfigurationError(
                f"Unknown strategy: {strategy_name}",
                context={
                    "strategy_name": strategy_name,
                    "available_strategies": list(STRATEGY_REGISTRY.keys())
                }
            )

        # Dispatch table lookup - NO if/elif chain
        strategy_class = STRATEGY_REGISTRY[strategy_name]
        return strategy_class(observable=observable, verbose=verbose)

    @staticmethod
    def register_strategy(name: str, strategy_class: Type[PassStrategy]) -> None:
        """
        Register new strategy (Open/Closed Principle - open for extension).

        WHY: Enables adding custom strategies without modifying factory code.
        Supports extensibility and plugin architecture.

        Args:
            name: Strategy name for lookup
            strategy_class: Strategy class (must inherit from PassStrategy)

        Raises:
            ConfigurationError: If strategy_class doesn't inherit from PassStrategy

        Example:
            class CustomStrategy(PassStrategy):
                ...
            StrategyFactory.register_strategy("custom", CustomStrategy)
        """
        # Guard clause - validate strategy_class is PassStrategy subclass
        if not issubclass(strategy_class, PassStrategy):
            raise ConfigurationError(
                f"Strategy class must inherit from PassStrategy",
                context={
                    "strategy_class": strategy_class.__name__,
                    "expected_base": "PassStrategy"
                }
            )

        STRATEGY_REGISTRY[name] = strategy_class

    @staticmethod
    def list_strategies() -> list[str]:
        """
        List all available strategy names.

        WHY: Enables discovery of available strategies for UI/CLI/documentation.

        Returns:
            List of registered strategy names

        Example:
            strategies = StrategyFactory.list_strategies()
            # ['first', 'second', 'FirstPass', 'SecondPass']
        """
        return list(STRATEGY_REGISTRY.keys())

    @staticmethod
    def has_strategy(name: str) -> bool:
        """
        Check if strategy is registered.

        WHY: Validation before strategy creation, avoids exception handling.

        Args:
            name: Strategy name to check

        Returns:
            True if strategy is registered

        Example:
            if StrategyFactory.has_strategy("custom"):
                strategy = StrategyFactory.create_strategy("custom")
        """
        return name in STRATEGY_REGISTRY


__all__ = [
    "StrategyFactory",
    "STRATEGY_REGISTRY"
]
