#!/usr/bin/env python3
"""
Module: pipeline_facade.py

WHY: Facade orchestrates all pipeline components - execution engine, lifecycle
     manager, AI optimizer, and context. Provides simple interface to complex
     subsystem.

RESPONSIBILITY: Coordinate pipeline components, provide public API, apply stage
                selection strategy, and expose runtime modification methods.

PATTERNS:
    - Facade: Simplifies interaction with complex subsystems
    - Dependency Injection: Receives all dependencies via constructor
    - Guard Clauses: Validates preconditions before operations
"""

from typing import Dict, Any, List, Optional
from artemis_exceptions import PipelineException, wrap_exception
from artemis_services import PipelineLogger
from pipeline_observer import PipelineObservable
from dynamic_pipeline.pipeline_state import PipelineState
from dynamic_pipeline.pipeline_stage import PipelineStage
from dynamic_pipeline.stage_result import StageResult
from dynamic_pipeline.stage_selection_strategy import StageSelectionStrategy
from dynamic_pipeline.stage_executor import StageExecutor
from dynamic_pipeline.parallel_stage_executor import ParallelStageExecutor
from dynamic_pipeline.core.pipeline_context import PipelineContext
from dynamic_pipeline.core.execution_engine import ExecutionEngine
from dynamic_pipeline.core.lifecycle_manager import LifecycleManager
from dynamic_pipeline.core.ai_optimizer import AIOptimizer


