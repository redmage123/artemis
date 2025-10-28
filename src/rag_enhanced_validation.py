#!/usr/bin/env python3
"""
RAG-Enhanced Validation System (Backward Compatibility Wrapper)

WHY: Maintains backward compatibility while code transitions to modular package.
This file re-exports all components from the rag_validation package.

MIGRATION: All functionality has been moved to rag_validation/
- Update imports: from rag_validation import RAGValidator, RAGValidationFactory
- This wrapper will be deprecated in future versions

ARCHITECTURE: The modularized package structure provides:
- Separate modules for each class (Single Responsibility)
- Clear dependency hierarchy
- Easier testing and maintenance
- Better code organization
"""

# Re-export all components from modularized package
from rag_validation import (
    # Data models
    RAGExample,
    SimilarityResult,
    RAGValidationResult,

    # Strategies
    SimilarityStrategy,
    StructuralSimilarityStrategy,
    SemanticSimilarityStrategy,
    ASTSimilarityStrategy,

    # Core
    RAGQueryCache,
    RAGValidator,

    # Factory
    RAGValidationFactory,
)

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
