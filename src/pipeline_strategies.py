#!/usr/bin/env python3
"""
Pipeline Execution Strategies (BACKWARD COMPATIBILITY WRAPPER)

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
! DEPRECATED: This module is a backward compatibility wrapper.                !
! NEW CODE SHOULD USE: workflows.strategies package                           !
!                                                                              !
! Refactored: 2025-10-27                                                      !
! Original: 856 lines                                                         !
! New package: workflows/strategies/ (6 modules)                              !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

WHY: Maintain backward compatibility during migration.
RESPONSIBILITY: Re-export all public APIs from new package.
PATTERNS: Facade Pattern - unified interface to refactored modules.

Provides different execution strategies for the Artemis pipeline, implementing
the Strategy Pattern for flexible and extensible pipeline execution.

SOLID Principles:
- Single Responsibility: Each strategy handles ONE execution mode
- Open/Closed: Add new strategies without modifying existing code
- Liskov Substitution: All strategies are interchangeable
- Interface Segregation: Minimal strategy interface
- Dependency Inversion: Depends on PipelineStage abstraction

Strategies:
1. StandardPipelineStrategy - Sequential execution (default)
2. FastPipelineStrategy - Skip optional stages for quick turnaround
3. ParallelPipelineStrategy - Execute independent stages concurrently
4. CheckpointPipelineStrategy - Resume from failures with checkpoints

Migration Guide:
    OLD:
        from pipeline_strategies import PipelineStrategy, get_strategy

    NEW:
        from workflows.strategies import PipelineStrategy, get_strategy

All functionality is preserved - only import paths change.
"""

# Re-export all public APIs from new package
from workflows.strategies import (
    # Base strategy interface
    PipelineStrategy,

    # Concrete strategy implementations
    StandardPipelineStrategy,
    FastPipelineStrategy,
    ParallelPipelineStrategy,
    CheckpointPipelineStrategy,

    # Execution context management
    ExecutionContextManager,

    # Strategy factory
    get_strategy,
    list_strategies,
    register_strategy,
    unregister_strategy,
    STRATEGY_REGISTRY,
)

__all__ = [
    # Base strategy
    "PipelineStrategy",

    # Concrete strategies
    "StandardPipelineStrategy",
    "FastPipelineStrategy",
    "ParallelPipelineStrategy",
    "CheckpointPipelineStrategy",

    # Context management
    "ExecutionContextManager",

    # Factory functions
    "get_strategy",
    "list_strategies",
    "register_strategy",
    "unregister_strategy",
    "STRATEGY_REGISTRY",
]
