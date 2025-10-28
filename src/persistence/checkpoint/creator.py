#!/usr/bin/env python3
"""
Checkpoint Creator

WHY: Encapsulates checkpoint creation and stage update logic, separating
     construction concerns from storage and restoration responsibilities.

RESPONSIBILITY:
    - Create new pipeline checkpoints
    - Update checkpoints with stage completion data
    - Track stage status and progress
    - Calculate execution statistics

PATTERNS:
    - Builder Pattern: Incrementally construct checkpoint state
    - Single Responsibility: Only handles checkpoint creation and updates
    - Guard Clauses: Validate preconditions before operations
"""

import time
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable

from .models import (
    PipelineCheckpoint,
    StageCheckpoint,
    CheckpointStatus,
    calculate_progress_percent,
    estimate_remaining_time
)


# ============================================================================
# CHECKPOINT CREATION
# ============================================================================

class CheckpointCreator:
    """
    Creates and updates pipeline checkpoints

    Handles the construction and modification of checkpoint objects,
    tracking stage execution and calculating progress metrics.
    """

    @staticmethod
    def create_new_checkpoint(
        card_id: str,
        total_stages: int,
        execution_context: Optional[Dict[str, Any]] = None
    ) -> PipelineCheckpoint:
        """
        Create a new pipeline checkpoint

        Args:
            card_id: Kanban card ID
            total_stages: Total number of stages in pipeline
            execution_context: Initial execution context

        Returns:
            New PipelineCheckpoint instance
        """
        checkpoint_id = f"checkpoint-{card_id}-{int(time.time())}"
        now = datetime.now()

        return PipelineCheckpoint(
            checkpoint_id=checkpoint_id,
            card_id=card_id,
            status=CheckpointStatus.ACTIVE,
            created_at=now,
            updated_at=now,
            total_stages=total_stages,
            execution_context=execution_context or {}
        )

    @staticmethod
    def create_stage_checkpoint(
        stage_name: str,
        status: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        result: Optional[Dict[str, Any]] = None,
        artifacts: Optional[List[str]] = None,
        llm_responses: Optional[List[Dict[str, Any]]] = None,
        error_message: Optional[str] = None
    ) -> StageCheckpoint:
        """
        Create a stage checkpoint

        Args:
            stage_name: Name of the stage
            status: Stage status (completed, failed, skipped)
            start_time: Stage start time
            end_time: Stage end time
            result: Stage execution result
            artifacts: List of artifact file paths
            llm_responses: LLM responses to cache
            error_message: Error message if failed

        Returns:
            StageCheckpoint instance
        """
        # Calculate duration using guard clause
        duration = 0.0
        if start_time and end_time:
            duration = (end_time - start_time).total_seconds()

        return StageCheckpoint(
            stage_name=stage_name,
            status=status,
            start_time=start_time or datetime.now(),
            end_time=end_time or datetime.now(),
            duration_seconds=duration,
            result=result,
            artifacts=artifacts or [],
            llm_responses=llm_responses or [],
            error_message=error_message
        )


# ============================================================================
# CHECKPOINT UPDATER
# ============================================================================

