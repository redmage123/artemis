#!/usr/bin/env python3
"""
AI Query Result Data Class

WHY: Encapsulates the complete result from the AI query pipeline.

RESPONSIBILITY:
- Aggregate results from all pipeline stages (KG, RAG, LLM)
- Track success/failure status
- Measure total duration
- Provide single return type for service

PATTERNS:
- Dataclass for immutability
- Composition of other result types
- Optional fields for graceful degradation
"""

from typing import Optional
from dataclasses import dataclass

from ai_query.query_type import QueryType
from ai_query.kg_context import KGContext
from ai_query.rag_context import RAGContext
from ai_query.llm_response import LLMResponse


@dataclass
class AIQueryResult:
    """Complete result from AI query pipeline"""
    query_type: QueryType
    kg_context: Optional[KGContext]
    rag_context: Optional[RAGContext]
    llm_response: LLMResponse
    total_duration_ms: float
    success: bool
    error: Optional[str] = None
