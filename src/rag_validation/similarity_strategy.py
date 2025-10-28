#!/usr/bin/env python3
"""
Similarity Strategy Interface

WHY: Defines the contract for similarity computation algorithms using the
Strategy Pattern. This allows adding new similarity metrics without modifying
existing validation logic, following the Open/Closed Principle.

RESPONSIBILITY:
- Define abstract interface for similarity strategies
- Enforce consistent method signatures across implementations
- Document expected behavior for strategy implementers

PATTERNS:
- Strategy Pattern: Interchangeable algorithms
- Abstract Base Class: Interface definition
- Template Method: Common interface with varied implementations
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict
from rag_validation.rag_example import RAGExample
from rag_validation.similarity_result import SimilarityResult


class SimilarityStrategy(ABC):
    """
    Abstract base class for similarity computation strategies.

    WHY: Strategy Pattern allows different similarity algorithms
         without modifying validation logic. Each language/framework
         may require different similarity metrics.

    WHAT: Defines interface for computing similarity between
          generated code and RAG examples.
    """

    @abstractmethod
    def compute_similarity(
        self,
        generated_code: str,
        rag_example: RAGExample,
        context: Optional[Dict] = None
    ) -> SimilarityResult:
        """
        Compute similarity between generated code and RAG example.

        WHY: Abstract method ensures all strategies implement consistent interface.

        Args:
            generated_code: Code to validate
            rag_example: Reference code from RAG
            context: Additional context (language, framework, requirements)

        Returns:
            SimilarityResult with score and details
        """
        pass

    @abstractmethod
    def get_strategy_name(self) -> str:
        """Return strategy name for logging and debugging."""
        pass
