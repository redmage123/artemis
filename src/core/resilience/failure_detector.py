#!/usr/bin/env python3
"""
Module: core.resilience.failure_detector

WHY: Detects and validates circuit breaker state before request execution
RESPONSIBILITY: Pre-request validation, rejection of requests when circuit open
PATTERNS: Guard Clauses, Early Returns, Exception-based Control Flow

Architecture:
    - State checking before request execution
    - Rejection with detailed error information
    - Time-until-retry calculations

Design Decisions:
    - Raises CircuitBreakerOpenError when circuit open
    - Guard clauses for clean control flow
    - Error includes context for debugging
"""

from typing import Dict, Any
from core.resilience.models import CircuitBreakerOpenError, CircuitState
from core.resilience.state_machine import StateMachine


class FailureDetector:
    """
    Detects when circuit breaker should reject requests.

    WHY: Separates failure detection logic from state machine
    """

    def __init__(self, name: str, state_machine: StateMachine):
        """
        Initialize failure detector.

        Args:
            name: Circuit breaker name
            state_machine: State machine to check
        """
        self.name = name
        self.state_machine = state_machine

    def check_before_request(self):
        """
        Check if request should be allowed.

        WHY: Guard clause with early return for clean flow

        Raises:
            CircuitBreakerOpenError: If circuit is open and not ready
        """
        # Guard clause: request allowed
        if self.state_machine.should_allow_request():
            return

        # Circuit is open - reject request with details
        time_until_retry = self.state_machine.get_time_until_retry()
        context = self._build_error_context(time_until_retry)

        raise CircuitBreakerOpenError(
            f"Circuit breaker '{self.name}' is OPEN. "
            f"Retry in {time_until_retry:.1f} seconds.",
            context=context
        )

    def _build_error_context(self, time_until_retry: float) -> Dict[str, Any]:
        """
        Build error context dictionary.

        WHY: Extracted to keep error handling clean

        Args:
            time_until_retry: Seconds until retry allowed

        Returns:
            Context dictionary
        """
        status = self.state_machine.get_status()
        return {
            "circuit_breaker": self.name,
            "state": status["state"],
            "failure_count": status["failure_count"],
            "time_until_retry": time_until_retry
        }