class DynamicPipeline:
    """
    Dynamic pipeline facade with runtime adaptability.

    WHY: Provides simple interface to complex pipeline execution subsystem.
         Coordinates execution engine, lifecycle management, AI optimization,
         and context management.

    RESPONSIBILITY: Orchestrate pipeline components, apply selection strategy,
                    execute stages, and provide runtime modification API.

    PATTERNS: Facade pattern simplifying subsystem interaction.

    Thread safety: Not thread-safe (assumes single-threaded orchestrator)

    Attributes:
        name: Pipeline name
        available_stages: All available stages
        selected_stages: Stages selected by strategy
        strategy: Optional stage selection strategy
        context: Pipeline execution context
        execution_engine: Stage execution engine
        lifecycle_manager: State and lifecycle management
        ai_optimizer: AI-enhanced optimization
        logger: Pipeline logger
    """

    def __init__(
        self,
        name: str,
        stages: List[PipelineStage],
        strategy: Optional[StageSelectionStrategy],
        executor: StageExecutor,
        parallel_executor: Optional[ParallelStageExecutor],
        observable: PipelineObservable,
        initial_context: Dict[str, Any],
        logger: PipelineLogger
    ):
        """
        Initialize dynamic pipeline.

        WHY: Sets up all subsystems and coordinates initialization.

        Args:
            name: Pipeline name
            stages: Available stages
            strategy: Optional stage selection strategy
            executor: Sequential stage executor
            parallel_executor: Optional parallel executor
            observable: Event notification system
            initial_context: Initial execution context
            logger: Pipeline logger
        """
        self.name = name
        self.available_stages = stages
        self.strategy = strategy
        self.logger = logger

        # Initialize subsystems
        self.context = PipelineContext(initial_context)
        self.execution_engine = ExecutionEngine(
            executor,
            parallel_executor,
            logger
        )
        self.lifecycle_manager = LifecycleManager(
            name,
            observable,
            logger
        )
        self.ai_optimizer = AIOptimizer(self.context)

        # Select stages and transition to ready
        self.selected_stages = self._select_stages()
        self.lifecycle_manager.transition_to_ready(len(self.selected_stages))

        # Results storage
        self.results: Dict[str, StageResult] = {}

    def _select_stages(self) -> List[PipelineStage]:
        """
        Select stages using strategy.

        WHY: Extracts stage selection logic, applies strategy if configured.

        Returns:
            List of selected stages
        """
        # Guard clause: No strategy - use all stages
        if not self.strategy:
            return self.available_stages

        return self.strategy.select_stages(
            self.available_stages,
            self.context.context
        )

    @wrap_exception(PipelineException, "Failed to execute pipeline")
    def execute(self, card_id: str) -> Dict[str, StageResult]:
        """
        Execute pipeline for given card.

        WHY: Main pipeline execution entry point. Orchestrates lifecycle
             transitions, stage execution, and result handling.

        Args:
            card_id: Card ID for tracking and events

        Returns:
            Dictionary mapping stage name to StageResult

        Raises:
            PipelineException: If pipeline not ready or execution fails
        """
        # Start execution (validates state)
        self.lifecycle_manager.start_execution(card_id)

        # Update context with card ID
        self.context.set("card_id", card_id)

        try:
            # Execute stages
            self.results = self.execution_engine.execute_stages(
                self.selected_stages,
                self.context,
                card_id,
                use_parallel=self.execution_engine.has_parallel_support()
            )

            # Check for failures
            failures = [r for r in self.results.values() if not r.is_success()]

            # Handle outcome using dispatch
            outcome_handlers = {
                True: self._handle_success,
                False: self._handle_failure
            }

            handler = outcome_handlers[len(failures) == 0]
            handler(failures)

            return self.results

        except Exception as e:
            # Handle unexpected error
            self.lifecycle_manager.mark_error(e)
            raise

    def _handle_success(self, failures: List[StageResult]) -> None:
        """
        Handle successful pipeline completion.

        Args:
            failures: Empty list (unused, for consistent signature)
        """
        self.lifecycle_manager.mark_completed(len(self.results))

    def _handle_failure(self, failures: List[StageResult]) -> None:
        """
        Handle pipeline failure.

        Args:
            failures: List of failed stage results
        """
        self.lifecycle_manager.mark_failed(failures)

    @wrap_exception(PipelineException, "Failed to pause pipeline")
    def pause(self) -> None:
        """
        Pause pipeline execution.

        WHY: Enables supervisor to pause long-running pipelines.

        Raises:
            PipelineException: If pipeline not running
        """
        self.lifecycle_manager.pause()

    @wrap_exception(PipelineException, "Failed to resume pipeline")
    def resume(self) -> None:
        """
        Resume paused pipeline.

        Raises:
            PipelineException: If pipeline not paused
        """
        self.lifecycle_manager.resume()

    @wrap_exception(PipelineException, "Failed to add stage at runtime")
    def add_stage_runtime(self, stage: PipelineStage) -> None:
        """
        Add stage to pipeline at runtime.

        WHY: Enables dynamic pipeline modification based on intermediate
             results or supervisor commands.

        Args:
            stage: Stage to add

        Raises:
            PipelineException: If pipeline is running
        """
        # Validate can modify
        self.lifecycle_manager.validate_stage_modification(
            f"add stage {stage.name}"
        )

        self.available_stages.append(stage)
        self.selected_stages.append(stage)

        self.logger.log(f"Added stage at runtime: {stage.name}", "INFO")

    @wrap_exception(PipelineException, "Failed to remove stage at runtime")
    def remove_stage_runtime(self, stage_name: str) -> None:
        """
        Remove stage from pipeline at runtime.

        WHY: Enables skipping stages based on conditions or supervisor override.

        Args:
            stage_name: Name of stage to remove

        Raises:
            PipelineException: If pipeline is running
        """
        # Validate can modify
        self.lifecycle_manager.validate_stage_modification(
            f"remove stage {stage_name}"
        )

        self.selected_stages = [
            s for s in self.selected_stages
            if s.name != stage_name
        ]

        self.logger.log(f"Removed stage at runtime: {stage_name}", "INFO")

    def get_state(self) -> PipelineState:
        """
        Get current pipeline state.

        Returns:
            Current state
        """
        return self.lifecycle_manager.get_state()

    def get_results(self) -> Dict[str, StageResult]:
        """
        Get all stage results.

        Returns:
            Copy of results dictionary
        """
        return self.results.copy()

    def get_context(self) -> Dict[str, Any]:
        """
        Get current execution context.

        Returns:
            Copy of context dictionary
        """
        return self.context.copy()

    def clear_cache(self) -> None:
        """Clear result cache."""
        self.context.clear_cache()
        self.logger.log("Result cache cleared", "DEBUG")

    # ========================================================================
    # AI OPTIMIZATION METHODS (Delegate to AIOptimizer)
    # ========================================================================

    @wrap_exception(PipelineException, "AI-enhanced stage optimization failed")
    def optimize_stage_execution_with_ai(
        self,
        stages: List[PipelineStage],
        context: Dict[str, Any],
        use_initial_analysis: bool = True
    ) -> Dict[str, Any]:
        """
        Optimize stage execution using hybrid AI approach.

        WHY: Demonstrates hybrid pattern:
        1. Start with router's pre-computed intensity (free!)
        2. Make adaptive AI call if needed (via optimizer)
        3. Return optimized execution plan

        Args:
            stages: Stages to optimize
            context: Execution context (unused, for compatibility)
            use_initial_analysis: If True, uses router's pre-computed analysis

        Returns:
            Dictionary with optimized execution plan
        """
        return self.ai_optimizer.optimize_stage_execution(
            stages,
            use_initial_analysis
        )

    @wrap_exception(PipelineException, "AI-enhanced parallelization assessment failed")
    def assess_parallelization_with_ai(
        self,
        stages: List[PipelineStage],
        context: Dict[str, Any],
        use_initial_analysis: bool = True
    ) -> Dict[str, Any]:
        """
        Assess parallelization strategy using hybrid AI approach.

        WHY: Determines safe parallelization based on dependencies.

        Args:
            stages: Stages to assess
            context: Execution context (unused, for compatibility)
            use_initial_analysis: If True, uses router's suggested workers

        Returns:
            Dictionary with parallelization assessment
        """
        return self.ai_optimizer.assess_parallelization(
            stages,
            use_initial_analysis
        )
