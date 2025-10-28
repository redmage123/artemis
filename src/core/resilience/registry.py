#!/usr/bin/env python3
"""
Module: core.resilience.registry

WHY: Manages multiple circuit breakers with global registry pattern
RESPONSIBILITY: Circuit breaker lifecycle, centralized monitoring
PATTERNS: Registry Pattern, Singleton Pattern (global instance), Factory Pattern

Architecture:
    - Registry of named circuit breakers
    - Factory method for get-or-create
    - Centralized status monitoring
    - Thread-safe operations

Design Decisions:
    - Global registry instance for convenience
    - Thread-safe via Lock
    - Factory pattern for circuit breaker creation
    - Bulk operations (reset_all, get_all_statuses)
"""

from typing import Optional, Dict, List
from threading import Lock
import logging

from core.resilience.models import CircuitBreakerConfig
from core.resilience.circuit_breaker_core import CircuitBreaker


class CircuitBreakerRegistry:
    """
    Registry for managing multiple circuit breakers.

    WHY: Centralized management and monitoring of all circuit breakers

    Usage:
        registry = CircuitBreakerRegistry()

        rag_breaker = registry.get_or_create("rag_agent")
        kg_breaker = registry.get_or_create("knowledge_graph")

        # Get all statuses
        statuses = registry.get_all_statuses()
    """

    def __init__(self):
        """Initialize empty registry."""
        self.breakers: Dict[str, CircuitBreaker] = {}
        self.logger = logging.getLogger("CircuitBreakerRegistry")
        self._lock = Lock()

    def get_or_create(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None
    ) -> CircuitBreaker:
        """
        Get existing circuit breaker or create new one.

        WHY: Factory pattern with guard clause for existing breakers

        Args:
            name: Circuit breaker name
            config: Configuration (optional)

        Returns:
            CircuitBreaker instance
        """
        with self._lock:
            # Guard clause: breaker already exists
            if name in self.breakers:
                return self.breakers[name]

            # Create new breaker
            self.breakers[name] = CircuitBreaker(name, config)
            self.logger.info(f"Created circuit breaker: {name}")
            return self.breakers[name]

    def get(self, name: str) -> Optional[CircuitBreaker]:
        """
        Get circuit breaker by name.

        Args:
            name: Circuit breaker name

        Returns:
            CircuitBreaker instance or None
        """
        return self.breakers.get(name)

    def reset_all(self):
        """Reset all circuit breakers to closed state."""
        with self._lock:
            for breaker in self.breakers.values():
                breaker.reset()
            self.logger.info("Reset all circuit breakers")

    def get_all_statuses(self) -> Dict[str, dict]:
        """
        Get status of all circuit breakers.

        Returns:
            Dictionary mapping names to status dictionaries
        """
        with self._lock:
            return {
                name: breaker.get_status()
                for name, breaker in self.breakers.items()
            }

    def get_open_breakers(self) -> List[str]:
        """
        Get names of all open circuit breakers.

        Returns:
            List of circuit breaker names in OPEN state
        """
        with self._lock:
            statuses = [
                name for name, breaker in self.breakers.items()
                if breaker.state == "open"
            ]
            return statuses

    def get_failing_breakers(self) -> List[str]:
        """
        Get names of circuit breakers with failures.

        Returns:
            List of circuit breaker names with failure_count > 0
        """
        with self._lock:
            return [
                name for name, breaker in self.breakers.items()
                if breaker.failure_count > 0
            ]


# ============================================================================
# Global Registry and Convenience Functions
# ============================================================================

_global_registry = CircuitBreakerRegistry()


def get_circuit_breaker(
    name: str,
    config: Optional[CircuitBreakerConfig] = None
) -> CircuitBreaker:
    """
    Get or create a circuit breaker from global registry.

    Args:
        name: Circuit breaker name
        config: Configuration (optional)

    Returns:
        CircuitBreaker instance

    Example:
        breaker = get_circuit_breaker("rag_agent")

        @breaker.protect
        def query_rag():
            return rag.query(...)
    """
    return _global_registry.get_or_create(name, config)


def get_all_circuit_breaker_statuses() -> Dict[str, dict]:
    """
    Get status of all circuit breakers.

    Returns:
        Dictionary mapping names to status dictionaries
    """
    return _global_registry.get_all_statuses()


def reset_all_circuit_breakers():
    """Reset all circuit breakers to closed state."""
    _global_registry.reset_all()


def get_registry() -> CircuitBreakerRegistry:
    """
    Get global registry instance.

    Returns:
        Global CircuitBreakerRegistry
    """
    return _global_registry
