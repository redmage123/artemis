#!/usr/bin/env python3
"""
RAG Validation Package

WHY: Modularized RAG-enhanced validation system for detecting and preventing
LLM hallucinations in generated code by comparing against proven patterns
from authoritative sources.

RESPONSIBILITY:
- Export all public validation components
- Provide clean package interface
- Enable backward compatibility

EXPORTS:
- Data Models: RAGExample, SimilarityResult, RAGValidationResult
- Strategies: SimilarityStrategy, StructuralSimilarityStrategy,
              SemanticSimilarityStrategy, ASTSimilarityStrategy
- Core: RAGValidator, RAGQueryCache
- Factory: RAGValidationFactory
"""

# Data models
from rag_validation.rag_example import RAGExample
from rag_validation.similarity_result import SimilarityResult
from rag_validation.validation_result import RAGValidationResult

# Strategy interface and implementations
from rag_validation.similarity_strategy import SimilarityStrategy
from rag_validation.structural_similarity_strategy import StructuralSimilarityStrategy
from rag_validation.semantic_similarity_strategy import SemanticSimilarityStrategy
from rag_validation.ast_similarity_strategy import ASTSimilarityStrategy

# Core components
from rag_validation.query_cache import RAGQueryCache
from rag_validation.rag_validator import RAGValidator

# Factory
from rag_validation.validation_factory import RAGValidationFactory

__all__ = [
    # Data models
    'RAGExample',
    'SimilarityResult',
    'RAGValidationResult',

    # Strategies
    'SimilarityStrategy',
    'StructuralSimilarityStrategy',
    'SemanticSimilarityStrategy',
    'ASTSimilarityStrategy',

    # Core
    'RAGQueryCache',
    'RAGValidator',

    # Factory
    'RAGValidationFactory',
]
