#!/usr/bin/env python3
"""
RAG Validation Result Data Model

WHY: Aggregates results from multiple similarity strategies into a single
validation decision with comprehensive feedback. Separates result structure
from validation logic for better testing and evolution.

RESPONSIBILITY:
- Store final validation pass/fail decision
- Aggregate similarity results and confidence metrics
- Provide warnings and recommendations
- Track validation metadata and timestamps

PATTERNS:
- Dataclass pattern for complex result structures
- Default factory pattern for collections
- Factory function pattern for datetime defaults
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from rag_validation.rag_example import RAGExample
from rag_validation.similarity_result import SimilarityResult


@dataclass
class RAGValidationResult:
    """
    Complete validation result with all similarity comparisons.

    WHY: Aggregates results from multiple strategies for final decision.
    """
    passed: bool
    confidence: float  # 0.0 to 1.0
    similar_examples: List[RAGExample]
    similarity_results: List[SimilarityResult]
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    validation_timestamp: datetime = field(default_factory=datetime.now)
