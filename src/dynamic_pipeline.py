#!/usr/bin/env python3
"""
Module: dynamic_pipeline.py (Backward Compatibility Wrapper)

WHY: Maintains backward compatibility for existing imports while enabling modular architecture.
     All implementations moved to dynamic_pipeline/ package for better organization.

RESPONSIBILITY: Re-export all public APIs from modularized package.

MIGRATION PATH:
    Old: from dynamic_pipeline import DynamicPipeline, PipelineState
    New: from dynamic_pipeline import DynamicPipeline, PipelineState  (same!)
    Or:  from dynamic_pipeline.dynamic_pipeline_core import DynamicPipeline

DEPRECATION: This wrapper will remain indefinitely for backward compatibility.
             New code should import from dynamic_pipeline package directly.
"""

# Re-export all public APIs from modularized package
from dynamic_pipeline import (
    # Core pipeline components
    DynamicPipeline,
    DynamicPipelineBuilder,
    DynamicPipelineFactory,

    # State and configuration
    PipelineState,
    ProjectComplexity,
    StageResult,

    # Stage interfaces
    PipelineStage,

    # Selection strategies
    StageSelectionStrategy,
    ComplexityBasedSelector,
    ResourceBasedSelector,
    ManualSelector,

    # Execution components
    StageExecutor,
    ParallelStageExecutor,

    # Policies
    RetryPolicy,
)

__all__ = [
    # Core
    'DynamicPipeline',
    'DynamicPipelineBuilder',
    'DynamicPipelineFactory',

    # State
    'PipelineState',
    'ProjectComplexity',
    'StageResult',

    # Stages
    'PipelineStage',

    # Selection
    'StageSelectionStrategy',
    'ComplexityBasedSelector',
    'ResourceBasedSelector',
    'ManualSelector',

    # Execution
    'StageExecutor',
    'ParallelStageExecutor',

    # Policies
    'RetryPolicy',
]
