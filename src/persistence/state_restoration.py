#!/usr/bin/env python3
"""
State Restoration

WHY: Handles pipeline state restoration for crash recovery and resume operations.
     Encapsulates complex recovery logic separate from persistence layer.

RESPONSIBILITY: Restores pipeline state from persisted data.
                Validates state consistency for safe resume operations.

PATTERNS:
- Single Responsibility: Focused on state restoration only
- Guard Clauses: Early returns for validation
- Strategy Pattern: Different restoration strategies
"""

from typing import Optional, Dict, Any, List
from datetime import datetime

from .interface import PersistenceStoreInterface
from .models import PipelineState, StageCheckpoint


class StateRestorationManager:
    """
    Manages pipeline state restoration.

    WHY: Centralizes recovery logic separate from persistence layer.
         Ensures safe and consistent pipeline resume operations.

    RESPONSIBILITY: Restores pipeline state for recovery.
                    Validates state consistency before resume.

    PATTERNS: Single Responsibility - restoration logic only.
              Guard Clauses - validation checks.
    """

    def __init__(self, store: PersistenceStoreInterface):
        """
        Initialize restoration manager.

        WHY: Wraps persistence store for restoration operations.
        PERFORMANCE: O(1) initialization.

        Args:
            store: Persistence store implementation
        """
        self.store = store

    def restore_pipeline_state(self, card_id: str) -> Optional[PipelineState]:
        """
        Restore pipeline state by card ID.

        WHY: Retrieves and validates pipeline state for resume.
        PERFORMANCE: O(1) with indexed store, O(n) with file-based store.

        Args:
            card_id: Pipeline card ID to restore

        Returns:
            Restored PipelineState if valid, None otherwise
        """
        state = self.store.load_pipeline_state(card_id)

        # Early return guard clause - state not found
        if not state:
            return None

        # Validate state before returning
        if not self._validate_state(state):
            return None

        return state

    def can_resume(self, card_id: str) -> bool:
        """
        Check if pipeline can be safely resumed.

        WHY: Validates pipeline is in resumable state.
        PERFORMANCE: O(1) state lookup and validation.

        Args:
            card_id: Pipeline card ID

        Returns:
            True if pipeline can be resumed, False otherwise
        """
        state = self.store.load_pipeline_state(card_id)

        # Early return guard clause - state not found
        if not state:
            return False

        # Early return guard clause - not in resumable status
        resumable_statuses = {'running', 'failed', 'paused'}
        if state.status not in resumable_statuses:
            return False

        # State is resumable
        return True

    def get_resume_point(self, card_id: str) -> Optional[str]:
        """
        Get stage name to resume from.

        WHY: Determines where to restart pipeline execution.
        PERFORMANCE: O(1) state lookup.

        Args:
            card_id: Pipeline card ID

        Returns:
            Stage name to resume from, None if not resumable
        """
        state = self.store.load_pipeline_state(card_id)

        # Early return guard clause - state not found
        if not state:
            return None

        # Early return guard clause - not in resumable status
        if not self.can_resume(card_id):
            return None

        # Return current stage if set, otherwise None
        return state.current_stage

    def get_completed_stages(self, card_id: str) -> List[str]:
        """
        Get list of completed stages for a pipeline.

        WHY: Identifies which stages to skip during resume.
        PERFORMANCE: O(1) state lookup.

        Args:
            card_id: Pipeline card ID

        Returns:
            List of completed stage names
        """
        state = self.store.load_pipeline_state(card_id)

        # Early return guard clause - state not found
        if not state:
            return []

        return state.stages_completed

    def restore_stage_checkpoints(self, card_id: str) -> List[StageCheckpoint]:
        """
        Restore all stage checkpoints for a pipeline.

        WHY: Retrieves complete stage execution history for analysis.
        PERFORMANCE: O(n) where n is number of checkpoints.

        Args:
            card_id: Pipeline card ID

        Returns:
            List of stage checkpoints
        """
        return self.store.load_stage_checkpoints(card_id)

    def get_last_successful_stage(self, card_id: str) -> Optional[str]:
        """
        Get name of last successfully completed stage.

        WHY: Identifies safe recovery point for failed pipelines.
        PERFORMANCE: O(n) where n is number of checkpoints.

        Args:
            card_id: Pipeline card ID

        Returns:
            Name of last successful stage, None if none completed
        """
        checkpoints = self.store.load_stage_checkpoints(card_id)

        # Early return guard clause - no checkpoints
        if not checkpoints:
            return None

        # Find last completed checkpoint
        for checkpoint in reversed(checkpoints):
            if checkpoint.status == 'completed':
                return checkpoint.stage_name

        return None

    def get_failed_stage(self, card_id: str) -> Optional[str]:
        """
        Get name of failed stage if any.

        WHY: Identifies which stage caused pipeline failure.
        PERFORMANCE: O(n) where n is number of checkpoints.

        Args:
            card_id: Pipeline card ID

        Returns:
            Name of failed stage, None if no failure
        """
        checkpoints = self.store.load_stage_checkpoints(card_id)

        # Find failed checkpoint
        for checkpoint in checkpoints:
            if checkpoint.status == 'failed':
                return checkpoint.stage_name

        return None

    def _validate_state(self, state: PipelineState) -> bool:
        """
        Validate pipeline state consistency.

        WHY: Ensures state is internally consistent before use.
        PERFORMANCE: O(1) validation checks.

        Args:
            state: Pipeline state to validate

        Returns:
            True if state is valid, False otherwise
        """
        # Early return guard clause - missing required fields
        if not state.card_id or not state.status:
            return False

        # Early return guard clause - invalid status
        valid_statuses = {'running', 'completed', 'failed', 'paused'}
        if state.status not in valid_statuses:
            return False

        # Early return guard clause - completed should have completion time
        if state.status == 'completed' and not state.completed_at:
            return False

        # All checks passed
        return True

    def create_resume_context(self, card_id: str) -> Optional[Dict[str, Any]]:
        """
        Create context for pipeline resume.

        WHY: Provides all necessary information for pipeline restart.
        PERFORMANCE: O(n) where n is number of checkpoints.

        Args:
            card_id: Pipeline card ID

        Returns:
            Resume context dictionary, None if not resumable
        """
        # Early return guard clause - not resumable
        if not self.can_resume(card_id):
            return None

        state = self.store.load_pipeline_state(card_id)
        checkpoints = self.store.load_stage_checkpoints(card_id)

        # Early return guard clause - state not found
        if not state:
            return None

        # Build resume context
        return {
            'card_id': card_id,
            'status': state.status,
            'current_stage': state.current_stage,
            'completed_stages': state.stages_completed,
            'stage_results': state.stage_results,
            'last_successful_stage': self.get_last_successful_stage(card_id),
            'failed_stage': self.get_failed_stage(card_id),
            'checkpoint_count': len(checkpoints),
            'updated_at': state.updated_at
        }
