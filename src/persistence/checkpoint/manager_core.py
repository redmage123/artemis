#!/usr/bin/env python3
"""
Checkpoint Manager Core

WHY: Orchestrates checkpoint operations by coordinating creator, restorer,
     storage, and cache components into a unified checkpoint management API.

RESPONSIBILITY:
    - Provide unified checkpoint management interface
    - Coordinate checkpoint creation, storage, and restoration
    - Manage LLM response caching
    - Track pipeline execution state

PATTERNS:
    - Facade Pattern: Simplify complex subsystem interactions
    - Dependency Injection: Accept repository and cache dependencies
    - Single Responsibility: Orchestrate, don't implement
"""

from typing import Dict, List, Optional, Any
from datetime import datetime

from debug_mixin import DebugMixin
from .models import PipelineCheckpoint, CheckpointStatus
from .storage import CheckpointRepository, create_checkpoint_repository
from .creator import (
    CheckpointCreator,
    CheckpointUpdater,
    ProgressCalculator
)
from .restorer import (
    CheckpointStateRestorer,
    LLMCacheManager,
    create_state_restorer
)


# ============================================================================
# CHECKPOINT MANAGER
# ============================================================================

class CheckpointManager(DebugMixin):
    """
    Main checkpoint manager facade

    Coordinates checkpoint operations across creator, restorer,
    storage, and cache components. Provides simplified API for
    pipeline checkpoint management.
    """

    def __init__(
        self,
        card_id: str,
        checkpoint_dir: Optional[str] = None,
        enable_llm_cache: bool = True,
        verbose: bool = True
    ):
        """
        Initialize checkpoint manager

        Args:
            card_id: Kanban card ID
            checkpoint_dir: Directory for checkpoint storage
            enable_llm_cache: Enable LLM response caching
            verbose: Enable verbose logging
        """
        DebugMixin.__init__(self, component_name="checkpoint")

        self.card_id = card_id
        self.verbose = verbose

        # Initialize repository
        self.repository = create_checkpoint_repository(
            storage_type="filesystem",
            checkpoint_dir=checkpoint_dir
        )

        # Initialize components
        self.creator = CheckpointCreator()
        self.updater = CheckpointUpdater()
        self.progress_calculator = ProgressCalculator()
        self.cache_manager = LLMCacheManager(enabled=enable_llm_cache)
        self.state_restorer = create_state_restorer(
            self.repository,
            enable_llm_cache
        )

        # Current checkpoint
        self.checkpoint: Optional[PipelineCheckpoint] = None

        self.debug_log(
            "Checkpoint manager initialized",
            card_id=card_id,
            checkpoint_dir=str(self.repository.checkpoint_dir) if hasattr(self.repository, 'checkpoint_dir') else 'unknown'
        )

        if self.verbose:
            print(f"[CheckpointManager] Initialized for card {card_id}")

    # ========================================================================
    # CHECKPOINT LIFECYCLE
    # ========================================================================

    def create_checkpoint(
        self,
        total_stages: int,
        execution_context: Optional[Dict[str, Any]] = None
    ) -> PipelineCheckpoint:
        """
        Create a new checkpoint

        Args:
            total_stages: Total number of stages in pipeline
            execution_context: Initial execution context

        Returns:
            New PipelineCheckpoint
        """
        self.checkpoint = self.creator.create_new_checkpoint(
            card_id=self.card_id,
            total_stages=total_stages,
            execution_context=execution_context
        )

        self.repository.save(self.checkpoint)

        if self.verbose:
            print(f"[CheckpointManager] Created checkpoint: {self.checkpoint.checkpoint_id}")

        return self.checkpoint

    def save_stage_checkpoint(
        self,
        stage_name: str,
        status: str,
        result: Optional[Dict[str, Any]] = None,
        artifacts: Optional[List[str]] = None,
        llm_responses: Optional[List[Dict[str, Any]]] = None,
        error_message: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> None:
        """
        Save checkpoint for a completed stage

        Args:
            stage_name: Name of the stage
            status: Stage status (completed, failed, skipped)
            result: Stage execution result
            artifacts: List of artifact file paths
            llm_responses: LLM responses to cache
            error_message: Error message if failed
            start_time: Stage start time
            end_time: Stage end time

        Raises:
            ValueError: If no checkpoint created
        """
        # Guard: Checkpoint must exist
        if not self.checkpoint:
            raise ValueError("No checkpoint created. Call create_checkpoint() first.")

        self.debug_log(
            "Saving stage checkpoint",
            stage_name=stage_name,
            status=status,
            artifacts_count=len(artifacts or [])
        )

        # Create stage checkpoint
        stage_checkpoint = self.creator.create_stage_checkpoint(
            stage_name=stage_name,
            status=status,
            start_time=start_time,
            end_time=end_time,
            result=result,
            artifacts=artifacts,
            llm_responses=llm_responses,
            error_message=error_message
        )

        # Update pipeline checkpoint
        self.updater.update_with_stage(self.checkpoint, stage_checkpoint)

        # Cache LLM responses
        if llm_responses:
            for response in llm_responses:
                prompt = response.get("prompt", "")
                if prompt:
                    self.cache_manager.store_response(
                        self.card_id,
                        stage_name,
                        prompt,
                        response
                    )

        # Save checkpoint
        self.repository.save(self.checkpoint)

        if self.verbose:
            duration = stage_checkpoint.duration_seconds
            print(f"[CheckpointManager] Saved stage checkpoint: {stage_name} ({status})")
            print(f"[CheckpointManager]    Duration: {duration:.2f}s")
            print(f"[CheckpointManager]    Progress: {self.checkpoint.stages_completed}/{self.checkpoint.total_stages}")

    # ========================================================================
    # CHECKPOINT STATE MANAGEMENT
    # ========================================================================

    def set_current_stage(self, stage_name: str) -> None:
        """
        Set the currently executing stage

        Args:
            stage_name: Stage name

        Raises:
            ValueError: If no checkpoint created
        """
        # Guard: Checkpoint must exist
        if not self.checkpoint:
            raise ValueError("No checkpoint created.")

        self.updater.set_current_stage(self.checkpoint, stage_name)
        self.repository.save(self.checkpoint)

        if self.verbose:
            print(f"[CheckpointManager] Current stage: {stage_name}")

    def mark_completed(self) -> None:
        """Mark pipeline as completed"""
        # Guard: Return early if no checkpoint
        if not self.checkpoint:
            return

        self.updater.mark_completed(self.checkpoint)
        self.repository.save(self.checkpoint)

        if self.verbose:
            print(f"[CheckpointManager] Pipeline completed!")
            print(f"[CheckpointManager]    Total duration: {self.checkpoint.total_duration_seconds:.2f}s")
            print(f"[CheckpointManager]    Stages completed: {self.checkpoint.stages_completed}/{self.checkpoint.total_stages}")

    def mark_failed(self, reason: str) -> None:
        """
        Mark pipeline as failed

        Args:
            reason: Failure reason
        """
        # Guard: Return early if no checkpoint
        if not self.checkpoint:
            return

        self.updater.mark_failed(self.checkpoint, reason)
        self.repository.save(self.checkpoint)

        if self.verbose:
            print(f"[CheckpointManager] Pipeline failed: {reason}")

    # ========================================================================
    # CHECKPOINT RESTORATION
    # ========================================================================

    def can_resume(self) -> bool:
        """
        Check if there's a checkpoint to resume from

        Returns:
            True if checkpoint exists and can be resumed
        """
        return self.state_restorer.can_resume(self.card_id)

    def resume(self) -> Optional[PipelineCheckpoint]:
        """
        Resume from checkpoint

        Returns:
            Checkpoint if available, None otherwise
        """
        self.debug_log("Attempting to resume from checkpoint", card_id=self.card_id)

        # Guard: Cannot resume if not resumable
        if not self.can_resume():
            self.debug_log("Cannot resume - no valid checkpoint found")
            if self.verbose:
                print(f"[CheckpointManager] No checkpoint to resume from")
            return None

        # Restore full state including cache
        self.checkpoint = self.state_restorer.restore_full_state(self.card_id)

        self.debug_log(
            "Resumed from checkpoint",
            checkpoint_id=self.checkpoint.checkpoint_id if self.checkpoint else None,
            completed_stages=len(self.checkpoint.completed_stages) if self.checkpoint else 0
        )

        if self.verbose and self.checkpoint:
            print(f"[CheckpointManager] Resumed from checkpoint!")
            print(f"[CheckpointManager]    Checkpoint ID: {self.checkpoint.checkpoint_id}")
            print(f"[CheckpointManager]    Completed stages: {len(self.checkpoint.completed_stages)}")
            print(f"[CheckpointManager]    Current stage: {self.checkpoint.current_stage}")
            print(f"[CheckpointManager]    Resume count: {self.checkpoint.resume_count}")

        return self.checkpoint

    # ========================================================================
    # LLM CACHE OPERATIONS
    # ========================================================================

    def get_cached_llm_response(
        self,
        stage_name: str,
        prompt: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached LLM response if available

        Args:
            stage_name: Stage name
            prompt: LLM prompt

        Returns:
            Cached response or None
        """
        cached = self.cache_manager.get_cached_response(
            self.card_id,
            stage_name,
            prompt
        )

        if cached and self.verbose:
            print(f"[CheckpointManager] LLM cache hit for {stage_name}")

        return cached

    # ========================================================================
    # PROGRESS AND NAVIGATION
    # ========================================================================

    def get_next_stage(self, all_stages: List[str]) -> Optional[str]:
        """
        Get the next stage to execute after resume

        Args:
            all_stages: List of all stages in order

        Returns:
            Next stage name or None if all completed
        """
        return self.progress_calculator.get_next_stage(
            self.checkpoint,
            all_stages
        )

    def get_progress(self) -> Dict[str, Any]:
        """
        Get execution progress

        Returns:
            Progress statistics
        """
        return self.progress_calculator.calculate_progress(self.checkpoint)

    # ========================================================================
    # CHECKPOINT MANAGEMENT
    # ========================================================================

    def clear_checkpoint(self) -> None:
        """Clear checkpoint (delete from disk)"""
        self.debug_log("Clearing checkpoint", card_id=self.card_id)

        deleted = self.repository.delete(self.card_id)

        if deleted:
            self.checkpoint = None
            self.cache_manager.clear_cache()
            self.debug_log("Checkpoint cleared", card_id=self.card_id)

            if self.verbose:
                print(f"[CheckpointManager] Checkpoint cleared")


# ============================================================================
# FACTORY FUNCTION
# ============================================================================

def create_checkpoint_manager(
    card_id: str,
    verbose: bool = True,
    checkpoint_dir: Optional[str] = None,
    enable_llm_cache: bool = True
) -> CheckpointManager:
    """
    Create checkpoint manager

    Factory function for creating CheckpointManager instances

    Args:
        card_id: Card ID
        verbose: Enable verbose logging
        checkpoint_dir: Directory for checkpoint storage
        enable_llm_cache: Enable LLM caching

    Returns:
        CheckpointManager instance
    """
    return CheckpointManager(
        card_id=card_id,
        checkpoint_dir=checkpoint_dir,
        enable_llm_cache=enable_llm_cache,
        verbose=verbose
    )
