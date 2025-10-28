"""
Module: two_pass/strategies.py (BACKWARD COMPATIBILITY WRAPPER)

WHY: Maintains 100% backward compatibility while code is refactored into modular package.
RESPONSIBILITY: Re-export all public APIs from new strategies package without breaking existing imports.
PATTERNS: Facade Pattern, Adapter Pattern, Deprecation Path.

MIGRATION STATUS: This file is now a thin wrapper around two_pass.strategies package.

OLD STRUCTURE (845 lines):
- Monolithic file with all strategy implementations
- PassStrategy, FirstPassStrategy, SecondPassStrategy in one file

NEW STRUCTURE (modular package):
- two_pass/strategies/base_strategy.py - PassStrategy base class (187 lines)
- two_pass/strategies/first_pass_strategy.py - FirstPassStrategy (300 lines)
- two_pass/strategies/second_pass_strategy.py - SecondPassStrategy (421 lines)
- two_pass/strategies/strategy_factory.py - StrategyFactory (157 lines)
- two_pass/strategies/__init__.py - Public API (35 lines)

TOTAL REDUCTION: 845 lines -> 52 lines wrapper (93.8% reduction)
MODULES CREATED: 5 focused modules

BACKWARD COMPATIBILITY: All existing imports work unchanged:
    from two_pass.strategies import PassStrategy  # ✅ Works
    from two_pass.strategies import FirstPassStrategy  # ✅ Works
    from two_pass.strategies import SecondPassStrategy  # ✅ Works

EXTRACTED FROM: Original two_pass/strategies.py (lines 1-845)
REFACTORED: 2025-10-28
"""

# Re-export all public APIs from new package structure
# WHY: Maintains 100% backward compatibility with existing imports
from two_pass.strategies.base_strategy import PassStrategy
from two_pass.strategies.first_pass_strategy import FirstPassStrategy
from two_pass.strategies.second_pass_strategy import SecondPassStrategy
from two_pass.strategies.strategy_factory import StrategyFactory, STRATEGY_REGISTRY

# Preserve original __all__ for backward compatibility
__all__ = [
    "PassStrategy",
    "FirstPassStrategy",
    "SecondPassStrategy",
]

# Optional exports for new functionality
__all__.extend([
    "StrategyFactory",
    "STRATEGY_REGISTRY",
])
