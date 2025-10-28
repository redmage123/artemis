#!/usr/bin/env python3
"""
RAG Example Data Model

WHY: Encapsulates code examples retrieved from RAG database with complete metadata.
This separation allows the example model to evolve independently of validation logic.

RESPONSIBILITY:
- Define the structure for RAG-retrieved code examples
- Store code content, source information, and metadata
- Provide relevance scoring for ranking examples

PATTERNS:
- Dataclass pattern for immutable data modeling
- Default factory pattern for mutable defaults
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class RAGExample:
    """
    Represents a code example retrieved from RAG database.

    WHY: Encapsulates RAG query results with metadata for similarity comparison.
    """
    code: str
    source: str  # Book, repo, documentation
    language: str
    framework: Optional[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    relevance_score: float = 0.0
