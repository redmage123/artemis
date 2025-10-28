#!/usr/bin/env python3
"""
WHY: Track agent progress via state machine transitions
RESPONSIBILITY: Monitor state transitions, detect stalls and hangs
PATTERNS: Observer (state monitoring), Strategy (transition tracking)
"""

from datetime import datetime
from typing import Any, Dict, Optional


class ProgressTracker:
    """
    WHY: Separate progress tracking from general health monitoring
    RESPONSIBILITY: Monitor state transitions, calculate elapsed time, detect stalls/hangs
    PATTERNS: Observer, Strategy
    """

    def __init__(self, state_machine: Optional[Any] = None):
        """
        WHY: Initialize progress tracker with optional state machine
        RESPONSIBILITY: Setup state machine integration
        PATTERNS: Dependency injection

        Args:
            state_machine: Optional ArtemisStateMachine for progress tracking
        """
        self.state_machine = state_machine

    def check_progress(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """
        WHY: Check if agent is making progress
        RESPONSIBILITY: Query state machine for transition information
        PATTERNS: Guard clause

        Args:
            agent_name: Name of the agent

        Returns:
            Progress info dict if available, None otherwise
        """
        if not self.state_machine or not hasattr(self.state_machine, 'context'):
            return None

        return self._get_transition_progress(agent_name)

    def _get_transition_progress(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """
        WHY: Extract progress from state transitions
        RESPONSIBILITY: Query context for last transition time
        PATTERNS: Guard clause

        Args:
            agent_name: Name of the agent

        Returns:
            Progress info dict if available, None otherwise
        """
        context = self.state_machine.context
        last_transition = context.get("last_transition_time")

        if not last_transition:
            return None

        return {
            "agent_name": agent_name,
            "last_transition": last_transition,
            "current_state": str(self.state_machine.get_current_state())
        }

    def get_elapsed_since_transition(self) -> Optional[float]:
        """
        WHY: Calculate time since last state transition
        RESPONSIBILITY: Query context and calculate elapsed time
        PATTERNS: Guard clause

        Returns:
            Elapsed seconds since last transition, None if no transition
        """
        if not self.state_machine or not hasattr(self.state_machine, 'context'):
            return None

        context = self.state_machine.context
        last_transition = context.get("last_transition_time")

        if not last_transition:
            return None

        return self._calculate_elapsed_time(last_transition)

    def _calculate_elapsed_time(self, last_transition: Any) -> float:
        """
        WHY: Convert transition time to elapsed seconds
        RESPONSIBILITY: Handle string or datetime conversion
        PATTERNS: Guard clause (type checking)

        Args:
            last_transition: Transition time (string or datetime)

        Returns:
            Elapsed seconds
        """
        if isinstance(last_transition, str):
            last_transition = datetime.fromisoformat(last_transition)

        return (datetime.now() - last_transition).total_seconds()

    def check_hang_or_stall(
        self,
        timeout_seconds: int
    ) -> Optional[Dict[str, Any]]:
        """
        WHY: Detect hung or stalled agents
        RESPONSIBILITY: Compare elapsed time to thresholds
        PATTERNS: Guard clause, Dispatch table (hung vs stalled)

        Args:
            timeout_seconds: Timeout threshold for hung detection

        Returns:
            Dict with event type and data, or None if healthy
        """
        if not self.state_machine or not hasattr(self.state_machine, 'context'):
            return None

        context = self.state_machine.context
        last_transition = context.get("last_transition_time")

        if not last_transition:
            return None

        elapsed = self._calculate_elapsed_time(last_transition)
        stage_name = context.get("stage_name", "unknown")

        # Check thresholds
        if elapsed > timeout_seconds:
            return {
                "event": "hung",
                "stage_name": stage_name,
                "data": {
                    "timeout_info": {
                        "timeout_seconds": timeout_seconds,
                        "elapsed_time": elapsed
                    }
                }
            }

        if elapsed > (timeout_seconds / 2):
            return {
                "event": "stalled",
                "stage_name": stage_name,
                "data": {"time_since_activity": elapsed}
            }

        return None

    def set_state_machine(self, state_machine: Any) -> None:
        """
        WHY: Allow late binding of state machine
        RESPONSIBILITY: Update state machine reference
        """
        self.state_machine = state_machine
