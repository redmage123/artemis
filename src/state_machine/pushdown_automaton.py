#!/usr/bin/env python3
"""
WHY: Provide state stack for rollback and backtracking capabilities
RESPONSIBILITY: Implement pushdown automaton with state stack management
PATTERNS: Pushdown automaton, memento pattern for state snapshots
"""

from datetime import datetime
from typing import Dict, Any, Optional, List

from state_machine.pipeline_state import PipelineState


class PushdownAutomaton:
    """
    Pushdown automaton for state stack management

    Features:
    - State stack with context
    - Backtracking and rollback
    - Stack depth tracking
    - State search and navigation
    """

    def __init__(self, verbose: bool = True) -> None:
        """
        Initialize pushdown automaton

        Args:
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        self._state_stack: List[Dict[str, Any]] = []

    def push_state(
        self,
        state: PipelineState,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Push state onto stack

        Enables backtracking and rollback by maintaining state stack

        Args:
            state: State to push
            context: Optional context for this state
        """
        self._state_stack.append({
            "state": state,
            "timestamp": datetime.now(),
            "context": context or {}
        })

        if self.verbose:
            print(f"[PushdownAutomaton] Pushed state: {state.value} (depth: {len(self._state_stack)})")

    def pop_state(self) -> Optional[Dict[str, Any]]:
        """
        Pop state from stack

        Returns:
            Previous state and context, or None if stack is empty
        """
        # Guard: Check stack not empty
        if not self._state_stack:
            return None

        popped = self._state_stack.pop()

        if self.verbose:
            print(f"[PushdownAutomaton] Popped state: {popped['state'].value} (depth: {len(self._state_stack)})")

        return popped

    def peek_state(self) -> Optional[Dict[str, Any]]:
        """
        Peek at top of state stack without removing

        Returns:
            Top state and context, or None if stack is empty
        """
        # Guard: Check stack not empty
        if not self._state_stack:
            return None

        return self._state_stack[-1]

    def rollback_to_state(self, target_state: PipelineState) -> Optional[List[Dict[str, Any]]]:
        """
        Find rollback path to a previous state

        Args:
            target_state: State to rollback to

        Returns:
            List of states to pop (rollback path), or None if state not found
        """
        rollback_steps = self._find_rollback_path(target_state)

        # Guard: Check target state exists in stack
        if not rollback_steps:
            self._log_state_not_found(target_state)
            return None

        self._execute_rollback(rollback_steps, target_state)
        return rollback_steps

    def _find_rollback_path(self, target_state: PipelineState) -> List[Dict[str, Any]]:
        """Find path to rollback to target state"""
        rollback_steps = []

        for i in range(len(self._state_stack) - 1, -1, -1):
            state_info = self._state_stack[i]
            rollback_steps.append(state_info)

            if state_info["state"] == target_state:
                return rollback_steps

        return []

    def _execute_rollback(
        self,
        rollback_steps: List[Dict[str, Any]],
        target_state: PipelineState
    ) -> None:
        """Execute the rollback to target state"""
        if self.verbose:
            print(f"[PushdownAutomaton] Rolling back {len(rollback_steps)} states to {target_state.value}")

        # Pop all states until target
        for _ in range(len(rollback_steps) - 1):
            self.pop_state()

    def _log_state_not_found(self, target_state: PipelineState) -> None:
        """Log warning when target state not in stack"""
        if self.verbose:
            print(f"[PushdownAutomaton] ⚠️  State {target_state.value} not found in stack")

    def get_depth(self) -> int:
        """
        Get current depth of state stack

        Returns:
            Number of states on stack
        """
        return len(self._state_stack)

    def clear_stack(self) -> None:
        """Clear the entire state stack"""
        self._state_stack.clear()
        if self.verbose:
            print(f"[PushdownAutomaton] Stack cleared")

    def get_stack_snapshot(self) -> List[Dict[str, Any]]:
        """
        Get snapshot of entire state stack

        Returns:
            Copy of state stack
        """
        return [
            {
                "state": entry["state"],
                "timestamp": entry["timestamp"],
                "context": entry["context"].copy()
            }
            for entry in self._state_stack
        ]
