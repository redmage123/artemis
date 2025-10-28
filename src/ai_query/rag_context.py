#!/usr/bin/env python3
"""
RAG Context Data Class

WHY: Encapsulates retrieval-augmented generation results for prompt enhancement.

RESPONSIBILITY:
- Store RAG recommendations
- Track availability and errors
- Count recommendations for metrics

PATTERNS:
- Dataclass for immutability
- Optional error for graceful degradation
"""

from typing import List, Optional
from dataclasses import dataclass


@dataclass
class RAGContext:
    """RAG context retrieved for prompt enhancement"""
    recommendations: List[str]
    recommendation_count: int
    rag_available: bool
    error: Optional[str] = None
