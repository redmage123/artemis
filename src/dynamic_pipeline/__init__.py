#!/usr/bin/env python3
"""
Package: dynamic_pipeline

WHY: Dynamic pipeline system enables runtime-configurable, adaptive pipeline execution
     that adjusts to project complexity, resource constraints, and real-time conditions.

RESPONSIBILITY: Export all dynamic pipeline components for external use.

ARCHITECTURE:
    - Core: DynamicPipeline, DynamicPipelineBuilder, DynamicPipelineFactory
    - State: PipelineState, ProjectComplexity, StageResult
    - Stages: PipelineStage (abstract base)
    - Selection: StageSelectionStrategy, ComplexityBasedSelector, ResourceBasedSelector, ManualSelector
    - Execution: StageExecutor, ParallelStageExecutor
    - Policies: RetryPolicy

USAGE:
    from dynamic_pipeline import (
        DynamicPipeline,
        DynamicPipelineBuilder,
        DynamicPipelineFactory,
        PipelineState,
        ProjectComplexity,
        PipelineStage,
        ComplexityBasedSelector
    )

    # Create adaptive pipeline
    pipeline = (DynamicPipelineBuilder()
        .with_name("my-pipeline")
        .add_stages([stage1, stage2, stage3])
        .with_strategy(ComplexityBasedSelector())
        .with_parallelism(enabled=True, max_workers=4)
        .build())

    # Execute
    results = pipeline.execute(card_id="CARD-123")
"""

# Core pipeline components
from dynamic_pipeline.dynamic_pipeline_core import DynamicPipeline
from dynamic_pipeline.dynamic_pipeline_builder import DynamicPipelineBuilder
from dynamic_pipeline.dynamic_pipeline_factory import DynamicPipelineFactory

# State and configuration
from dynamic_pipeline.pipeline_state import PipelineState
from dynamic_pipeline.project_complexity import ProjectComplexity
from dynamic_pipeline.stage_result import StageResult

# Stage interfaces
from dynamic_pipeline.pipeline_stage import PipelineStage

# Selection strategies
from dynamic_pipeline.stage_selection_strategy import StageSelectionStrategy
from dynamic_pipeline.complexity_based_selector import ComplexityBasedSelector
from dynamic_pipeline.resource_based_selector import ResourceBasedSelector
from dynamic_pipeline.manual_selector import ManualSelector

# Execution components
from dynamic_pipeline.stage_executor import StageExecutor
from dynamic_pipeline.parallel_stage_executor import ParallelStageExecutor

# Policies
from dynamic_pipeline.retry_policy import RetryPolicy


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
