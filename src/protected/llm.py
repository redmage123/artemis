#!/usr/bin/env python3
"""
WHY: LLM Client with circuit breaker protection
RESPONSIBILITY: Protect LLM calls from API failures
PATTERNS: Proxy (protected wrapper), Circuit Breaker

Protected LLM client fails fast when API is unavailable.
"""

from circuit_breaker import CircuitBreakerConfig, CircuitBreakerOpenError
from artemis_exceptions import LLMClientError
from protected.base import BaseProtectedComponent


class ProtectedLLMClient(BaseProtectedComponent):
    """
    LLM Client with circuit breaker protection.

    WHY: LLM APIs can fail - circuit breaker prevents retrying unavailable service.
    PATTERNS: Proxy (wraps LLM client), Circuit Breaker.
    """

    def __init__(self, provider: str = "openai", fallback_mode: bool = False):
        """Initialize protected LLM client"""
        config = CircuitBreakerConfig(
            failure_threshold=5,
            timeout_seconds=60,
            success_threshold=3
        )

        super().__init__(f"llm_{provider}", config, fallback_mode)
        self.provider = provider

        # Initialize LLM client
        try:
            from llm_client import create_llm_client
            with self.breaker:
                self._component = create_llm_client(provider)
                self.logger.info(f"LLM Client ({provider}) initialized successfully")
        except (CircuitBreakerOpenError, Exception) as e:
            self.logger.error(f"LLM Client ({provider}) initialization failed: {e}")
            self._component = None

    def _handle_circuit_open(self, method_name: str):
        """Handle circuit breaker open state"""
        raise LLMClientError(
            f"LLM API unavailable - circuit breaker open",
            context={"method": method_name, "breaker_status": self.breaker.get_status()}
        )

    def _protected_call(self, method_name: str, *args, **kwargs):
        """Execute protected method call"""
        # Guard clause - component unavailable
        if not self._component:
            raise LLMClientError(
                f"LLM client unavailable - circuit breaker open",
                context={"method": method_name}
            )

        try:
            with self.breaker:
                method = getattr(self._component, method_name)
                return method(*args, **kwargs)
        except CircuitBreakerOpenError as e:
            raise LLMClientError(
                f"LLM API unavailable - circuit breaker open",
                context={"method": method_name, "breaker_status": self.breaker.get_status()}
            ) from e

    def complete(self, *args, **kwargs):
        """Complete with circuit breaker protection"""
        return self._protected_call("complete", *args, **kwargs)

    def generate_text(self, *args, **kwargs):
        """Generate text with circuit breaker protection"""
        return self._protected_call("generate_text", *args, **kwargs)

    def _handle_unavailable_component(self, method_name: str):
        """Handle unavailable LLM component"""
        raise LLMClientError(
            f"LLM client unavailable for method: {method_name}",
            context={"method": method_name}
        )
