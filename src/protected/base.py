#!/usr/bin/env python3
"""
WHY: Provide base class for circuit-breaker-protected components
RESPONSIBILITY: Common initialization and error handling for protected wrappers
PATTERNS: Template Method, Delegation (__getattr__)

Base protected component eliminates duplication across RAG, LLM, and KG wrappers.
"""

from typing import Any, Dict, Optional
import logging
from circuit_breaker import CircuitBreaker, CircuitBreakerConfig, get_circuit_breaker


class BaseProtectedComponent:
    """
    Base class for circuit-breaker-protected components.

    WHY: All protected components share circuit breaker initialization and delegation.
    RESPONSIBILITY: Provide template for protected wrappers.
    PATTERNS: Template Method, Delegation.
    """

    def __init__(
        self,
        component_name: str,
        config: CircuitBreakerConfig,
        fallback_mode: bool,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize base protected component.

        Args:
            component_name: Name for circuit breaker
            config: Circuit breaker configuration
            fallback_mode: Enable fallback behavior
            logger: Optional logger
        """
        self.component_name = component_name
        self.fallback_mode = fallback_mode
        self.logger = logger or logging.getLogger(f"Protected{component_name}")

        # Create circuit breaker
        self.breaker = get_circuit_breaker(component_name, config)

        # Underlying component (set by subclass)
        self._component = None

    def get_circuit_status(self) -> Dict[str, Any]:
        """
        Get circuit breaker status.

        Returns:
            Circuit breaker status dict
        """
        return self.breaker.get_status()

    def __getattr__(self, name):
        """
        Delegate unknown methods to underlying component.

        WHY: Transparent wrapper - exposes all component methods.

        Args:
            name: Method name

        Returns:
            Method from underlying component
        """
        # Guard clause - component must exist
        if self._component is None:
            return self._handle_unavailable_component(name)

        return getattr(self._component, name)

    def _handle_unavailable_component(self, method_name: str):
        """
        Handle access to unavailable component.

        WHY: Subclasses override to provide specific error handling.

        Args:
            method_name: Method being accessed

        Returns:
            Callable or raises exception
        """
        raise NotImplementedError("Subclass must implement _handle_unavailable_component")
