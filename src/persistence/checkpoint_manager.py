#!/usr/bin/env python3
"""
Checkpoint Manager

WHY: Manages checkpoint creation and validation for pipeline stages.
     Encapsulates checkpoint logic separate from storage concerns.

RESPONSIBILITY: Creates, validates, and manages stage checkpoints.
                Ensures checkpoint consistency and data integrity.

PATTERNS:
- Single Responsibility: Focused on checkpoint management only
- Guard Clauses: Early returns for validation
- Factory Methods: Checkpoint creation methods
"""

from datetime import datetime
from typing import Dict, Any, Optional

from .models import StageCheckpoint


class CheckpointManager:
    """
    Manages stage checkpoint creation and validation.

    WHY: Centralizes checkpoint logic separate from persistence layer.
         Ensures consistent checkpoint creation across the system.

    RESPONSIBILITY: Creates and validates stage checkpoints.
                    Provides factory methods for checkpoint creation.

    PATTERNS: Factory Pattern - checkpoint creation methods.
              Single Responsibility - checkpoint management only.
    """

    @staticmethod
    def create_checkpoint(
        card_id: str,
        stage_name: str,
        status: str,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        started_at: Optional[str] = None,
        completed_at: Optional[str] = None
    ) -> StageCheckpoint:
        """
        Create a new stage checkpoint.

        WHY: Factory method for consistent checkpoint creation.
        PERFORMANCE: O(1) object creation.

        Args:
            card_id: Pipeline card ID
            stage_name: Name of stage
            status: Checkpoint status (started, completed, failed)
            result: Stage result data
            error: Error message if failed
            started_at: Start timestamp (defaults to now)
            completed_at: Completion timestamp

        Returns:
            New StageCheckpoint instance
        """
        # Default values
        if result is None:
            result = {}

        if started_at is None:
            started_at = datetime.utcnow().isoformat() + 'Z'

        return StageCheckpoint(
            card_id=card_id,
            stage_name=stage_name,
            status=status,
            started_at=started_at,
            completed_at=completed_at,
            result=result,
            error=error
        )

    @staticmethod
    def create_started_checkpoint(
        card_id: str,
        stage_name: str
    ) -> StageCheckpoint:
        """
        Create a 'started' checkpoint.

        WHY: Convenience method for stage start checkpoints.
        PERFORMANCE: O(1) checkpoint creation.

        Args:
            card_id: Pipeline card ID
            stage_name: Name of stage

        Returns:
            StageCheckpoint with status='started'
        """
        return CheckpointManager.create_checkpoint(
            card_id=card_id,
            stage_name=stage_name,
            status='started'
        )

    @staticmethod
    def create_completed_checkpoint(
        card_id: str,
        stage_name: str,
        result: Dict[str, Any],
        started_at: str
    ) -> StageCheckpoint:
        """
        Create a 'completed' checkpoint.

        WHY: Convenience method for successful stage completion.
        PERFORMANCE: O(1) checkpoint creation.

        Args:
            card_id: Pipeline card ID
            stage_name: Name of stage
            result: Stage result data
            started_at: Original start timestamp

        Returns:
            StageCheckpoint with status='completed'
        """
        return CheckpointManager.create_checkpoint(
            card_id=card_id,
            stage_name=stage_name,
            status='completed',
            result=result,
            started_at=started_at,
            completed_at=datetime.utcnow().isoformat() + 'Z'
        )

    @staticmethod
    def create_failed_checkpoint(
        card_id: str,
        stage_name: str,
        error: str,
        started_at: str,
        result: Optional[Dict[str, Any]] = None
    ) -> StageCheckpoint:
        """
        Create a 'failed' checkpoint.

        WHY: Convenience method for stage failure recording.
        PERFORMANCE: O(1) checkpoint creation.

        Args:
            card_id: Pipeline card ID
            stage_name: Name of stage
            error: Error message
            started_at: Original start timestamp
            result: Partial result data if any

        Returns:
            StageCheckpoint with status='failed'
        """
        if result is None:
            result = {}

        return CheckpointManager.create_checkpoint(
            card_id=card_id,
            stage_name=stage_name,
            status='failed',
            result=result,
            error=error,
            started_at=started_at,
            completed_at=datetime.utcnow().isoformat() + 'Z'
        )

    @staticmethod
    def validate_checkpoint(checkpoint: StageCheckpoint) -> bool:
        """
        Validate checkpoint data.

        WHY: Ensures checkpoint has required fields and valid status.
        PERFORMANCE: O(1) validation checks.

        Args:
            checkpoint: Checkpoint to validate

        Returns:
            True if valid, False otherwise
        """
        # Early return guard clause - missing required fields
        if not checkpoint.card_id or not checkpoint.stage_name:
            return False

        # Early return guard clause - invalid status
        valid_statuses = {'started', 'completed', 'failed'}
        if checkpoint.status not in valid_statuses:
            return False

        # Early return guard clause - completed/failed should have completion time
        if checkpoint.status in {'completed', 'failed'}:
            if not checkpoint.completed_at:
                return False

        # Early return guard clause - failed should have error message
        if checkpoint.status == 'failed':
            if not checkpoint.error:
                return False

        # All checks passed
        return True

    @staticmethod
    def is_terminal_status(status: str) -> bool:
        """
        Check if status is terminal (completed or failed).

        WHY: Determines if checkpoint represents final stage state.
        PERFORMANCE: O(1) set membership check.

        Args:
            status: Checkpoint status

        Returns:
            True if terminal status, False otherwise
        """
        return status in {'completed', 'failed'}

    @staticmethod
    def calculate_duration(checkpoint: StageCheckpoint) -> Optional[float]:
        """
        Calculate checkpoint duration in seconds.

        WHY: Provides stage execution time for metrics and analysis.
        PERFORMANCE: O(1) datetime arithmetic.

        Args:
            checkpoint: Checkpoint to calculate duration for

        Returns:
            Duration in seconds if completed, None otherwise
        """
        # Early return guard clause - no completion time
        if not checkpoint.completed_at:
            return None

        # Parse timestamps
        try:
            started = datetime.fromisoformat(checkpoint.started_at.rstrip('Z'))
            completed = datetime.fromisoformat(checkpoint.completed_at.rstrip('Z'))
            duration = (completed - started).total_seconds()
            return duration
        except (ValueError, AttributeError):
            return None
