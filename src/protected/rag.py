#!/usr/bin/env python3
"""
WHY: RAG Agent with circuit breaker protection
RESPONSIBILITY: Protect RAG operations from ChromaDB/embedding failures
PATTERNS: Proxy (protected wrapper), Circuit Breaker

Protected RAG agent fails fast when storage is unavailable.
"""

from typing import Any
import logging
from circuit_breaker import CircuitBreakerConfig, CircuitBreakerOpenError
from protected.base import BaseProtectedComponent


class ProtectedRAGAgent(BaseProtectedComponent):
    """
    RAG Agent with circuit breaker protection.

    WHY: RAG storage (ChromaDB) can fail - circuit breaker prevents cascading failures.
    PATTERNS: Proxy (wraps RAGAgent), Circuit Breaker.
    """

    def __init__(self, *args, fallback_mode: bool = True, **kwargs):
        """Initialize protected RAG agent"""
        config = CircuitBreakerConfig(
            failure_threshold=3,
            timeout_seconds=120,
            success_threshold=2
        )

        super().__init__("rag_agent", config, fallback_mode)

        # Initialize RAG agent
        try:
            from rag_agent import RAGAgent
            with self.breaker:
                self._component = RAGAgent(*args, **kwargs)
                self.logger.info("RAG Agent initialized successfully")
        except (CircuitBreakerOpenError, Exception) as e:
            self.logger.error(f"RAG Agent initialization failed: {e}")
            self._component = None

    def _handle_circuit_open(self, method_name: str):
        """Handle circuit breaker open state"""
        if self.fallback_mode:
            self.logger.warning(f"RAG {method_name} skipped - using fallback mode")
            return None

        raise CircuitBreakerOpenError(
            f"RAG {method_name} failed - circuit breaker open",
            context={"method": method_name}
        )

    def _protected_call(self, method_name: str, *args, **kwargs):
        """Execute protected method call"""
        # Guard clause - component unavailable
        if not self._component:
            return self._handle_circuit_open(method_name)

        try:
            with self.breaker:
                method = getattr(self._component, method_name)
                return method(*args, **kwargs)
        except CircuitBreakerOpenError:
            return self._handle_circuit_open(method_name)

    def store_artifact(self, *args, **kwargs):
        """Store artifact with circuit breaker protection"""
        return self._protected_call("store_artifact", *args, **kwargs)

    def query_similar(self, *args, **kwargs):
        """Query similar with circuit breaker protection"""
        return self._protected_call("query_similar", *args, **kwargs)

    def delete_artifact(self, *args, **kwargs):
        """Delete artifact with circuit breaker protection"""
        return self._protected_call("delete_artifact", *args, **kwargs)

    def _handle_unavailable_component(self, method_name: str):
        """Handle unavailable RAG component"""
        return lambda *args, **kwargs: self._handle_circuit_open(method_name)
