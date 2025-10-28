#!/usr/bin/env python3
"""
Module: core.resilience.circuit_breaker_core

WHY: Main circuit breaker implementation with decorator and context manager support
RESPONSIBILITY: Coordinate state machine, failure detector, and recovery handler
PATTERNS: Facade Pattern, Decorator Pattern, Context Manager, Composition

Architecture:
    - Facade over state machine, detector, and recovery handler
    - Decorator pattern for function protection
    - Context manager for block protection
    - Thread-safe via internal lock

Design Decisions:
    - Composition over inheritance (uses state machine, detector, handler)
    - Decorator and context manager for flexible usage
    - Type hints for type safety
    - Guard clauses for clean control flow
"""

from typing import Callable, Any, Optional, TypeVar
from functools import wraps
from threading import Lock
import logging

from core.resilience.models import CircuitBreakerConfig, CircuitBreakerOpenError
from core.resilience.state_machine import StateMachine
from core.resilience.failure_detector import FailureDetector
from core.resilience.recovery_handler import RecoveryHandler


T = TypeVar('T')


class CircuitBreaker:
    """
    Circuit breaker to prevent cascading failures.

    WHY: Facade pattern coordinates all circuit breaker components

    States:
        CLOSED: Normal operation, all requests go through
        OPEN: Too many failures, reject all requests immediately
        HALF_OPEN: Testing recovery, allow limited requests

    Usage:
        breaker = CircuitBreaker("rag_agent")

        @breaker.protect
        def query_rag(text):
            return rag.query(text)

        try:
            result = query_rag("test")
        except CircuitBreakerOpenError:
            result = use_fallback()

    Context manager usage:
        with breaker:
            result = expensive_api_call()
    """

    def __init__(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize circuit breaker.

        Args:
            name: Name of the protected component
            config: Circuit breaker configuration
            logger: Logger instance
        """
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.logger = logger or logging.getLogger(f"CircuitBreaker.{name}")

        # Thread safety
        self._lock = Lock()

        # Initialize components
        self.state_machine = StateMachine(
            name=name,
            failure_threshold=self.config.failure_threshold,
            success_threshold=self.config.success_threshold,
            timeout_seconds=self.config.timeout_seconds,
            lock=self._lock,
            logger=self.logger
        )

        self.failure_detector = FailureDetector(
            name=name,
            state_machine=self.state_machine
        )

        self.recovery_handler = RecoveryHandler(
            name=name,
            state_machine=self.state_machine,
            logger=self.logger
        )

    def protect(self, func: Callable[..., T]) -> Callable[..., T]:
        """
        Decorator to protect a function with circuit breaker.

        Args:
            func: Function to protect

        Returns:
            Wrapped function

        Example:
            @breaker.protect
            def risky_operation():
                return call_external_service()
        """
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            return self.call(func, *args, **kwargs)
        return wrapper

    def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """
        Execute function with circuit breaker protection.

        WHY: Guard clauses with early execution pattern

        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            CircuitBreakerOpenError: If circuit is open
        """
        # Check if request allowed (raises if not)
        self.failure_detector.check_before_request()

        # Execute function with success/failure handling
        try:
            result = func(*args, **kwargs)
            self.recovery_handler.handle_success()
            return result
        except Exception as e:
            self.recovery_handler.handle_failure(e)
            raise

    def reset(self):
        """Manually reset circuit breaker to closed state."""
        self.state_machine.reset()

    def get_status(self) -> dict:
        """
        Get circuit breaker status.

        Returns:
            Status dictionary with state, counts, and timestamps
        """
        status = self.state_machine.get_status()
        recovery_status = self.recovery_handler.get_recovery_status()

        return {
            "name": self.name,
            **status,
            **recovery_status
        }

    # ========================================================================
    # Context Manager Support
    # ========================================================================

    def __enter__(self):
        """
        Enter context - check if circuit is open.

        WHY: Reuses failure detector for DRY principle
        """
        self.failure_detector.check_before_request()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit context - record success or failure.

        WHY: Guard clause for clean control flow

        Args:
            exc_type: Exception type (None if success)
            exc_val: Exception value
            exc_tb: Exception traceback

        Returns:
            False (don't suppress exceptions)
        """
        # Guard clause: handle success case
        if exc_type is None:
            self.recovery_handler.handle_success()
            return False

        # Handle failure case
        self.recovery_handler.handle_failure(exc_val)
        return False

    # ========================================================================
    # Property Access for Backward Compatibility
    # ========================================================================

    @property
    def state(self) -> str:
        """Get current state (backward compatibility)."""
        return self.state_machine.state

    @property
    def failure_count(self) -> int:
        """Get failure count (backward compatibility)."""
        return self.state_machine.failure_count

    @property
    def success_count(self) -> int:
        """Get success count (backward compatibility)."""
        return self.state_machine.success_count
