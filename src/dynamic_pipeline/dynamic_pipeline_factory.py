#!/usr/bin/env python3
"""
Module: dynamic_pipeline_factory.py

WHY: Common pipeline configurations should be reusable. Factory provides convenient
     presets for typical use cases without manual builder configuration.

RESPONSIBILITY: Create pre-configured pipeline instances for common scenarios.

PATTERNS:
    - Factory Pattern: Creates complex objects with preset configurations
    - Static Factory Methods: Provides named constructors for clarity
"""

from typing import List, Optional

from pipeline_observer import PipelineObservable
from dynamic_pipeline.pipeline_stage import PipelineStage
from dynamic_pipeline.project_complexity import ProjectComplexity
from dynamic_pipeline.complexity_based_selector import ComplexityBasedSelector
from dynamic_pipeline.dynamic_pipeline_builder import DynamicPipelineBuilder
from dynamic_pipeline.dynamic_pipeline_core import DynamicPipeline


class DynamicPipelineFactory:
    """
    Factory for creating common pipeline configurations.

    Why it exists: Provides convenient preset configurations for common
    use cases without needing to manually configure builder.

    Design pattern: Factory Pattern
    """

    @staticmethod
    def create_simple_pipeline(
        name: str,
        stages: List[PipelineStage],
        observable: Optional[PipelineObservable] = None
    ) -> DynamicPipeline:
        """
        Create simple sequential pipeline.

        Args:
            name: Pipeline name
            stages: Stages to execute
            observable: Optional observable (creates default if None)

        Returns:
            Configured pipeline
        """
        return (DynamicPipelineBuilder()
            .with_name(name)
            .add_stages(stages)
            .with_observable(observable or PipelineObservable())
            .build())

    @staticmethod
    def create_parallel_pipeline(
        name: str,
        stages: List[PipelineStage],
        max_workers: int = 4,
        observable: Optional[PipelineObservable] = None
    ) -> DynamicPipeline:
        """
        Create pipeline with parallel execution.

        Args:
            name: Pipeline name
            stages: Stages to execute
            max_workers: Maximum parallel workers
            observable: Optional observable

        Returns:
            Configured pipeline with parallelism
        """
        return (DynamicPipelineBuilder()
            .with_name(name)
            .add_stages(stages)
            .with_parallelism(enabled=True, max_workers=max_workers)
            .with_observable(observable or PipelineObservable())
            .build())

    @staticmethod
    def create_adaptive_pipeline(
        name: str,
        stages: List[PipelineStage],
        complexity: ProjectComplexity,
        enable_parallel: bool = True,
        observable: Optional[PipelineObservable] = None
    ) -> DynamicPipeline:
        """
        Create adaptive pipeline with complexity-based selection.

        Args:
            name: Pipeline name
            stages: Available stages
            complexity: Project complexity level
            enable_parallel: Enable parallel execution
            observable: Optional observable

        Returns:
            Configured adaptive pipeline
        """
        builder = (DynamicPipelineBuilder()
            .with_name(name)
            .add_stages(stages)
            .with_strategy(ComplexityBasedSelector())
            .with_context({"complexity": complexity})
            .with_observable(observable or PipelineObservable()))

        if enable_parallel:
            builder.with_parallelism(enabled=True, max_workers=4)

        return builder.build()
