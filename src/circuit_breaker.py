#!/usr/bin/env python3
"""
Module: circuit_breaker.py

BACKWARD COMPATIBILITY WRAPPER

WHY: Maintains API compatibility while delegating to core.resilience package
RESPONSIBILITY: Re-export all public APIs from core.resilience
PATTERNS: Facade Pattern, Proxy Pattern

This module is a compatibility shim that re-exports the entire circuit breaker
API from the modular core.resilience package. All functionality has been
refactored into focused, single-responsibility modules:

Architecture (core.resilience):
    models.py - States, config, exceptions (~60 lines)
    state_machine.py - State transitions (~240 lines)
    failure_detector.py - Request validation (~70 lines)
    recovery_handler.py - Success/failure handling (~100 lines)
    circuit_breaker_core.py - Main facade (~240 lines)
    registry.py - Global registry (~180 lines)
    cli_demo.py - CLI interface (~150 lines)

Migration Guide:
    OLD: from circuit_breaker import CircuitBreaker
    NEW: from core.resilience import CircuitBreaker

    Both work identically - this wrapper ensures backward compatibility.

Usage Patterns (unchanged):
    1. Decorator:
        breaker = CircuitBreaker("service")
        @breaker.protect
        def func(): ...

    2. Context manager:
        with breaker:
            result = risky_call()

    3. Direct call:
        result = breaker.call(func, *args)

    4. Global registry:
        breaker = get_circuit_breaker("service")

Design Decisions:
    - Full backward compatibility (all imports work)
    - Zero changes required to existing code
    - CLI interface preserved (--demo, --status)
    - Performance identical (thin wrapper, no overhead)
"""

# Re-export all public APIs from core.resilience
from core.resilience import (
    # Models and exceptions
    CircuitState,
    CircuitBreakerConfig,
    CircuitBreakerOpenError,

    # Core components (for advanced usage)
    StateMachine,
    FailureDetector,
    RecoveryHandler,

    # Main circuit breaker
    CircuitBreaker,

    # Registry and convenience functions
    CircuitBreakerRegistry,
    get_circuit_breaker,
    get_all_circuit_breaker_statuses,
    reset_all_circuit_breakers,
    get_registry,
)

# Private registry reference for backward compatibility
_global_registry = get_registry()


# ============================================================================
# CLI INTERFACE (unchanged)
# ============================================================================

if __name__ == "__main__":
    from core.resilience.cli_demo import main
    main()
