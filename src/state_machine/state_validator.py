#!/usr/bin/env python3
"""
WHY: Validate state transitions according to pipeline state machine rules
RESPONSIBILITY: Define and enforce valid state transition rules for pipeline safety
PATTERNS: Strategy pattern for validation, guard clauses for early exit
"""

from typing import Dict, Set

from state_machine.pipeline_state import PipelineState


class StateValidator:
    """
    Validates state transitions according to pipeline state machine rules

    Features:
    - Declarative transition rules
    - Fast O(1) validation lookup
    - Immutable rule set for thread safety
    """

    def __init__(self) -> None:
        """Initialize validator with transition rules"""
        self.transition_rules = self._build_transition_rules()

    def _build_transition_rules(self) -> Dict[PipelineState, Set[PipelineState]]:
        """
        Build valid state transition rules

        Returns:
            Map of state → valid next states
        """
        return {
            PipelineState.IDLE: {
                PipelineState.INITIALIZING,
                PipelineState.ABORTED
            },
            PipelineState.INITIALIZING: {
                PipelineState.RUNNING,
                PipelineState.FAILED,
                PipelineState.ABORTED
            },
            PipelineState.RUNNING: {
                PipelineState.STAGE_RUNNING,
                PipelineState.PAUSED,
                PipelineState.COMPLETED,
                PipelineState.FAILED,
                PipelineState.DEGRADED,
                PipelineState.ABORTED
            },
            PipelineState.STAGE_RUNNING: {
                PipelineState.STAGE_COMPLETED,
                PipelineState.STAGE_FAILED,
                PipelineState.STAGE_RETRYING,
                PipelineState.STAGE_SKIPPED,
                PipelineState.RUNNING
            },
            PipelineState.STAGE_FAILED: {
                PipelineState.STAGE_RETRYING,
                PipelineState.RECOVERING,
                PipelineState.FAILED,
                PipelineState.ROLLING_BACK
            },
            PipelineState.RECOVERING: {
                PipelineState.RUNNING,
                PipelineState.DEGRADED,
                PipelineState.FAILED,
                PipelineState.ROLLING_BACK
            },
            PipelineState.DEGRADED: {
                PipelineState.RUNNING,
                PipelineState.COMPLETED,
                PipelineState.FAILED
            },
            PipelineState.PAUSED: {
                PipelineState.RUNNING,
                PipelineState.ABORTED
            },
            PipelineState.ROLLING_BACK: {
                PipelineState.FAILED,
                PipelineState.ABORTED
            },
            PipelineState.FAILED: {
                PipelineState.RECOVERING,
                PipelineState.ROLLING_BACK,
                PipelineState.ABORTED
            },
            # Terminal states
            PipelineState.COMPLETED: set(),
            PipelineState.ABORTED: set()
        }

    def is_valid_transition(
        self,
        from_state: PipelineState,
        to_state: PipelineState
    ) -> bool:
        """
        Check if a state transition is valid

        Args:
            from_state: Current state
            to_state: Desired next state

        Returns:
            True if transition is allowed
        """
        # Same-state transitions are always valid (idempotent)
        if to_state == from_state:
            return True

        # Check transition rules
        valid_next_states = self.transition_rules.get(from_state, set())
        return to_state in valid_next_states
