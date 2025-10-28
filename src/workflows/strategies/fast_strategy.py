#!/usr/bin/env python3
"""
Fast Pipeline Execution Strategy.

WHY: Rapid execution by skipping optional stages.
RESPONSIBILITY: Execute pipeline with configurable stage skipping.
PATTERNS: Strategy Pattern, Template Method Pattern.

Dependencies: base_strategy, execution_context, artemis_constants
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

from artemis_stage_interface import PipelineStage
from artemis_constants import STAGE_ARCHITECTURE, STAGE_VALIDATION
from pipeline_observer import PipelineObservable

from .base_strategy import PipelineStrategy
from .execution_context import ExecutionContextManager


class FastPipelineStrategy(PipelineStrategy):
    """
    Fast execution strategy - skip optional stages.

    WHY: Reduce execution time for quick prototypes and testing.
    RESPONSIBILITY: Filter and execute only essential stages.
    PATTERNS: Strategy Pattern - optimized execution variant.

    Skipped Stages (by default):
    - Architecture (can be regenerated later)
    - Validation (tests run in development)

    Use Cases:
    - Quick prototypes
    - Development testing
    - Low-priority tasks
    """

    def __init__(
        self,
        skip_stages: Optional[List[str]] = None,
        verbose: bool = True,
        observable: Optional[PipelineObservable] = None
    ):
        """
        Initialize fast strategy.

        Args:
            skip_stages: List of stage names to skip (default: architecture, validation)
            verbose: Enable verbose logging
            observable: Optional PipelineObservable for event broadcasting
        """
        super().__init__(verbose, observable)
        self.skip_stages = skip_stages or [STAGE_ARCHITECTURE, STAGE_VALIDATION]
        self.context_manager = ExecutionContextManager()

    def execute(self, stages: List[PipelineStage], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute pipeline with optional stages skipped.

        WHY: Optimize execution time by running only essential stages.
        RESPONSIBILITY: Filter stages and execute remaining ones.

        Args:
            stages: List of pipeline stages to execute
            context: Execution context (card info, config, etc.)

        Returns:
            Execution result dict with status, results, duration
        """
        start_time = datetime.now()

        # Filter out skipped stages
        active_stages = self._filter_active_stages(stages)
        skipped_count = len(stages) - len(active_stages)

        self._log_execution_start(len(active_stages), skipped_count)

        results = {}

        for i, stage in enumerate(active_stages, 1):
            stage_name = stage.__class__.__name__
            card_id = self.context_manager.get_card_id(context)

            self._log(f"▶️  Stage {i}/{len(active_stages)}: {stage_name}", "STAGE")

            # Notify stage started
            self._notify_stage_started(card_id, stage_name, stage_number=i, total_stages=len(active_stages))

            # Execute stage
            stage_result = self._execute_stage(stage, context, stage_name)

            # Guard: Check for execution failure
            if stage_result is None:
                return self._build_exception_result(i, stage_name, "Stage execution returned None", results, skipped_count, start_time)

            # Store result
            results[stage_name] = stage_result

            # Update context with stage result
            self.context_manager.update_context_from_result(context, stage_result)

            # Check if stage succeeded
            if not self.context_manager.is_stage_successful(stage_result):
                return self._handle_stage_failure(i, stage_name, stage_result, card_id, results, skipped_count, start_time)

            # Stage succeeded
            self._handle_stage_success(stage_name, card_id, stage_result)

        # All stages completed successfully
        return self._build_success_result(len(active_stages), results, skipped_count, start_time)

    def _filter_active_stages(self, stages: List[PipelineStage]) -> List[PipelineStage]:
        """
        Filter out skipped stages.

        WHY: Apply skip list to stage pipeline.
        RESPONSIBILITY: Remove optional stages from execution.

        Args:
            stages: Full list of pipeline stages

        Returns:
            Filtered list of active stages
        """
        return [
            stage for stage in stages
            if self._get_stage_name(stage) not in self.skip_stages
        ]

    def _get_stage_name(self, stage: PipelineStage) -> str:
        """
        Get normalized stage name for comparison.

        WHY: Consistent stage name extraction.
        RESPONSIBILITY: Extract stage name from various sources.

        Args:
            stage: Pipeline stage

        Returns:
            Normalized lowercase stage name
        """
        # Try to get name from stage, fallback to class name
        if hasattr(stage, 'name'):
            return stage.name.lower()
        return stage.__class__.__name__.replace('Stage', '').lower()

    def _log_execution_start(self, active_count: int, skipped_count: int):
        """
        Log fast execution start information.

        WHY: Clear visibility into stage filtering.
        RESPONSIBILITY: Log execution summary.

        Args:
            active_count: Number of active stages
            skipped_count: Number of skipped stages
        """
        self._log("⚡ Starting FAST pipeline execution")
        self._log(f"   Running: {active_count} stages")
        self._log(f"   Skipping: {skipped_count} stages ({', '.join(self.skip_stages)})")

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

    def _handle_stage_failure(
        self,
        stage_index: int,
        stage_name: str,
        stage_result: Dict[str, Any],
        card_id: str,
        results: Dict[str, Any],
        skipped_count: int,
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
            skipped_count: Number of skipped stages
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
            strategy="fast",
            stages_skipped=skipped_count
        )

    def _handle_stage_success(
        self,
        stage_name: str,
        card_id: str,
        stage_result: Dict[str, Any]
    ):
        """
        Handle stage success.

        WHY: Centralize success handling logic.
        RESPONSIBILITY: Log and notify.

        Args:
            stage_name: Name of successful stage
            card_id: Card ID for notifications
            stage_result: Stage execution result
        """
        self._log(f"✅ Stage COMPLETE: {stage_name}", "SUCCESS")

        # Notify stage completed
        self._notify_stage_completed(card_id, stage_name, stage_result=stage_result)

    def _build_exception_result(
        self,
        stage_index: int,
        stage_name: str,
        error: str,
        results: Dict[str, Any],
        skipped_count: int,
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
            skipped_count: Number of skipped stages
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
            strategy="fast",
            stages_skipped=skipped_count
        )

    def _build_success_result(
        self,
        total_stages: int,
        results: Dict[str, Any],
        skipped_count: int,
        start_time: datetime
    ) -> Dict[str, Any]:
        """
        Build result for successful pipeline completion.

        WHY: Consistent success result structure.
        RESPONSIBILITY: Create success result dict.

        Args:
            total_stages: Total number of stages executed
            results: All stage results
            skipped_count: Number of skipped stages
            start_time: Execution start time

        Returns:
            Success result dict
        """
        duration = (datetime.now() - start_time).total_seconds()

        self._log(f"⚡ FAST pipeline COMPLETE! ({duration:.1f}s, skipped {skipped_count} stages)", "SUCCESS")

        return self.context_manager.build_success_result(
            stages_completed=total_stages,
            results=results,
            duration=duration,
            strategy="fast",
            stages_skipped=skipped_count
        )
