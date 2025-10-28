#!/usr/bin/env python3
"""
Module: core.resilience.recovery_handler

WHY: Handles success/failure recording and recovery strategies
RESPONSIBILITY: Record execution outcomes, manage recovery logic
PATTERNS: Strategy Pattern, Guard Clauses, Callback Pattern

Architecture:
    - Success/failure recording
    - Delegates to state machine for state updates
    - Provides hooks for custom recovery strategies

Design Decisions:
    - Simple delegation to state machine
    - Extensible for future recovery strategies
    - Clear separation from detection logic
"""

from typing import Optional, Callable, Any
import logging

from core.resilience.state_machine import StateMachine


class RecoveryHandler:
    """
    Handles success/failure recording and recovery.

    WHY: Separates recovery logic from detection and state management
    """

    def __init__(
        self,
        name: str,
        state_machine: StateMachine,
        logger: logging.Logger,
        on_success_callback: Optional[Callable[[], None]] = None,
        on_failure_callback: Optional[Callable[[Exception], None]] = None
    ):
        """
        Initialize recovery handler.

        Args:
            name: Circuit breaker name
            state_machine: State machine for recording
            logger: Logger instance
            on_success_callback: Optional callback on success
            on_failure_callback: Optional callback on failure
        """
        self.name = name
        self.state_machine = state_machine
        self.logger = logger
        self.on_success_callback = on_success_callback
        self.on_failure_callback = on_failure_callback

    def handle_success(self):
        """
        Handle successful execution.

        WHY: Guard clause for optional callback
        """
        # Record success in state machine
        self.state_machine.record_success()

        # Guard clause: invoke callback if provided
        if self.on_success_callback:
            try:
                self.on_success_callback()
            except Exception as e:
                self.logger.warning(
                    f"Circuit breaker {self.name} success callback failed: {e}"
                )

    def handle_failure(self, exception: Exception):
        """
        Handle failed execution.

        WHY: Guard clause for optional callback

        Args:
            exception: Exception that occurred
        """
        # Record failure in state machine
        self.state_machine.record_failure()

        # Guard clause: invoke callback if provided
        if self.on_failure_callback:
            try:
                self.on_failure_callback(exception)
            except Exception as e:
                self.logger.warning(
                    f"Circuit breaker {self.name} failure callback failed: {e}"
                )

    def get_recovery_status(self) -> dict:
        """
        Get recovery status.

        Returns:
            Status dictionary
        """
        return {
            "has_success_callback": self.on_success_callback is not None,
            "has_failure_callback": self.on_failure_callback is not None,
        }
