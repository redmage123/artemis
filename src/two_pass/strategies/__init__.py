"""
Module: two_pass/strategies/__init__.py

WHY: Provides clean public API for two_pass strategies package.
RESPONSIBILITY: Export public interfaces, maintain backward compatibility, hide implementation details.
PATTERNS: Facade Pattern, Information Hiding, Single Point of Entry.

This module handles:
- Public API exports for strategy classes
- Factory exports for strategy creation
- Backward compatibility with original monolithic module
- Clean namespace management

PACKAGE STRUCTURE:
- base_strategy.py: Abstract PassStrategy base class
- first_pass_strategy.py: FirstPassStrategy implementation
- second_pass_strategy.py: SecondPassStrategy implementation
- strategy_factory.py: StrategyFactory for creating strategies

REFACTORED FROM: two_pass/strategies.py (845 lines -> 4 focused modules)
"""

from two_pass.strategies.base_strategy import PassStrategy
from two_pass.strategies.first_pass_strategy import FirstPassStrategy
from two_pass.strategies.second_pass_strategy import SecondPassStrategy
from two_pass.strategies.strategy_factory import StrategyFactory, STRATEGY_REGISTRY

# Public API - all imports that external code should use
__all__ = [
    # Base class
    "PassStrategy",

    # Concrete strategies
    "FirstPassStrategy",
    "SecondPassStrategy",

    # Factory
    "StrategyFactory",
    "STRATEGY_REGISTRY",
]
