#!/usr/bin/env python3
"""
WHY: Knowledge Graph with circuit breaker protection
RESPONSIBILITY: Protect KG operations with in-memory fallback
PATTERNS: Proxy (protected wrapper), Circuit Breaker, Fallback (in-memory storage)

Protected Knowledge Graph provides in-memory fallback when Neo4j is unavailable.
"""

from typing import Any, Dict
from circuit_breaker import CircuitBreakerConfig, CircuitBreakerOpenError
from protected.base import BaseProtectedComponent


class ProtectedKnowledgeGraph(BaseProtectedComponent):
    """
    Knowledge Graph with circuit breaker protection.

    WHY: Neo4j can fail - circuit breaker + in-memory fallback prevents data loss.
    PATTERNS: Proxy, Circuit Breaker, Fallback (in-memory storage).
    """

    def __init__(self, fallback_mode: bool = True, *args, **kwargs):
        """Initialize protected Knowledge Graph"""
        config = CircuitBreakerConfig(
            failure_threshold=3,
            timeout_seconds=120,
            success_threshold=2
        )

        super().__init__("knowledge_graph", config, fallback_mode)
        self.in_memory_fallback: Dict[str, Any] = {}

        # Initialize Knowledge Graph
        try:
            from knowledge_graph import KnowledgeGraph
            with self.breaker:
                self._component = KnowledgeGraph(*args, **kwargs)
                self.logger.info("Knowledge Graph initialized successfully")
        except (CircuitBreakerOpenError, Exception) as e:
            self.logger.error(f"Knowledge Graph initialization failed: {e}")
            self._component = None

    def _handle_circuit_open(self, method_name: str, *args, **kwargs):
        """Handle circuit breaker open state with in-memory fallback"""
        # Guard clause - raise if fallback disabled
        if not self.fallback_mode:
            raise CircuitBreakerOpenError(
                f"KG {method_name} failed - circuit breaker open",
                context={"method": method_name}
            )

        self.logger.warning(f"KG {method_name} using in-memory fallback")

        # Dispatch table for fallback handlers
        fallback_handlers = {
            "add_node": self._fallback_add_node,
            "query": lambda *a, **kw: [],
        }

        handler = fallback_handlers.get(method_name, lambda *a, **kw: None)
        return handler(*args, **kwargs)

    def _fallback_add_node(self, *args, **kwargs):
        """In-memory fallback for add_node"""
        node_id = kwargs.get("node_id") or (args[0] if args else None)

        # Guard clause - return None if no node_id
        if not node_id:
            return None

        self.in_memory_fallback[node_id] = kwargs
        return node_id

    def _protected_call(self, method_name: str, *args, **kwargs):
        """Execute protected method call"""
        # Guard clause - use fallback if component unavailable
        if not self._component:
            return self._handle_circuit_open(method_name, *args, **kwargs)

        try:
            with self.breaker:
                method = getattr(self._component, method_name)
                return method(*args, **kwargs)
        except CircuitBreakerOpenError:
            return self._handle_circuit_open(method_name, *args, **kwargs)

    def add_node(self, *args, **kwargs):
        """Add node with circuit breaker protection"""
        return self._protected_call("add_node", *args, **kwargs)

    def query(self, *args, **kwargs):
        """Query with circuit breaker protection"""
        return self._protected_call("query", *args, **kwargs)

    def _handle_unavailable_component(self, method_name: str):
        """Handle unavailable KG component"""
        return lambda *args, **kwargs: self._handle_circuit_open(method_name, *args, **kwargs)
