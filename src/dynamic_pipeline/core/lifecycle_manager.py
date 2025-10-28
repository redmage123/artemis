#!/usr/bin/env python3
"""
Module: lifecycle_manager.py

WHY: Manages pipeline lifecycle state transitions (created -> ready -> running
     -> paused/completed/failed) and stage runtime modifications.

RESPONSIBILITY: Enforce valid state transitions, emit lifecycle events, and
                support runtime stage additions/removals.

PATTERNS:
    - State Pattern: Manages pipeline state machine
    - Guard Clauses: Validates state before transitions
    - Observer: Emits events for state changes
"""

from typing import List, Dict, Any, Optional
from artemis_exceptions import PipelineException, wrap_exception
from artemis_services import PipelineLogger
from pipeline_observer import PipelineObservable, PipelineEvent, EventType
from dynamic_pipeline.pipeline_state import PipelineState
from dynamic_pipeline.pipeline_stage import PipelineStage
from dynamic_pipeline.stage_result import StageResult


class LifecycleManager:
    """
    Pipeline lifecycle and state management.

    WHY: Centralizes state transition logic and validation. Ensures pipeline
         follows valid state machine paths. Emits events for monitoring.

    RESPONSIBILITY: Manage state transitions, validate state changes, emit
                    lifecycle events, support runtime modifications.

    PATTERNS: State pattern with guard clauses for validation.

    State transitions:
        CREATED -> READY -> RUNNING -> (PAUSED <-> RUNNING)* -> COMPLETED/FAILED

    Attributes:
        state: Current pipeline state
        observable: Event notification system
        logger: Pipeline logger
        pipeline_name: Name for logging and events
    """

    def __init__(
        self,
        pipeline_name: str,
        observable: PipelineObservable,
        logger: PipelineLogger
    ):
        """
        Initialize lifecycle manager.

        Args:
            pipeline_name: Pipeline name for events
            observable: Event notification system
            logger: Logger for state changes
        """
        self.state = PipelineState.CREATED
        self.observable = observable
        self.logger = logger
        self.pipeline_name = pipeline_name
        self._card_id: Optional[str] = None

    def transition_to_ready(self, stage_count: int) -> None:
        """
        Transition to READY state.

        WHY: Signals pipeline is configured and ready for execution.

        Args:
            stage_count: Number of selected stages
        """
        self.state = PipelineState.READY
        self.logger.log(
            f"Pipeline '{self.pipeline_name}' ready with {stage_count} selected stages",
            "INFO"
        )

    @wrap_exception(PipelineException, "Failed to start pipeline execution")
    def start_execution(self, card_id: str) -> None:
        """
        Start pipeline execution.

        WHY: Validates pipeline is ready before execution begins.

        Args:
            card_id: Card ID for tracking

        Raises:
            PipelineException: If pipeline not in READY state
        """
        # Guard clause: Validate state
        if self.state != PipelineState.READY:
            raise PipelineException(
                f"Pipeline not ready for execution (state: {self.state})",
                context={"pipeline": self.pipeline_name, "card_id": card_id}
            )

        self.state = PipelineState.RUNNING
        self._card_id = card_id

        # Emit start event
        self.observable.notify(PipelineEvent(
            event_type=EventType.PIPELINE_STARTED,
            card_id=card_id,
            data={"pipeline": self.pipeline_name}
        ))

    def mark_completed(self, stage_count: int) -> None:
        """
        Mark pipeline as completed.

        Args:
            stage_count: Number of completed stages
        """
        self.state = PipelineState.COMPLETED

        self.logger.log(
            f"Pipeline '{self.pipeline_name}' completed successfully",
            "SUCCESS"
        )

        self.observable.notify(PipelineEvent(
            event_type=EventType.PIPELINE_COMPLETED,
            card_id=self._card_id,
            data={
                "pipeline": self.pipeline_name,
                "stage_count": stage_count
            }
        ))

    def mark_failed(self, failures: List[StageResult]) -> None:
        """
        Mark pipeline as failed.

        Args:
            failures: List of failed stage results
        """
        self.state = PipelineState.FAILED

        failure_info = [
            f"{r.stage_name}: {r.error}"
            for r in failures
        ]

        self.logger.log(
            f"Pipeline '{self.pipeline_name}' failed: {failure_info}",
            "ERROR"
        )

        self.observable.notify(PipelineEvent(
            event_type=EventType.PIPELINE_FAILED,
            card_id=self._card_id,
            data={
                "pipeline": self.pipeline_name,
                "failures": failure_info
            }
        ))

    def mark_error(self, error: Exception) -> None:
        """
        Mark pipeline as failed due to unexpected error.

        Args:
            error: Exception that caused failure
        """
        self.state = PipelineState.FAILED

        self.logger.log(
            f"Pipeline '{self.pipeline_name}' encountered error: {error}",
            "ERROR"
        )

        self.observable.notify(PipelineEvent(
            event_type=EventType.PIPELINE_FAILED,
            card_id=self._card_id,
            error=error,
            data={"pipeline": self.pipeline_name}
        ))

    @wrap_exception(PipelineException, "Failed to pause pipeline")
    def pause(self) -> None:
        """
        Pause pipeline execution.

        WHY: Enables supervisor to pause long-running pipelines for
             resource management or debugging.

        Raises:
            PipelineException: If pipeline not running
        """
        # Guard clause: Not running
        if self.state != PipelineState.RUNNING:
            raise PipelineException(
                "Cannot pause pipeline that is not running",
                context={"state": self.state.value}
            )

        self.state = PipelineState.PAUSED
        self.logger.log("Pipeline paused", "INFO")

        self.observable.notify(PipelineEvent(
            event_type=EventType.PIPELINE_PAUSED,
            card_id=self._card_id,
            data={"pipeline": self.pipeline_name}
        ))

    @wrap_exception(PipelineException, "Failed to resume pipeline")
    def resume(self) -> None:
        """
        Resume paused pipeline.

        Raises:
            PipelineException: If pipeline not paused
        """
        # Guard clause: Not paused
        if self.state != PipelineState.PAUSED:
            raise PipelineException(
                "Cannot resume pipeline that is not paused",
                context={"state": self.state.value}
            )

        self.state = PipelineState.RUNNING
        self.logger.log("Pipeline resumed", "INFO")

        self.observable.notify(PipelineEvent(
            event_type=EventType.PIPELINE_RESUMED,
            card_id=self._card_id,
            data={"pipeline": self.pipeline_name}
        ))

    def get_state(self) -> PipelineState:
        """
        Get current state.

        Returns:
            Current pipeline state
        """
        return self.state

    def is_running(self) -> bool:
        """Check if pipeline is running."""
        return self.state == PipelineState.RUNNING

    def can_modify_stages(self) -> bool:
        """
        Check if stages can be modified.

        WHY: Stages can only be modified when pipeline is not running.

        Returns:
            True if stages can be added/removed
        """
        return self.state != PipelineState.RUNNING

    @wrap_exception(PipelineException, "Failed to validate stage modification")
    def validate_stage_modification(self, operation: str) -> None:
        """
        Validate stage can be modified.

        Args:
            operation: Description of operation for error message

        Raises:
            PipelineException: If pipeline is running
        """
        # Guard clause: Cannot modify running pipeline
        if self.state == PipelineState.RUNNING:
            raise PipelineException(
                f"Cannot {operation} while pipeline is running",
                context={"state": self.state.value}
            )
