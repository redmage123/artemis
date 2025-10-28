#!/usr/bin/env python3
"""
Advanced Features Package

WHY: Modular package providing AI query capabilities for advanced Artemis
features (Thermodynamic Computing, Two-Pass Pipeline, Dynamic Pipeline).
Separates concerns into focused modules for maintainability and testability.

RESPONSIBILITY:
- Export public API for advanced features
- Provide convenient imports for common use cases
- Maintain backward compatibility with original module

PATTERNS:
- Package Pattern: Organized module hierarchy
- Facade Pattern: Simplified public interface
- Single Responsibility: Each module has one clear purpose

MODULES:
- models: Data structures for AI responses
- prompt_builder: Prompt construction logic
- response_parser: Response parsing logic
- ai_capabilities: Core AI query orchestration
- feature_mixins: Mixin classes for feature inheritance

USAGE:
    # Import the main mixin
    from advanced_features import AdvancedFeaturesAIMixin

    # Or import specific models
    from advanced_features import ConfidenceEstimate, RiskAssessment

    # Or import components for custom usage
    from advanced_features import PromptBuilder, ResponseParser
"""

# ============================================================================
# DATA MODELS
# ============================================================================

from advanced_features.models import (
    # Enums
    RiskLevel,
    ComplexityLevel,
    IssueSeverity,
    # Data classes
    ConfidenceEstimate,
    RiskAssessment,
    QualityIssue,
    QualityEvaluation,
    ComplexityEstimate,
    BatchConfidenceResult
)

# ============================================================================
# CORE COMPONENTS
# ============================================================================

from advanced_features.prompt_builder import PromptBuilder
from advanced_features.response_parser import ResponseParser
from advanced_features.ai_capabilities import AICapabilities

# ============================================================================
# MIXIN CLASSES
# ============================================================================

from advanced_features.feature_mixins import AdvancedFeaturesAIMixin

# ============================================================================
# PUBLIC API
# ============================================================================

__all__ = [
    # Enums
    'RiskLevel',
    'ComplexityLevel',
    'IssueSeverity',
    # Data classes
    'ConfidenceEstimate',
    'RiskAssessment',
    'QualityIssue',
    'QualityEvaluation',
    'ComplexityEstimate',
    'BatchConfidenceResult',
    # Core components
    'PromptBuilder',
    'ResponseParser',
    'AICapabilities',
    # Mixins
    'AdvancedFeaturesAIMixin',
]

# ============================================================================
# PACKAGE METADATA
# ============================================================================

__version__ = '1.0.0'
__author__ = 'Artemis Development Team'
__description__ = 'AI query capabilities for advanced Artemis features'

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_ai_capabilities(ai_service, logger=None) -> AICapabilities:
    """
    Convenience function to create AICapabilities instance.

    WHY: Simplifies initialization for common use case.

    Args:
        ai_service: AIQueryService instance
        logger: Optional logger

    Returns:
        Configured AICapabilities instance

    Example:
        from advanced_features import create_ai_capabilities

        capabilities = create_ai_capabilities(ai_service, logger)
        estimate = capabilities.query_for_confidence(code)
    """
    return AICapabilities(ai_service, logger)


def get_package_info() -> dict:
    """
    Get package information.

    Returns:
        Dictionary with package metadata

    Example:
        from advanced_features import get_package_info

        info = get_package_info()
        print(f"Version: {info['version']}")
    """
    return {
        'version': __version__,
        'author': __author__,
        'description': __description__,
        'modules': [
            'models',
            'prompt_builder',
            'response_parser',
            'ai_capabilities',
            'feature_mixins'
        ]
    }
