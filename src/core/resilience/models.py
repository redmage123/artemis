#!/usr/bin/env python3
"""
Module: core.resilience.models

WHY: Defines circuit breaker states, configuration, and exceptions
RESPONSIBILITY: Provide type-safe configuration and state constants for circuit breaker
PATTERNS: Value Object (dataclass), Constants (CircuitState)

Architecture:
    - CircuitState: Enum-like constants for circuit breaker states
    - CircuitBreakerConfig: Immutable configuration object
    - CircuitBreakerOpenError: Custom exception for open circuit

Design Decisions:
    - dataclass for config (immutable, type-safe)
    - String constants for states (serialization-friendly)
    - Extends PipelineStageError for consistent exception handling
"""

from dataclasses import dataclass
from artemis_exceptions import PipelineStageError


class CircuitBreakerOpenError(PipelineStageError):
    """Raised when circuit breaker is open (component is failing)"""
    pass


class CircuitState:
    """
    Circuit breaker states.

    WHY: String constants instead of Enum for JSON serialization compatibility
    """
    CLOSED = "closed"          # Normal operation, requests pass through
    OPEN = "open"              # Failing, reject all requests
    HALF_OPEN = "half_open"    # Testing if component recovered


@dataclass
class CircuitBreakerConfig:
    """
    Circuit breaker configuration.

    WHY: Dataclass for type safety and immutability

    Attributes:
        failure_threshold: Number of failures before opening circuit
        timeout_seconds: How long to wait before testing recovery
        half_open_attempts: Number of successful attempts needed to close circuit
        success_threshold: Number of successes needed to close from half-open
    """
    failure_threshold: int = 5
    timeout_seconds: int = 60
    half_open_attempts: int = 1
    success_threshold: int = 2
