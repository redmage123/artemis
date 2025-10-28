#!/usr/bin/env python3
"""
Knowledge Graph Query Strategy Interface

WHY: Abstract base class for different KG query strategies (Strategy Pattern).

RESPONSIBILITY:
- Define interface for KG query strategies
- Enforce contract for query_kg and estimate_token_savings
- Enable extensibility for new query types

PATTERNS:
- Strategy Pattern (GOF)
- Abstract Base Class (ABC)
- Open/Closed Principle (SOLID)
"""

from typing import Dict, List, Any
from abc import ABC, abstractmethod

from ai_query.kg_context import KGContext


class KGQueryStrategy(ABC):
    """
    Abstract strategy for querying Knowledge Graph

    Each query type (requirements, architecture, etc.) implements
    its own KG query logic via this interface.
    """

    @abstractmethod
    def query_kg(self, kg: Any, query_params: Dict[str, Any]) -> KGContext:
        """
        Query Knowledge Graph for patterns

        Args:
            kg: Knowledge Graph instance
            query_params: Query-specific parameters

        Returns:
            KGContext with patterns found
        """
        pass

    @abstractmethod
    def estimate_token_savings(self, patterns: List[Dict]) -> int:
        """Estimate token savings from patterns found"""
        pass
