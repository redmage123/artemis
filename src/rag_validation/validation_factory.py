#!/usr/bin/env python3
"""
RAG Validation Factory

WHY: Different frameworks and languages require different validation strategies
and thresholds. The factory pattern centralizes configuration and makes it easy
to create properly configured validators for specific contexts.

RESPONSIBILITY:
- Create RAG validators with framework-specific configurations
- Map framework names to optimal validation strategies
- Provide default configurations for unknown frameworks
- Create appropriate strategy instances

PATTERNS:
- Factory Pattern: Centralized object creation
- Configuration as data: Dictionary-based config
- Dictionary dispatch: Avoid if/elif chains
"""

from typing import Dict, List, Optional
from rag_validation.rag_validator import RAGValidator
from rag_validation.similarity_strategy import SimilarityStrategy
from rag_validation.structural_similarity_strategy import StructuralSimilarityStrategy
from rag_validation.semantic_similarity_strategy import SemanticSimilarityStrategy
from rag_validation.ast_similarity_strategy import ASTSimilarityStrategy


class RAGValidationFactory:
    """
    Factory for creating RAG validators with framework-specific configurations.

    WHY: Different frameworks need different validation strategies and thresholds.
    WHAT: Factory Pattern for creating pre-configured validators.
    """

    # Framework-specific configurations
    _FRAMEWORK_CONFIGS = {
        'django': {
            'min_similarity': 0.4,
            'min_confidence': 0.7,
            'strategies': ['structural', 'semantic', 'ast']
        },
        'flask': {
            'min_similarity': 0.3,
            'min_confidence': 0.6,
            'strategies': ['structural', 'semantic', 'ast']
        },
        'rails': {
            'min_similarity': 0.4,
            'min_confidence': 0.7,
            'strategies': ['structural', 'semantic']  # No AST for Ruby
        },
        'react': {
            'min_similarity': 0.3,
            'min_confidence': 0.6,
            'strategies': ['structural', 'semantic']
        },
    }

    @staticmethod
    def create_validator(
        rag_agent,
        framework: Optional[str] = None,
        custom_config: Optional[Dict] = None
    ) -> RAGValidator:
        """
        Create validator with framework-specific configuration.

        WHY: Different frameworks have different validation requirements.

        Args:
            rag_agent: RAG agent instance
            framework: Framework name (django, flask, rails, etc.)
            custom_config: Override default configuration

        Returns:
            Configured RAGValidator instance
        """
        # Get framework config or use defaults
        config = RAGValidationFactory._FRAMEWORK_CONFIGS.get(
            framework.lower() if framework else 'default',
            {
                'min_similarity': 0.3,
                'min_confidence': 0.6,
                'strategies': ['structural', 'semantic', 'ast']
            }
        )

        # Apply custom config overrides
        if custom_config:
            config.update(custom_config)

        # Create strategies based on config
        strategies = RAGValidationFactory._create_strategies(
            config['strategies']
        )

        # Create validator
        return RAGValidator(
            rag_agent=rag_agent,
            strategies=strategies,
            min_similarity_threshold=config['min_similarity'],
            min_confidence_threshold=config['min_confidence']
        )

    @staticmethod
    def _create_strategies(strategy_names: List[str]) -> List[SimilarityStrategy]:
        """
        Create strategy instances from names.

        WHY: Map string names to strategy objects.
        """
        # Strategy mapping (avoid elif chain)
        strategy_map = {
            'structural': StructuralSimilarityStrategy,
            'semantic': SemanticSimilarityStrategy,
            'ast': ASTSimilarityStrategy,
        }

        strategies = []

        for name in strategy_names:
            strategy_class = strategy_map.get(name.lower())
            if strategy_class:
                strategies.append(strategy_class())

        return strategies
