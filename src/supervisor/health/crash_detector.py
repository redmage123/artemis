#!/usr/bin/env python3
"""
WHY: Detect agent crashes via state machine monitoring
RESPONSIBILITY: Monitor state machine for FAILED states and extract crash information
PATTERNS: Observer (state monitoring), Strategy (state machine integration)
"""

from datetime import datetime
from typing import Any, Dict, Optional


class CrashDetector:
    """
    WHY: Separate crash detection logic from general health monitoring
    RESPONSIBILITY: Monitor state machine for FAILED states, extract crash details
    PATTERNS: Observer, Strategy
    """

    def __init__(self, state_machine: Optional[Any] = None):
        """
        WHY: Initialize crash detector with optional state machine
        RESPONSIBILITY: Setup state machine integration
        PATTERNS: Dependency injection (state_machine)

        Args:
            state_machine: Optional ArtemisStateMachine for crash detection
        """
        self.state_machine = state_machine
        self.stats = {
            "crashes_detected": 0
        }

    def detect_crash(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """
        WHY: Check if agent has crashed
        RESPONSIBILITY: Query state machine for FAILED state
        PATTERNS: Guard clause (early return)

        Args:
            agent_name: Name of the agent

        Returns:
            Crash info dict if crashed, None otherwise
        """
        if not self.state_machine:
            return None

        return self._check_state_machine_crash(agent_name)

    def _check_state_machine_crash(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """
        WHY: Extract crash details from state machine
        RESPONSIBILITY: Query current state and context for error information
        PATTERNS: Guard clause

        Args:
            agent_name: Name of the agent

        Returns:
            Crash info dict if crashed, None otherwise
        """
        current_state = self.state_machine.get_current_state()

        if not current_state or "FAILED" not in str(current_state):
            return None

        # Get error details from context
        context = getattr(self.state_machine, 'context', {})
        error_info = context.get("error", {})

        crash_info = {
            "agent_name": agent_name,
            "error": error_info.get("message", "Unknown error"),
            "error_type": error_info.get("type", "Unknown"),
            "traceback": context.get("traceback", ""),
            "state": str(current_state)
        }

        self.stats["crashes_detected"] += 1
        return crash_info

    def check_for_crash_event(self) -> Optional[Dict[str, Any]]:
        """
        WHY: Check for crash without specific agent name
        RESPONSIBILITY: Query state machine and extract agent name from context
        PATTERNS: Guard clause

        Returns:
            Crash info dict with agent_name if crashed, None otherwise
        """
        if not self.state_machine:
            return None

        current_state = self.state_machine.get_current_state()

        if not current_state or "FAILED" not in str(current_state):
            return None

        context = getattr(self.state_machine, 'context', {})
        error_info = context.get("error", {})

        crash_info = {
            "agent_name": context.get("stage_name", "unknown"),
            "error": error_info.get("message", "Unknown error"),
            "error_type": error_info.get("type", "Unknown"),
            "traceback": context.get("traceback", ""),
            "state": str(current_state),
            "context": context
        }

        self.stats["crashes_detected"] += 1
        return crash_info

    def set_state_machine(self, state_machine: Any) -> None:
        """
        WHY: Allow late binding of state machine
        RESPONSIBILITY: Update state machine reference
        """
        self.state_machine = state_machine
