#!/usr/bin/env python3
"""
WHY: Provide public API for circuit-breaker-protected components
RESPONSIBILITY: Export protected wrappers and health utilities
PATTERNS: Facade (simplified package interface)

Protected components package provides circuit breaker protection for critical
Artemis services (RAG, LLM, Knowledge Graph).
"""

from protected.rag import ProtectedRAGAgent
from protected.llm import ProtectedLLMClient
from protected.knowledge_graph import ProtectedKnowledgeGraph
from protected.health import check_all_protected_components, reset_all_circuit_breakers

__all__ = [
    # Protected components
    'ProtectedRAGAgent',
    'ProtectedLLMClient',
    'ProtectedKnowledgeGraph',

    # Health utilities
    'check_all_protected_components',
    'reset_all_circuit_breakers',
]
