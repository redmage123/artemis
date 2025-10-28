#!/usr/bin/env python3
"""
Module: advanced_pipeline_strategy.py

WHY this module exists:
    Backward compatibility wrapper that re-exports AdvancedPipelineStrategy
    from refactored modular package.

RESPONSIBILITY:
    - Maintain backward compatibility with existing imports
    - Re-export all public API from strategy package
    - Enable seamless transition to modular structure

PATTERNS:
    - Facade Pattern: Single entry point
    - Module Pattern: Clean re-exports

REFACTORING NOTE:
    This file has been refactored into a modular package structure at
    advanced_pipeline/strategy/. The original 810-line monolithic file
    has been broken down into:
        - models.py: Data structures (ExecutionResult, PerformanceMetrics)
        - executors.py: Mode-specific execution strategies
        - confidence_quantifier.py: Uncertainty tracking
        - performance_tracker.py: Performance metrics tracking
        - event_emitter.py: Event emission logic
        - complexity_analyzer.py: Complexity determination
        - strategy_facade.py: Main orchestration facade
        - __init__.py: Public API

    All existing code using AdvancedPipelineStrategy will continue to work
    without modification.

Usage (backward compatible):
    from advanced_pipeline.advanced_pipeline_strategy import AdvancedPipelineStrategy

    strategy = AdvancedPipelineStrategy(config, observable)
    result = strategy.execute(stages, context)
"""

# Re-export from modular package for backward compatibility
from advanced_pipeline.strategy import (
    AdvancedPipelineStrategy,
    AdvancedPipelineStrategyFacade,
    ExecutionResult,
    PerformanceMetrics
)

# Maintain public API
__all__ = [
    "AdvancedPipelineStrategy",
    "AdvancedPipelineStrategyFacade",
    "ExecutionResult",
    "PerformanceMetrics"
]
