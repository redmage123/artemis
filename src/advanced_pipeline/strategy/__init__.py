#!/usr/bin/env python3
"""
Package: advanced_pipeline.strategy

WHY this package exists:
    Modular implementation of advanced pipeline strategy with separate
    components for execution, tracking, and analysis.

RESPONSIBILITY:
    - Provide clean public API for advanced pipeline strategy
    - Export facade for backward compatibility
    - Organize strategy components

PATTERNS:
    - Facade Pattern: Single entry point through AdvancedPipelineStrategy
    - Module Pattern: Organized components with clean exports

Public API:
    - AdvancedPipelineStrategy: Main facade (backward compatible)
    - ExecutionResult: Result data structure
    - PerformanceMetrics: Performance data structure

Usage:
    from advanced_pipeline.strategy import AdvancedPipelineStrategy

    strategy = AdvancedPipelineStrategy(config, observable)
    result = strategy.execute(stages, context)
"""

from advanced_pipeline.strategy.strategy_facade import AdvancedPipelineStrategyFacade
from advanced_pipeline.strategy.models import ExecutionResult, PerformanceMetrics

# Export facade as AdvancedPipelineStrategy for backward compatibility
AdvancedPipelineStrategy = AdvancedPipelineStrategyFacade

# Public API
__all__ = [
    "AdvancedPipelineStrategy",
    "AdvancedPipelineStrategyFacade",
    "ExecutionResult",
    "PerformanceMetrics"
]
