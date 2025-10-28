#!/usr/bin/env python3
"""
Module: core.resilience.state_machine

WHY: Manages circuit breaker state transitions using State Pattern
RESPONSIBILITY: Handle state transitions, track counters, enforce state rules
PATTERNS: State Pattern, Guard Clauses, Early Returns

Architecture:
    - StateMachine: Core state transition logic
    - State tracking: failure_count, success_count, timestamps
    - Thread-safe via external lock (injected)

Design Decisions:
    - State Pattern for clean state transition logic
    - Guard clauses for early returns (max 1 level nesting)
    - Timestamps track state changes and failure times
    - Lock passed in (dependency injection) for flexibility
"""

from datetime import datetime, timedelta
from typing import Optional
from threading import Lock
import logging

from core.resilience.models import CircuitState


class StateMachine:
    """
    Circuit breaker state machine.

    WHY: Centralizes state transition logic using State Pattern

    States:
        CLOSED → OPEN (failure_threshold exceeded)
        OPEN → HALF_OPEN (timeout_seconds elapsed)
        HALF_OPEN → CLOSED (success_threshold reached)
        HALF_OPEN → OPEN (any failure)
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int,
        success_threshold: int,
        timeout_seconds: int,
        lock: Lock,
        logger: logging.Logger
    ):
        """
        Initialize state machine.

        Args:
            name: Circuit breaker name
            failure_threshold: Failures before opening
            success_threshold: Successes to close from half-open
            timeout_seconds: Wait time before half-open
            lock: Thread safety lock
            logger: Logger instance
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout_seconds = timeout_seconds
        self.lock = lock
        self.logger = logger

        # State tracking
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.last_state_change: Optional[datetime] = None

    def should_allow_request(self) -> bool:
        """
        Check if request should be allowed.

        WHY: Guard clauses with early returns (max 1 level nesting)

        Returns:
            True if request allowed, False otherwise
        """
        with self.lock:
            # Guard clause: not open, allow request
            if self.state != CircuitState.OPEN:
                return True

            # Guard clause: can attempt reset, transition to half-open
            if self._should_attempt_reset():
                self._transition_to_half_open()
                return True

            # Circuit is open and not ready
            return False

    def record_success(self):
        """
        Record successful execution.

        WHY: Guard clauses eliminate nested ifs
        """
        with self.lock:
            # Guard clause: handle CLOSED state
            if self.state == CircuitState.CLOSED:
                self.failure_count = 0
                return

            # Guard clause: not in HALF_OPEN, nothing to do
            if self.state != CircuitState.HALF_OPEN:
                return

            # Handle HALF_OPEN state
            self.success_count += 1
            self.logger.info(
                f"Circuit breaker {self.name} successful attempt "
                f"({self.success_count}/{self.success_threshold})"
            )

            # Check if enough successes to close
            if self.success_count >= self.success_threshold:
                self._transition_to_closed()

    def record_failure(self):
        """
        Record failed execution.

        WHY: Guard clauses with early returns
        """
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = datetime.now()

            self.logger.warning(
                f"Circuit breaker {self.name} failure "
                f"({self.failure_count}/{self.failure_threshold})"
            )

            # Guard clause: if half-open, reopen immediately
            if self.state == CircuitState.HALF_OPEN:
                self._transition_to_open_from_half_open()
                return

            # Open circuit if threshold exceeded
            if self.failure_count >= self.failure_threshold:
                self._transition_to_open()

    def reset(self):
        """Manually reset state machine to closed state."""
        with self.lock:
            self.logger.info(f"Circuit breaker {self.name} manually reset")
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            self.last_failure_time = None
            self.last_state_change = datetime.now()

    def get_time_until_retry(self) -> float:
        """
        Calculate time until retry allowed (seconds).

        WHY: Guard clause for edge case handling

        Returns:
            Seconds until retry (0.0 if ready now)
        """
        with self.lock:
            # Guard clause: no failure time
            if not self.last_failure_time:
                return 0.0

            # Calculate remaining time
            elapsed = datetime.now() - self.last_failure_time
            timeout = timedelta(seconds=self.timeout_seconds)
            remaining = timeout - elapsed

            return max(0.0, remaining.total_seconds())

    def get_status(self) -> dict:
        """Get current state machine status."""
        with self.lock:
            return {
                "state": self.state,
                "failure_count": self.failure_count,
                "success_count": self.success_count,
                "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
                "last_state_change": self.last_state_change.isoformat() if self.last_state_change else None,
                "time_until_retry": self.get_time_until_retry() if self.state == CircuitState.OPEN else 0.0
            }

    # ========================================================================
    # Private State Transition Methods
    # ========================================================================

    def _should_attempt_reset(self) -> bool:
        """
        Check if timeout elapsed for half-open attempt.

        WHY: Guard clause for early return
        """
        # Guard clause: no failure time
        if not self.last_failure_time:
            return True

        elapsed = datetime.now() - self.last_failure_time
        return elapsed >= timedelta(seconds=self.timeout_seconds)

    def _transition_to_half_open(self):
        """Transition from OPEN to HALF_OPEN."""
        self.logger.info(f"Circuit breaker {self.name} entering HALF_OPEN state")
        self.state = CircuitState.HALF_OPEN
        self.last_state_change = datetime.now()

    def _transition_to_closed(self):
        """Transition from HALF_OPEN to CLOSED after recovery."""
        self.logger.info(f"Circuit breaker {self.name} closing (recovered)")
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_state_change = datetime.now()

    def _transition_to_open(self):
        """Transition from CLOSED to OPEN after threshold."""
        self.logger.error(
            f"Circuit breaker {self.name} opening due to {self.failure_count} failures"
        )
        self.state = CircuitState.OPEN
        self.last_state_change = datetime.now()
        self.success_count = 0

    def _transition_to_open_from_half_open(self):
        """Transition from HALF_OPEN to OPEN after test failure."""
        self.logger.error(
            f"Circuit breaker {self.name} returning to OPEN (half-open test failed)"
        )
        self.state = CircuitState.OPEN
        self.last_state_change = datetime.now()
        self.success_count = 0
