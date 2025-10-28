#!/usr/bin/env python3
"""
Similarity Result Data Model

WHY: Encapsulates the output of similarity strategy computations, providing
detailed metrics and actionable feedback separate from the computation logic.

RESPONSIBILITY:
- Store similarity scores and strategy metadata
- Track differences and suggestions for improvement
- Provide structured output for aggregation and reporting

PATTERNS:
- Dataclass pattern for structured data
- Default factory pattern for collections
"""

from dataclasses import dataclass, field
from typing import List
from rag_validation.rag_example import RAGExample


@dataclass
class SimilarityResult:
    """
    Result of similarity comparison between generated code and RAG example.

    WHY: Provides detailed similarity metrics for validation decisions.
    """
    score: float  # 0.0 to 1.0
    strategy_name: str
    matched_example: RAGExample
    differences: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
