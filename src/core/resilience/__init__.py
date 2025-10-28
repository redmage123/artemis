#!/usr/bin/env python3
"""
Package: core.resilience

WHY: Circuit breaker pattern implementation for fault tolerance and resilience
RESPONSIBILITY: Prevent cascading failures, protect external service calls
PATTERNS: Circuit Breaker, State Pattern, Facade, Registry

Architecture:
    core.resilience/
        models.py - Circuit breaker states, config, exceptions
        state_machine.py - State transitions (CLOSED/OPEN/HALF_OPEN)
        failure_detector.py - Pre-request validation
        recovery_handler.py - Success/failure recording
        circuit_breaker_core.py - Main circuit breaker facade
        registry.py - Global circuit breaker registry

Key Concepts:
    - Three-state circuit: CLOSED → OPEN → HALF_OPEN → CLOSED
    - Failure counting and threshold detection
    - Timeout-based auto-recovery
    - Thread-safe state management
    - Decorator and context manager support

Usage:
    from core.resilience import CircuitBreaker, get_circuit_breaker

    # Direct instantiation
    breaker = CircuitBreaker("service_name")

    @breaker.protect
    def risky_call():
        return external_service.call()

    # Global registry
    breaker = get_circuit_breaker("service_name")

    with breaker:
        result = expensive_operation()

Backward Compatibility:
    All exports maintain compatibility with circuit_breaker.py
"""

# Core components
from core.resilience.models import (
    CircuitState,
    CircuitBreakerConfig,
    CircuitBreakerOpenError
)
from core.resilience.state_machine import StateMachine
from core.resilience.failure_detector import FailureDetector
from core.resilience.recovery_handler import RecoveryHandler
from core.resilience.circuit_breaker_core import CircuitBreaker

# Registry and convenience functions
from core.resilience.registry import (
    CircuitBreakerRegistry,
    get_circuit_breaker,
    get_all_circuit_breaker_statuses,
    reset_all_circuit_breakers,
    get_registry
)

# Public API
__all__ = [
    # Models
    "CircuitState",
    "CircuitBreakerConfig",
    "CircuitBreakerOpenError",
    # Components
    "StateMachine",
    "FailureDetector",
    "RecoveryHandler",
    "CircuitBreaker",
    # Registry
    "CircuitBreakerRegistry",
    "get_circuit_breaker",
    "get_all_circuit_breaker_statuses",
    "reset_all_circuit_breakers",
    "get_registry",
]
