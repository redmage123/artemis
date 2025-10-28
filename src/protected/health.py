#!/usr/bin/env python3
"""
WHY: Health check utilities for protected components
RESPONSIBILITY: Aggregate circuit breaker status across all protected components
PATTERNS: Facade (simplified health check API)

Health utilities provide system-wide view of circuit breaker states.
"""

from typing import Dict, Any


def check_all_protected_components() -> Dict[str, Dict[str, Any]]:
    """
    Check health of all protected components.

    WHY: System-wide health visibility for monitoring and debugging.

    Returns:
        Dict of component statuses

    Example:
        >>> statuses = check_all_protected_components()
        >>> statuses["rag_agent"]["state"]
        'CLOSED'
    """
    from circuit_breaker import get_all_circuit_breaker_statuses
    return get_all_circuit_breaker_statuses()


def reset_all_circuit_breakers():
    """
    Reset all circuit breakers to closed state.

    WHY: Manual recovery after fixing underlying service issues.

    Example:
        >>> reset_all_circuit_breakers()
        # All circuits reset to CLOSED
    """
    from circuit_breaker import reset_all_circuit_breakers
    reset_all_circuit_breakers()