class CheckpointUpdater:
    """
    Updates existing checkpoints with new stage data

    Handles incremental updates to checkpoint state, maintaining
    consistency and tracking progress statistics.
    """

    # Dispatch table for stage status updates
    _STATUS_HANDLERS: Dict[str, Callable] = {}

    @classmethod
    def _register_status_handler(cls, status: str):
        """Decorator to register status handler"""
        def decorator(func):
            cls._STATUS_HANDLERS[status] = func
            return func
        return decorator

    def __init__(self):
        """Initialize updater with status handlers"""
        self._setup_status_handlers()

    def _setup_status_handlers(self):
        """Setup status update dispatch table"""
        # Using a dispatch table pattern for status handling
        pass

    def update_with_stage(
        self,
        checkpoint: PipelineCheckpoint,
        stage_checkpoint: StageCheckpoint
    ) -> None:
        """
        Update checkpoint with completed stage data

        Args:
            checkpoint: Pipeline checkpoint to update
            stage_checkpoint: Stage checkpoint to add

        Raises:
            ValueError: If checkpoint is None
        """
        # Guard: Checkpoint must exist
        if not checkpoint:
            raise ValueError("Cannot update None checkpoint")

        stage_name = stage_checkpoint.stage_name

        # Add stage checkpoint
        checkpoint.stage_checkpoints[stage_name] = stage_checkpoint

        # Update stage tracking based on status
        self._update_stage_lists(checkpoint, stage_name, stage_checkpoint.status)

        # Update statistics
        checkpoint.total_duration_seconds += stage_checkpoint.duration_seconds
        checkpoint.updated_at = datetime.now()

    def _update_stage_lists(
        self,
        checkpoint: PipelineCheckpoint,
        stage_name: str,
        status: str
    ) -> None:
        """
        Update stage tracking lists based on status

        Uses dispatch table pattern to handle different statuses

        Args:
            checkpoint: Checkpoint to update
            stage_name: Stage name
            status: Stage status
        """
        # Dispatch table for status handlers
        status_handlers = {
            "completed": lambda: self._handle_completed(checkpoint, stage_name),
            "failed": lambda: self._handle_failed(checkpoint, stage_name),
            "skipped": lambda: self._handle_skipped(checkpoint, stage_name),
        }

        handler = status_handlers.get(status)

        if handler:
            handler()

    def _handle_completed(self, checkpoint: PipelineCheckpoint, stage_name: str) -> None:
        """Handle completed stage status"""
        if stage_name not in checkpoint.completed_stages:
            checkpoint.completed_stages.append(stage_name)
            checkpoint.stages_completed += 1

    def _handle_failed(self, checkpoint: PipelineCheckpoint, stage_name: str) -> None:
        """Handle failed stage status"""
        if stage_name not in checkpoint.failed_stages:
            checkpoint.failed_stages.append(stage_name)

    def _handle_skipped(self, checkpoint: PipelineCheckpoint, stage_name: str) -> None:
        """Handle skipped stage status"""
        if stage_name not in checkpoint.skipped_stages:
            checkpoint.skipped_stages.append(stage_name)

    def set_current_stage(
        self,
        checkpoint: PipelineCheckpoint,
        stage_name: str
    ) -> None:
        """
        Set the currently executing stage

        Args:
            checkpoint: Checkpoint to update
            stage_name: Current stage name

        Raises:
            ValueError: If checkpoint is None
        """
        # Guard: Checkpoint must exist
        if not checkpoint:
            raise ValueError("Cannot update None checkpoint")

        checkpoint.current_stage = stage_name
        checkpoint.updated_at = datetime.now()

    def mark_completed(self, checkpoint: PipelineCheckpoint) -> None:
        """
        Mark pipeline as completed

        Args:
            checkpoint: Checkpoint to update

        Raises:
            ValueError: If checkpoint is None
        """
        # Guard: Checkpoint must exist
        if not checkpoint:
            raise ValueError("Cannot update None checkpoint")

        checkpoint.status = CheckpointStatus.COMPLETED
        checkpoint.current_stage = None
        checkpoint.updated_at = datetime.now()

    def mark_failed(
        self,
        checkpoint: PipelineCheckpoint,
        reason: str
    ) -> None:
        """
        Mark pipeline as failed

        Args:
            checkpoint: Checkpoint to update
            reason: Failure reason

        Raises:
            ValueError: If checkpoint is None
        """
        # Guard: Checkpoint must exist
        if not checkpoint:
            raise ValueError("Cannot update None checkpoint")

        checkpoint.status = CheckpointStatus.FAILED
        checkpoint.metadata["failure_reason"] = reason
        checkpoint.updated_at = datetime.now()


# ============================================================================
# PROGRESS CALCULATOR
# ============================================================================

class ProgressCalculator:
    """
    Calculates execution progress and time estimates

    Provides metrics and statistics about checkpoint execution progress.
    """

    @staticmethod
    def calculate_progress(checkpoint: PipelineCheckpoint) -> Dict[str, Any]:
        """
        Calculate execution progress statistics

        Args:
            checkpoint: Checkpoint to analyze

        Returns:
            Dictionary containing progress metrics
        """
        # Guard: Return empty progress if no checkpoint
        if not checkpoint:
            return {
                "progress_percent": 0,
                "stages_completed": 0,
                "total_stages": 0,
                "current_stage": None,
                "elapsed_seconds": 0,
                "estimated_remaining_seconds": 0
            }

        elapsed = (datetime.now() - checkpoint.created_at).total_seconds()

        # Calculate progress percentage
        progress_percent = calculate_progress_percent(
            checkpoint.stages_completed,
            checkpoint.total_stages
        )

        # Estimate remaining time
        estimated_remaining = estimate_remaining_time(
            checkpoint.total_duration_seconds,
            checkpoint.stages_completed,
            checkpoint.total_stages
        )

        return {
            "progress_percent": progress_percent,
            "stages_completed": checkpoint.stages_completed,
            "total_stages": checkpoint.total_stages,
            "current_stage": checkpoint.current_stage,
            "elapsed_seconds": round(elapsed, 2),
            "estimated_remaining_seconds": estimated_remaining
        }

    @staticmethod
    def get_next_stage(
        checkpoint: Optional[PipelineCheckpoint],
        all_stages: List[str]
    ) -> Optional[str]:
        """
        Get the next stage to execute after resume

        Args:
            checkpoint: Current checkpoint (may be None for new pipeline)
            all_stages: List of all stages in order

        Returns:
            Next stage name or None if all completed
        """
        # Guard: If no checkpoint, start from first stage
        if not checkpoint:
            return all_stages[0] if all_stages else None

        # Find first stage not completed
        for stage in all_stages:
            if stage not in checkpoint.completed_stages:
                return stage

        return None  # All stages completed


# ============================================================================
# LLM CACHE KEY GENERATOR
# ============================================================================

class LLMCacheKeyGenerator:
    """
    Generates cache keys for LLM responses

    Creates consistent, collision-resistant keys for caching LLM responses.
    """

    @staticmethod
    def generate_cache_key(
        card_id: str,
        stage_name: str,
        prompt: str
    ) -> str:
        """
        Generate cache key for LLM response

        Uses SHA-256 hash of prompt to create deterministic key

        Args:
            card_id: Card ID
            stage_name: Stage name
            prompt: LLM prompt text

        Returns:
            Cache key string
        """
        # Hash the prompt for cache key
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:16]
        return f"{card_id}:{stage_name}:{prompt_hash}"
