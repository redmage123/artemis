#!/usr/bin/env python3
"""
Standard Sequential Pipeline Execution Strategy.

WHY: Default sequential execution with checkpoint support.
RESPONSIBILITY: Execute stages sequentially with failure handling.
PATTERNS: Strategy Pattern, Template Method Pattern.

Dependencies: base_strategy, execution_context, datetime
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from artemis_stage_interface import PipelineStage
from pipeline_observer import PipelineObservable

from .base_strategy import PipelineStrategy
from .execution_context import ExecutionContextManager


class StandardPipelineStrategy(PipelineStrategy):
    """
    Standard sequential execution strategy.

    WHY: Default pipeline execution with predictable, sequential behavior.
    RESPONSIBILITY: Execute all stages in order, stop at first failure.
    PATTERNS: Strategy Pattern - concrete strategy implementation.

    Execution Flow:
    1. Project Analysis
    2. Architecture
    3. Dependencies
    4. Development
    5. Code Review
    6. Validation
    7. Integration
    8. Testing
    """

    def __init__(self, verbose: bool = True, observable: Optional[PipelineObservable] = None, adaptive_config: Optional[Any] = None, summary_mode: bool = True):
        """
        Initialize standard strategy.

        Args:
            verbose: Enable verbose logging
            observable: Optional PipelineObservable for event broadcasting
            adaptive_config: Optional adaptive configuration for resource optimization
            summary_mode: Use summary display for cleaner output (default: True)
        """
        super().__init__(verbose, observable)
        self.context_manager = ExecutionContextManager()
        self.adaptive_config = adaptive_config
        self.summary_mode = summary_mode
        self.summary_display = None  # Will be initialized when logger is available

    def execute(self, stages: List[PipelineStage], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute all stages sequentially.

        WHY: Simple, predictable execution with clear failure points.
        RESPONSIBILITY: Run stages in order, handle failures, save checkpoints.

        Args:
            stages: List of pipeline stages to execute
            context: Execution context (card info, config, etc.)

        Returns:
            Execution result dict with status, results, duration
        """
        start_time = datetime.now()

        # Inject adaptive config into context if available
        if self.adaptive_config:
            context['adaptive_config'] = self.adaptive_config

            # Log based on verbosity mode
            if self.verbose:
                # Verbose mode: Show all details
                self._log(f"🔧 Using adaptive config: {self.adaptive_config.profile} profile")
                self._log(f"   Parallel devs: {self.adaptive_config.max_parallel_developers}")
                self._log(f"   Validation: {self.adaptive_config.validation_level}")
                self._log(f"   Code review: {self.adaptive_config.code_review_depth}")
            elif self.summary_mode:
                # Summary mode: Show key decisions only
                self._log(f"🔧 Using {self.adaptive_config.profile.upper()} profile")

        if self.summary_mode and not self.verbose:
            self._log(f"\n▶️  Starting pipeline ({len(stages)} stages)")
        else:
            self._log(f"🎯 Starting STANDARD pipeline execution ({len(stages)} stages)")

        results = {}

        for i, stage in enumerate(stages, 1):
            stage_name = stage.__class__.__name__
            card_id = self.context_manager.get_card_id(context)

            if self.summary_mode and not self.verbose:
                self._log(f"▶️  Stage {i}/{len(stages)}: {stage_name}")
            else:
                self._log(f"▶️  Stage {i}/{len(stages)}: {stage_name}", "STAGE")

            # Notify stage started
            self._notify_stage_started(card_id, stage_name, stage_number=i, total_stages=len(stages))

            # Execute stage
            stage_result = self._execute_stage(stage, context, stage_name)

            # Guard: Check for execution failure
            if stage_result is None:
                return self._build_exception_result(i, stage_name, "Stage execution returned None", results, start_time)

            # Store result
            results[stage_name] = stage_result

            # Update context with stage result
            self.context_manager.update_context_from_result(context, stage_result)

            # POST-SPRINT-PLANNING HOOK
            self._handle_sprint_planning_hook(stage_name, stage_result, context)

            # Check if stage succeeded
            if not self.context_manager.is_stage_successful(stage_result):
                return self._handle_stage_failure(i, stage_name, stage_result, card_id, results, start_time)

            # Stage succeeded
            self._handle_stage_success(i, stage_name, stage_result, card_id, context, start_time)

        # All stages completed successfully
        return self._build_success_result(len(stages), results, start_time)

    def _execute_stage(
        self,
        stage: PipelineStage,
        context: Dict[str, Any],
        stage_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Execute a single stage with exception handling.

        WHY: Isolate stage execution logic.
        RESPONSIBILITY: Run stage and catch exceptions.

        Args:
            stage: Pipeline stage to execute
            context: Execution context
            stage_name: Stage name for logging

        Returns:
            Stage result dict or None on exception
        """
        try:
            card = self.context_manager.get_card(context)
            return stage.execute(card, context)
        except Exception as e:
            self._log(f"❌ Stage EXCEPTION: {stage_name} - {e}", "ERROR")
            return None

    def _handle_sprint_planning_hook(
        self,
        stage_name: str,
        stage_result: Dict[str, Any],
        context: Dict[str, Any]
    ):
        """
        Handle post-sprint-planning complexity recalculation.

        WHY: Fix bug where AI guesses complexity without seeing sprint results.
        RESPONSIBILITY: Trigger complexity recalculation after sprint planning.

        Args:
            stage_name: Name of completed stage
            stage_result: Stage execution result
            context: Pipeline execution context
        """
        if stage_name != "SprintPlanningStage":
            return

        if "total_story_points" not in stage_result:
            return

        card = self.context_manager.get_card(context)
        if not card:
            return

        self._recalculate_complexity_after_sprint_planning(card, stage_result, context)

    def _handle_stage_failure(
        self,
        stage_index: int,
        stage_name: str,
        stage_result: Dict[str, Any],
        card_id: str,
        results: Dict[str, Any],
        start_time: datetime
    ) -> Dict[str, Any]:
        """
        Handle stage failure.

        WHY: Centralize failure handling logic.
        RESPONSIBILITY: Log, notify, and return failure result.

        Args:
            stage_index: Current stage index (1-based)
            stage_name: Name of failed stage
            stage_result: Stage execution result
            card_id: Card ID for notifications
            results: Accumulated results
            start_time: Execution start time

        Returns:
            Failure result dict
        """
        self._log(f"❌ Stage FAILED: {stage_name}", "ERROR")

        # Notify stage failed
        error = Exception(stage_result.get("error", "Unknown error"))
        self._notify_stage_failed(card_id, stage_name, error, stage_result=stage_result)

        return self.context_manager.build_failure_result(
            stages_completed=stage_index - 1,
            failed_stage=stage_name,
            error=stage_result.get("error", "Unknown error"),
            results=results,
            duration=(datetime.now() - start_time).total_seconds(),
            strategy="standard"
        )

    def _handle_stage_success(
        self,
        stage_index: int,
        stage_name: str,
        stage_result: Dict[str, Any],
        card_id: str,
        context: Dict[str, Any],
        start_time: datetime
    ):
        """
        Handle stage success.

        WHY: Centralize success handling logic.
        RESPONSIBILITY: Log, notify, and save checkpoint.

        Args:
            stage_index: Current stage index (1-based)
            stage_name: Name of successful stage
            stage_result: Stage execution result
            card_id: Card ID for notifications
            context: Execution context
            start_time: Execution start time
        """
        if self.summary_mode and not self.verbose:
            self._log(f"   ✅ Complete")
        else:
            self._log(f"✅ Stage COMPLETE: {stage_name}", "SUCCESS")

        # Notify stage completed
        self._notify_stage_completed(card_id, stage_name, stage_result=stage_result)

        # Save checkpoint (estimate start time as 5 seconds ago)
        stage_start = datetime.now() - timedelta(seconds=5)
        self.context_manager.save_checkpoint(context, stage_name, stage_result, stage_start)

    def _build_exception_result(
        self,
        stage_index: int,
        stage_name: str,
        error: str,
        results: Dict[str, Any],
        start_time: datetime
    ) -> Dict[str, Any]:
        """
        Build result for stage exception.

        WHY: Consistent exception result structure.
        RESPONSIBILITY: Create exception result dict.

        Args:
            stage_index: Current stage index (1-based)
            stage_name: Name of failed stage
            error: Error message
            results: Accumulated results
            start_time: Execution start time

        Returns:
            Failure result dict
        """
        return self.context_manager.build_failure_result(
            stages_completed=stage_index - 1,
            failed_stage=stage_name,
            error=error,
            results=results,
            duration=(datetime.now() - start_time).total_seconds(),
            strategy="standard"
        )

    def _build_success_result(
        self,
        total_stages: int,
        results: Dict[str, Any],
        start_time: datetime
    ) -> Dict[str, Any]:
        """
        Build result for successful pipeline completion.

        WHY: Consistent success result structure.
        RESPONSIBILITY: Create success result dict.

        Args:
            total_stages: Total number of stages executed
            results: All stage results
            start_time: Execution start time

        Returns:
            Success result dict
        """
        duration = (datetime.now() - start_time).total_seconds()

        if self.summary_mode and not self.verbose:
            self._log(f"\n✅ Pipeline complete ({duration/60:.1f} minutes)")
        else:
            self._log(f"🎉 Pipeline COMPLETE! ({duration:.1f}s)", "SUCCESS")

        return self.context_manager.build_success_result(
            stages_completed=total_stages,
            results=results,
            duration=duration,
            strategy="standard"
        )
