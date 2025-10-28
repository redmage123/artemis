#!/usr/bin/env python3
"""
WHY: Provide clean package interface for RAG functionality.
     Export main classes and convenience functions.

RESPONSIBILITY:
- Export public API classes and functions
- Provide backward-compatible imports
- Define package version and metadata

PATTERNS:
- Facade Pattern: Single import point for package functionality
- Explicit Exports: Control public API surface
"""

from rag.models import (
    Artifact,
    SearchResult,
    ARTIFACT_TYPES,
    create_artifact,
    create_search_result
)
from rag.document_processor import (
    generate_artifact_id,
    serialize_metadata_for_chromadb,
    deserialize_metadata,
    prepare_artifact_metadata
)
from rag.vector_store import VectorStore
from rag.retriever import Retriever
from rag.pattern_analyzer import PatternAnalyzer
from rag.rag_engine import RAGEngine


# Convenience function for backward compatibility
def create_rag_agent(db_path: str = "db") -> RAGEngine:
    """
    Create RAG engine instance.

    Args:
        db_path: Path to RAG database (default: 'db')

    Returns:
        Initialized RAGEngine instance
    """
    return RAGEngine(db_path=db_path)


__all__ = [
    # Core classes
    'RAGEngine',
    'VectorStore',
    'Retriever',
    'PatternAnalyzer',

    # Models
    'Artifact',
    'SearchResult',
    'ARTIFACT_TYPES',

    # Factory functions
    'create_artifact',
    'create_search_result',
    'create_rag_agent',

    # Utilities
    'generate_artifact_id',
    'serialize_metadata_for_chromadb',
    'deserialize_metadata',
    'prepare_artifact_metadata',
]

__version__ = '1.0.0'
