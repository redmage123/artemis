#!/usr/bin/env python3
"""
Research Strategy Factory

WHY: Provides centralized creation of research strategy objects using the Factory
Pattern. Decouples strategy instantiation from usage, enabling easy addition of new
strategies without modifying client code.

RESPONSIBILITY: Manages research strategy creation and registration:
- Create strategy instances by name
- Create all available strategies at once
- Maintain registry of available strategies
- Provide list of supported strategy names

PATTERNS:
- Factory Pattern: Centralized object creation with consistent interface
- Registry Pattern: Dictionary-based strategy registration
- Dispatch Table Pattern: Dictionary lookup instead of if/elif chains
- Guard Clause Pattern: Early validation before creation
"""

from typing import Any, Dict, List

from research.base_strategy import ResearchStrategy
from research.github_strategy import GitHubResearchStrategy
from research.huggingface_strategy import HuggingFaceResearchStrategy
from research.local_strategy import LocalExamplesResearchStrategy


class ResearchStrategyFactory:
    """
    Factory for creating research strategy instances.

    Uses a registry (dispatch table) to map strategy names to their classes,
    avoiding if/elif chains and enabling easy extension with new strategies.
    """

    # Strategy registry: maps strategy name to class (dispatch table)
    _STRATEGY_REGISTRY: Dict[str, type] = {
        "github": GitHubResearchStrategy,
        "huggingface": HuggingFaceResearchStrategy,
        "local": LocalExamplesResearchStrategy,
    }

    @classmethod
    def create_strategy(cls, source_name: str, **kwargs: Any) -> ResearchStrategy:
        """
        Create research strategy by name.

        Uses dispatch table (dictionary) instead of if/elif chain for O(1) lookup.

        Args:
            source_name: Name of strategy (github, huggingface, local)
            **kwargs: Arguments to pass to strategy constructor

        Returns:
            Instantiated ResearchStrategy object

        Raises:
            ValueError: If source_name is not in the registry
        """
        # Guard clause: validate strategy name exists
        source_lower = source_name.lower()
        if source_lower not in cls._STRATEGY_REGISTRY:
            available = ", ".join(cls._STRATEGY_REGISTRY.keys())
            raise ValueError(
                f"Unknown research source: {source_name}. "
                f"Available sources: {available}"
            )

        # Dispatch table lookup (no if/elif chain)
        strategy_class = cls._STRATEGY_REGISTRY[source_lower]

        # Instantiate and return strategy
        return strategy_class(**kwargs)

    @classmethod
    def create_all_strategies(cls, **kwargs: Any) -> List[ResearchStrategy]:
        """
        Create instances of all available strategies.

        Useful for searching across all sources simultaneously.

        Args:
            **kwargs: Arguments to pass to all strategy constructors

        Returns:
            List of all instantiated research strategies
        """
        # Use list comprehension to create all strategies (no explicit loop)
        return [
            strategy_class(**kwargs)
            for strategy_class in cls._STRATEGY_REGISTRY.values()
        ]

    @classmethod
    def get_available_sources(cls) -> List[str]:
        """
        Get list of available research source names.

        Returns:
            List of registered strategy names (e.g., ["github", "huggingface", "local"])
        """
        return list(cls._STRATEGY_REGISTRY.keys())

    @classmethod
    def register_strategy(cls, name: str, strategy_class: type) -> None:
        """
        Register a new research strategy.

        Allows extending the factory with custom strategies at runtime.

        Args:
            name: Name to register the strategy under
            strategy_class: Strategy class to register

        Raises:
            ValueError: If strategy_class is not a subclass of ResearchStrategy
        """
        # Guard clause: validate strategy class
        if not issubclass(strategy_class, ResearchStrategy):
            raise ValueError(
                f"Strategy class {strategy_class.__name__} must inherit from ResearchStrategy"
            )

        # Add to registry
        cls._STRATEGY_REGISTRY[name.lower()] = strategy_class
