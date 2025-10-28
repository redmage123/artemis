"""
Pipeline Execution Strategies Package.

WHY: Flexible pipeline execution with interchangeable strategies.
RESPONSIBILITY: Provide strategy pattern implementation for pipeline execution.
PATTERNS: Strategy Pattern, Factory Pattern, Memento Pattern (checkpointing).

This package implements the Strategy Pattern for pipeline execution, enabling:
- Sequential execution (StandardPipelineStrategy)
- Fast execution with stage skipping (FastPipelineStrategy)
- Parallel execution for independent stages (ParallelPipelineStrategy)
- Checkpoint-based execution with resume (CheckpointPipelineStrategy)

SOLID Principles:
- Single Responsibility: Each strategy handles ONE execution mode
- Open/Closed: Add new strategies without modifying existing code
- Liskov Substitution: All strategies are interchangeable
- Interface Segregation: Minimal strategy interface
- Dependency Inversion: Depends on PipelineStage abstraction

Dependencies: artemis_stage_interface, pipeline_observer, artemis_constants
"""

# Base strategy interface
from .base_strategy import PipelineStrategy

# Concrete strategy implementations
from .standard_strategy import StandardPipelineStrategy
from .fast_strategy import FastPipelineStrategy
from .parallel_strategy import ParallelPipelineStrategy
from .checkpoint_strategy import CheckpointPipelineStrategy

# Execution context management
from .execution_context import ExecutionContextManager

# Strategy factory
from .strategy_factory import (
    get_strategy,
    list_strategies,
    register_strategy,
    unregister_strategy,
    STRATEGY_REGISTRY
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
