"""
Module: two_pass/rollback.py

WHY: Rollback mechanism for two-pass pipeline failures.
RESPONSIBILITY: RollbackManager for state restoration.
PATTERNS: Memento Pattern, Command Pattern, Guard Clauses, Observer Pattern.

This module handles:
- Restore state from memento on second pass failure
- Validate rollback safety
- Emit rollback events

EXTRACTED FROM: two_pass_pipeline.py (lines 1242-1404, 163 lines)
"""

from typing import Optional, Dict, Any, List

from two_pass.models import PassMemento, PassDelta
from two_pass.events import TwoPassEventType
from two_pass.exceptions import RollbackException
from artemis_exceptions import wrap_exception
from artemis_services import PipelineLogger
from pipeline_observer import PipelineObservable, PipelineEvent, EventType

class RollbackManager:
    """
    Manages rollback to first pass when second pass fails or degrades quality.

    Why it exists: Provides safety net when second pass makes things worse.
    Preserves system stability by restoring known-good state.

    Design pattern: Memento Pattern + Command Pattern
    Why this design: Memento provides state snapshot, Command provides undo operation.

    Responsibilities:
    - Restore state from memento
    - Validate rollback success
    - Emit rollback events
    - Preserve rollback history
    - Support partial rollback (selective artifact restoration)

    Use cases:
    - Second pass degrades quality score
    - Second pass introduces errors
    - Second pass exceeds resource limits
    - User-initiated rollback
    """

    def __init__(self, observable: Optional[PipelineObservable] = None, verbose: bool = True):
        """Initialize rollback manager with observer integration"""
        self.observable = observable
        self.verbose = verbose
        self.logger = PipelineLogger(verbose=verbose)
        self.rollback_history: List[Dict[str, Any]] = []

    @wrap_exception(RollbackException, "Rollback operation failed")
    def rollback_to_memento(
        self,
        memento: PassMemento,
        reason: str = "Second pass failed"
    ) -> Dict[str, Any]:
        """
        Rollback to state captured in memento.

        What it does:
        1. Emit rollback initiated event
        2. Restore state from memento
        3. Validate restoration
        4. Record rollback in history
        5. Emit rollback completed event
        6. Return restored state

        Args:
            memento: State snapshot to restore
            reason: Human-readable reason for rollback

        Returns:
            Restored state dict

        Raises:
            RollbackException: On restoration failure

        Design note: Creates deep copy of memento state to prevent mutations
        from affecting stored memento.
        """
        self._emit_event(
            TwoPassEventType.ROLLBACK_INITIATED,
            {
                "memento_pass": memento.pass_name,
                "reason": reason,
                "quality_score": memento.quality_score
            }
        )

        # Restore state - deep copy to prevent mutation
        restored_state = copy.deepcopy(memento.state)

        # Validate restoration
        if not self._validate_restoration(restored_state, memento):
            raise RollbackException("Restored state validation failed")

        # Record rollback in history
        self.rollback_history.append({
            "timestamp": datetime.now().isoformat(),
            "memento_pass": memento.pass_name,
            "reason": reason,
            "quality_score": memento.quality_score
        })

        self._emit_event(
            TwoPassEventType.ROLLBACK_COMPLETED,
            {
                "memento_pass": memento.pass_name,
                "artifacts_restored": len(memento.artifacts)
            }
        )

        return restored_state

    def _validate_restoration(self, state: Dict[str, Any], memento: PassMemento) -> bool:
        """
        Validate that restoration succeeded.

        Why needed: Verifies state was correctly restored from memento.
        Prevents silent failures where rollback appears to succeed but state is corrupted.

        Args:
            state: Restored state
            memento: Original memento

        Returns:
            True if validation passes, False otherwise
        """
        # Guard clause - state must not be empty
        if not state:
            return False

        # Verify key memento fields are preserved
        required_keys = ["artifacts", "learnings", "insights"]
        return all(key in state or key in memento.__dict__ for key in required_keys)

    def should_rollback(self, delta: PassDelta, threshold: float = -0.1) -> bool:
        """
        Determine if rollback is needed based on quality delta.

        Why needed: Automated rollback decision based on objective quality metrics.
        Prevents manual intervention for obvious degradations.

        Args:
            delta: PassDelta from comparison
            threshold: Minimum quality degradation to trigger rollback (default -10%)

        Returns:
            True if rollback recommended, False otherwise

        Design note: Uses negative threshold because degradation is negative delta.
        Only rolls back on significant degradation (10%+) to avoid noise.
        """
        # Rollback if quality degraded significantly
        return delta.quality_delta < threshold

    def get_rollback_history(self) -> List[Dict[str, Any]]:
        """Get rollback history for audit trail"""
        return self.rollback_history.copy()

    def _emit_event(self, event_type: TwoPassEventType, data: Dict[str, Any]) -> None:
        """Emit event to observers (helper method)"""
        # Guard clause - early return if no observable
        if not self.observable:
            return

        event = PipelineEvent(
            event_type=EventType.STAGE_PROGRESS,
            stage_name="RollbackManager",
            data={
                "two_pass_event": event_type.value,
                **data
            }
        )

        self.observable.notify(event)


# ============================================================================
# TWO-PASS PIPELINE ORCHESTRATOR
# ============================================================================


__all__ = ['RollbackManager']
