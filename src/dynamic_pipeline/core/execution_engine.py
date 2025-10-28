#!/usr/bin/env python3
"""
Module: execution_engine.py

WHY: Handles actual stage execution logic - both sequential and parallel.
     Separates execution mechanics from pipeline orchestration.

RESPONSIBILITY: Execute pipeline stages, handle result caching, update context,
                and determine execution flow (continue vs stop on failure).

PATTERNS:
    - Strategy: Supports different execution modes (sequential/parallel)
    - Guard Clauses: Early returns on cache hits and failures
    - Dependency Injection: Receives executors via constructor
"""

from typing import Dict, List, Optional
from artemis_services import PipelineLogger
from dynamic_pipeline.pipeline_stage import PipelineStage
from dynamic_pipeline.stage_result import StageResult
from dynamic_pipeline.stage_executor import StageExecutor
from dynamic_pipeline.parallel_stage_executor import ParallelStageExecutor
from dynamic_pipeline.core.pipeline_context import PipelineContext


class ExecutionEngine:
    """
    Stage execution engine supporting sequential and parallel execution.

    WHY: Separates execution logic from pipeline orchestration. Handles
         caching, context updates, and failure handling consistently.

    RESPONSIBILITY: Execute stages using provided executors, manage result
                    caching, and update context with results.

    PATTERNS: Strategy pattern for execution mode selection.

    Attributes:
        executor: Sequential stage executor
        parallel_executor: Optional parallel executor
        logger: Pipeline logger
    """

    def __init__(
        self,
        executor: StageExecutor,
        parallel_executor: Optional[ParallelStageExecutor],
        logger: PipelineLogger
    ):
        """
        Initialize execution engine.

        Args:
            executor: Sequential stage executor
            parallel_executor: Optional parallel executor
            logger: Logger for execution events
        """
        self.executor = executor
        self.parallel_executor = parallel_executor
        self.logger = logger

    def execute_stages(
        self,
        stages: List[PipelineStage],
        context: PipelineContext,
        card_id: str,
        use_parallel: bool = False
    ) -> Dict[str, StageResult]:
        """
        Execute stages using appropriate execution mode.

        WHY: Single entry point for stage execution, delegates to sequential
             or parallel based on configuration.

        Args:
            stages: Stages to execute
            context: Pipeline context
            card_id: Card ID for tracking
            use_parallel: Whether to use parallel execution

        Returns:
            Dictionary mapping stage name to result
        """
        # Guard clause: No parallel executor available
        if use_parallel and not self.parallel_executor:
            self.logger.log(
                "Parallel execution requested but no parallel executor available, "
                "falling back to sequential",
                "WARNING"
            )
            use_parallel = False

        # Dispatch to appropriate executor
        if use_parallel:
            return self.parallel_executor.execute_stages_parallel(
                stages,
                context.context,
                card_id
            )

        return self._execute_sequential(stages, context, card_id)

    def _execute_sequential(
        self,
        stages: List[PipelineStage],
        context: PipelineContext,
        card_id: str
    ) -> Dict[str, StageResult]:
        """
        Execute stages sequentially with caching and early stopping.

        WHY: Sequential execution ensures stage dependencies are respected.
             Caching avoids re-executing expensive stages. Early stopping
             prevents wasted computation after failures.

        Args:
            stages: Stages to execute
            context: Pipeline context
            card_id: Card ID for tracking

        Returns:
            Dictionary of stage results
        """
        results = {}

        for stage in stages:
            # Check cache first (performance optimization)
            cached_result = context.get_cached_result(stage.name)
            if cached_result:
                self.logger.log(
                    f"Using cached result for {stage.name}",
                    "DEBUG"
                )
                results[stage.name] = cached_result
                continue

            # Execute stage
            result = self.executor.execute_stage(
                stage,
                context.context,
                card_id
            )
            results[stage.name] = result

            # Cache successful results
            if result.is_success():
                context.cache_result(stage.name, result)
                context.update_from_result(stage.name, result)

            # Guard clause: Stage failed - stop execution
            if not result.is_success():
                self.logger.log(
                    f"Stage {stage.name} failed, stopping pipeline",
                    "ERROR"
                )
                break

        return results

    def has_parallel_support(self) -> bool:
        """
        Check if parallel execution is supported.

        Returns:
            True if parallel executor available
        """
        return self.parallel_executor is not None
