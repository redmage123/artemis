#!/usr/bin/env python3
"""
WHY: Provide circuit breaker management for pipeline stages to prevent cascading failures
RESPONSIBILITY: Export circuit breaker models and manager for supervisor integration
PATTERNS: Circuit Breaker (fault tolerance), Strategy (recovery policies)

This package implements circuit breaker pattern for stage health management:
- CLOSED: Normal operation, requests pass through
- OPEN: Too many failures, reject immediately
- HALF_OPEN: Testing recovery, allow one request

Example:
    from supervisor.circuit_breaker import CircuitBreakerManager, RecoveryStrategy

    manager = CircuitBreakerManager(logger)
    manager.register_stage("stage1", RecoveryStrategy(circuit_breaker_threshold=3))

    # Before executing stage
    if manager.check_circuit("stage1"):
        # Circuit open - skip execution
        pass
    else:
        # Execute stage
        try:
            result = execute_stage()
            manager.record_success("stage1", duration=1.5)
        except Exception:
            manager.record_failure("stage1")
"""

from supervisor.circuit_breaker.models import (
    StageHealth,
    RecoveryStrategy,
    CircuitState
)
from supervisor.circuit_breaker.manager import CircuitBreakerManager

__all__ = [
    'StageHealth',
    'RecoveryStrategy',
    'CircuitState',
    'CircuitBreakerManager'
]
