#!/usr/bin/env python3
"""
Module: dynamic_pipeline_builder.py

WHY: Pipeline construction involves many configuration options (stages, strategies,
     retry policies, parallelism). Builder pattern provides clear fluent API.

RESPONSIBILITY: Build and validate dynamic pipeline configurations with fluent interface.

PATTERNS:
    - Builder Pattern: Fluent API for step-by-step pipeline construction
    - Validation: Ensures configuration completeness before building
    - Guard Clauses: Early validation to prevent invalid configurations
"""

from typing import Dict, Any, List, Optional

from artemis_exceptions import PipelineException, wrap_exception
from artemis_services import PipelineLogger
from pipeline_observer import PipelineObservable
from dynamic_pipeline.pipeline_stage import PipelineStage
from dynamic_pipeline.stage_selection_strategy import StageSelectionStrategy
from dynamic_pipeline.retry_policy import RetryPolicy
from dynamic_pipeline.stage_executor import StageExecutor
from dynamic_pipeline.parallel_stage_executor import ParallelStageExecutor


class DynamicPipelineBuilder:
    """
    Builder for constructing dynamic pipelines with fluent API.

    Why it exists: Pipeline construction involves many configuration options.
    Builder pattern provides clear, fluent API and validates configuration
    before creating pipeline.

    Design pattern: Builder Pattern

    Responsibilities:
    - Collect pipeline configuration (stages, strategies, policies)
    - Validate configuration (no duplicates, dependencies exist)
    - Create configured DynamicPipeline instance
    - Provide fluent interface for ergonomic construction

    Usage example:
        pipeline = (DynamicPipelineBuilder()
            .with_name("feature-123")
            .with_strategy(ComplexityBasedSelector())
            .add_stages([stage1, stage2, stage3])
            .with_retry_policy(RetryPolicy(max_retries=5))
            .with_parallelism(enabled=True, max_workers=4)
            .build())
    """

    def __init__(self):
        self._name: Optional[str] = None
        self._stages: List[PipelineStage] = []
        self._strategy: Optional[StageSelectionStrategy] = None
        self._retry_policy: RetryPolicy = RetryPolicy()
        self._observable: PipelineObservable = PipelineObservable(verbose=True)
        self._parallel_enabled: bool = False
        self._max_workers: int = 4
        self._context: Dict[str, Any] = {}
        self.logger = PipelineLogger(verbose=True)

    def with_name(self, name: str) -> 'DynamicPipelineBuilder':
        """
        Set pipeline name.

        Why needed: Name used for logging, metrics, and identification.

        Args:
            name: Pipeline name (usually card ID or feature name)

        Returns:
            Self for method chaining
        """
        self._name = name
        return self

    def add_stage(self, stage: PipelineStage) -> 'DynamicPipelineBuilder':
        """
        Add single stage to pipeline.

        Args:
            stage: Stage to add

        Returns:
            Self for method chaining
        """
        self._stages.append(stage)
        return self

    def add_stages(self, stages: List[PipelineStage]) -> 'DynamicPipelineBuilder':
        """
        Add multiple stages to pipeline.

        Args:
            stages: Stages to add

        Returns:
            Self for method chaining
        """
        self._stages.extend(stages)
        return self

    def with_strategy(self, strategy: StageSelectionStrategy) -> 'DynamicPipelineBuilder':
        """
        Set stage selection strategy.

        Args:
            strategy: Selection strategy (complexity, resource, manual)

        Returns:
            Self for method chaining
        """
        self._strategy = strategy
        return self

    def with_retry_policy(self, policy: RetryPolicy) -> 'DynamicPipelineBuilder':
        """
        Set retry policy for stage failures.

        Args:
            policy: Retry policy configuration

        Returns:
            Self for method chaining
        """
        self._retry_policy = policy
        return self

    def with_observable(self, observable: PipelineObservable) -> 'DynamicPipelineBuilder':
        """
        Set pipeline observable for event broadcasting.

        Args:
            observable: Observable with attached observers

        Returns:
            Self for method chaining
        """
        self._observable = observable
        return self

    def with_parallelism(
        self,
        enabled: bool,
        max_workers: int = 4
    ) -> 'DynamicPipelineBuilder':
        """
        Configure parallel stage execution.

        Args:
            enabled: Enable parallel execution
            max_workers: Maximum parallel workers

        Returns:
            Self for method chaining
        """
        self._parallel_enabled = enabled
        self._max_workers = max_workers
        return self

    def with_context(self, context: Dict[str, Any]) -> 'DynamicPipelineBuilder':
        """
        Set initial pipeline context.

        Args:
            context: Initial context data (complexity, resources, config)

        Returns:
            Self for method chaining
        """
        self._context = context
        return self

    @wrap_exception(PipelineException, "Failed to build dynamic pipeline")
    def build(self) -> 'DynamicPipeline':
        """
        Build and validate pipeline.

        Why needed: Final validation before creating pipeline. Ensures
        all required configuration present and valid.

        Returns:
            Configured DynamicPipeline instance

        Raises:
            PipelineException: If configuration invalid
        """
        # Import here to avoid circular dependency
        from dynamic_pipeline.dynamic_pipeline_core import DynamicPipeline

        # Validate configuration using helper method
        self._validate()

        # Create executor
        executor = StageExecutor(
            observable=self._observable,
            retry_policy=self._retry_policy,
            logger=self.logger
        )

        # Create parallel executor if enabled
        parallel_executor = None
        if self._parallel_enabled:
            parallel_executor = ParallelStageExecutor(
                executor=executor,
                max_workers=self._max_workers,
                logger=self.logger
            )

        # Build pipeline
        pipeline = DynamicPipeline(
            name=self._name or "unnamed-pipeline",
            stages=self._stages,
            strategy=self._strategy,
            executor=executor,
            parallel_executor=parallel_executor,
            observable=self._observable,
            initial_context=self._context,
            logger=self.logger
        )

        self.logger.log(
            f"Built pipeline '{pipeline.name}' with {len(self._stages)} stages",
            "SUCCESS"
        )

        return pipeline

    def _validate(self) -> None:
        """
        Validate builder configuration.

        Why helper method: Extracts validation logic from build(), uses
        guard clauses to avoid nested ifs.

        Raises:
            PipelineException: If configuration invalid
        """
        # Guard clause: No stages
        if not self._stages:
            raise PipelineException(
                "Pipeline must have at least one stage",
                context={"name": self._name}
            )

        # Guard clause: Duplicate stage names
        stage_names = [s.name for s in self._stages]
        duplicates = {name for name in stage_names if stage_names.count(name) > 1}
        if duplicates:
            raise PipelineException(
                "Pipeline has duplicate stage names",
                context={"duplicates": list(duplicates)}
            )

        # Guard clause: Invalid dependencies
        stage_name_set = set(stage_names)
        for stage in self._stages:
            invalid_deps = set(stage.get_dependencies()) - stage_name_set
            if invalid_deps:
                raise PipelineException(
                    f"Stage '{stage.name}' has invalid dependencies",
                    context={"invalid_dependencies": list(invalid_deps)}
                )
