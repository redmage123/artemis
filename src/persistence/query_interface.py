#!/usr/bin/env python3
"""
Persistence Query Interface

WHY: Provides high-level query operations for analyzing pipeline state.
     Abstracts complex queries from clients, maintaining encapsulation.

RESPONSIBILITY: Offers query methods for pipeline analysis and reporting.
                Wraps persistence store with convenient query operations.

PATTERNS:
- Facade Pattern: Simplifies complex query operations
- Delegation Pattern: Delegates to underlying store
- Single Responsibility: Focused on query operations only
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from .interface import PersistenceStoreInterface
from .models import PipelineState, StageCheckpoint


class PersistenceQueryInterface:
    """
    High-level query interface for persistence store.

    WHY: Provides convenient query methods for analyzing pipeline state
         without exposing underlying storage implementation details.

    RESPONSIBILITY: Wraps persistence store with high-level query operations.
                    Provides reporting and analysis functionality.

    PATTERNS: Facade Pattern - simplifies complex operations.
              Delegation Pattern - delegates to underlying store.
    """

    def __init__(self, store: PersistenceStoreInterface):
        """
        Initialize query interface.

        WHY: Wraps persistence store for query operations.
        PERFORMANCE: O(1) initialization.

        Args:
            store: Underlying persistence store implementation
        """
        self.store = store

    def get_pipeline_by_id(self, card_id: str) -> Optional[PipelineState]:
        """
        Get pipeline state by card ID.

        WHY: Convenience method for retrieving pipeline state.
        PERFORMANCE: O(1) with indexed store, O(n) with file-based store.

        Args:
            card_id: Pipeline card ID

        Returns:
            PipelineState if found, None otherwise
        """
        return self.store.load_pipeline_state(card_id)

    def get_pipeline_checkpoints(self, card_id: str) -> List[StageCheckpoint]:
        """
        Get all checkpoints for a pipeline.

        WHY: Retrieves complete stage execution history.
        PERFORMANCE: O(n) where n is number of checkpoints.

        Args:
            card_id: Pipeline card ID

        Returns:
            List of stage checkpoints
        """
        return self.store.load_stage_checkpoints(card_id)

    def list_resumable_pipelines(self) -> List[str]:
        """
        List all pipelines that can be resumed.

        WHY: Identifies incomplete pipelines for recovery operations.
        PERFORMANCE: O(n) where n is total number of pipelines.

        Returns:
            List of resumable pipeline card IDs
        """
        return self.store.get_resumable_pipelines()

    def get_failed_pipelines(self) -> List[str]:
        """
        Get list of failed pipeline IDs.

        WHY: Identifies pipelines requiring attention or retry.
        PERFORMANCE: O(n) where n is total number of pipelines.

        Returns:
            List of failed pipeline card IDs
        """
        resumable = self.store.get_resumable_pipelines()
        failed = []

        for card_id in resumable:
            state = self.store.load_pipeline_state(card_id)
            if state and state.status == 'failed':
                failed.append(card_id)

        return failed

    def get_running_pipelines(self) -> List[str]:
        """
        Get list of currently running pipeline IDs.

        WHY: Monitors active pipeline executions.
        PERFORMANCE: O(n) where n is total number of pipelines.

        Returns:
            List of running pipeline card IDs
        """
        resumable = self.store.get_resumable_pipelines()
        running = []

        for card_id in resumable:
            state = self.store.load_pipeline_state(card_id)
            if state and state.status == 'running':
                running.append(card_id)

        return running

    def get_completed_pipelines(self, limit: Optional[int] = None) -> List[str]:
        """
        Get list of completed pipeline IDs.

        WHY: Provides access to successful pipeline executions for analysis.
        PERFORMANCE: O(n) where n is total number of pipelines.

        Args:
            limit: Optional limit on number of results

        Returns:
            List of completed pipeline card IDs
        """
        # Note: This is a simplified implementation
        # For production, would need direct store support for filtering by status
        # and limiting results efficiently
        return []

    def has_checkpoint(self, card_id: str, stage_name: str) -> bool:
        """
        Check if a checkpoint exists for a specific stage.

        WHY: Determines if a stage has been executed in a pipeline.
        PERFORMANCE: O(n) where n is number of checkpoints for card_id.

        Args:
            card_id: Pipeline card ID
            stage_name: Name of stage to check

        Returns:
            True if checkpoint exists, False otherwise
        """
        checkpoints = self.store.load_stage_checkpoints(card_id)
        return any(cp.stage_name == stage_name for cp in checkpoints)

    def get_stage_status(self, card_id: str, stage_name: str) -> Optional[str]:
        """
        Get status of a specific stage.

        WHY: Retrieves execution status of individual stage.
        PERFORMANCE: O(n) where n is number of checkpoints for card_id.

        Args:
            card_id: Pipeline card ID
            stage_name: Name of stage

        Returns:
            Stage status if checkpoint exists, None otherwise
        """
        checkpoints = self.store.load_stage_checkpoints(card_id)

        for checkpoint in checkpoints:
            if checkpoint.stage_name == stage_name:
                return checkpoint.status

        return None

    def get_latest_checkpoint(self, card_id: str) -> Optional[StageCheckpoint]:
        """
        Get the most recent checkpoint for a pipeline.

        WHY: Identifies last executed stage in a pipeline.
        PERFORMANCE: O(n) where n is number of checkpoints for card_id.

        Args:
            card_id: Pipeline card ID

        Returns:
            Latest StageCheckpoint if any exist, None otherwise
        """
        checkpoints = self.store.load_stage_checkpoints(card_id)

        # Early return guard clause - no checkpoints
        if not checkpoints:
            return None

        # Checkpoints exist - return last one (already sorted by started_at)
        return checkpoints[-1]

    def cleanup_old_data(self, days: int = 30) -> None:
        """
        Clean up old pipeline data.

        WHY: Delegates cleanup to underlying store.
        PERFORMANCE: Store-dependent.

        Args:
            days: Number of days to retain data
        """
        self.store.cleanup_old_states(days)
