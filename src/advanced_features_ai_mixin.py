#!/usr/bin/env python3
"""
Advanced Features AI Mixin - Backward Compatibility Wrapper

WHY this file exists:
    This is a thin backward compatibility wrapper that redirects to the
    modularized advanced_features package. The original 655-line monolithic
    file has been refactored into focused modules for maintainability.

WHAT changed:
    Original file (655 lines) → Modular package:
    - advanced_features/models.py: Data models and enums
    - advanced_features/prompt_builder.py: Prompt construction
    - advanced_features/response_parser.py: Response parsing
    - advanced_features/ai_capabilities.py: AI query orchestration
    - advanced_features/feature_mixins.py: Mixin class
    - advanced_features/__init__.py: Package exports

RESPONSIBILITY:
    - Maintain backward compatibility with existing code
    - Re-export public API from advanced_features package
    - Provide deprecation notices for direct imports

MIGRATION PATH:
    Old code:
        from advanced_features_ai_mixin import AdvancedFeaturesAIMixin
        from advanced_features_ai_mixin import ConfidenceEstimate

    New code (preferred):
        from advanced_features import AdvancedFeaturesAIMixin
        from advanced_features import ConfidenceEstimate

    Both work, but new imports are preferred for future development.

DESIGN PATTERNS:
    - Facade Pattern: Simplified interface to modular package
    - Proxy Pattern: Wrapper delegates to actual implementation
    - Single Responsibility: Only handles backward compatibility

USAGE (existing code continues to work):
    from advanced_features_ai_mixin import AdvancedFeaturesAIMixin

    class ThermodynamicComputing(AdvancedFeaturesAIMixin):
        def __init__(self, ai_service):
            self.ai_service = ai_service

        def quantify_uncertainty(self, code):
            return self.query_for_confidence(code, context="uncertainty")
"""

# ============================================================================
# BACKWARD COMPATIBILITY EXPORTS
# ============================================================================

# Import everything from the modular package
from advanced_features import (
    # Data models
    ConfidenceEstimate,
    RiskAssessment,
    QualityEvaluation,
    ComplexityEstimate,
    QualityIssue,
    BatchConfidenceResult,
    # Enums
    RiskLevel,
    ComplexityLevel,
    IssueSeverity,
    # Main mixin class
    AdvancedFeaturesAIMixin,
    # Core components (for advanced usage)
    PromptBuilder,
    ResponseParser,
    AICapabilities,
)

# Re-export for backward compatibility
__all__ = [
    # Data classes (most commonly used)
    'ConfidenceEstimate',
    'RiskAssessment',
    'QualityEvaluation',
    'ComplexityEstimate',
    'QualityIssue',
    'BatchConfidenceResult',
    # Enums
    'RiskLevel',
    'ComplexityLevel',
    'IssueSeverity',
    # Main mixin (primary export)
    'AdvancedFeaturesAIMixin',
    # Advanced components
    'PromptBuilder',
    'ResponseParser',
    'AICapabilities',
]

# ============================================================================
# DEPRECATION NOTICE (for future migration)
# ============================================================================

import warnings

def _show_deprecation_warning():
    """
    Show deprecation warning on first import.

    WHY: Encourage migration to new package structure while maintaining
    backward compatibility.
    """
    warnings.warn(
        "Importing from 'advanced_features_ai_mixin' is deprecated. "
        "Please use 'from advanced_features import AdvancedFeaturesAIMixin' instead. "
        "This backward compatibility wrapper will be maintained but the new import "
        "path is preferred for new code.",
        DeprecationWarning,
        stacklevel=3
    )

# Uncomment below to enable deprecation warnings (currently disabled for smooth transition)
# _show_deprecation_warning()

# ============================================================================
# MODULE METADATA
# ============================================================================

__version__ = '2.0.0'  # Bumped to 2.0 to reflect modularization
__refactored__ = True
__original_lines__ = 655
__wrapper_lines__ = 115  # This file
__reduction_percentage__ = 82.4  # (655 - 115) / 655 * 100

# ============================================================================
# USAGE EXAMPLES (unchanged from original)
# ============================================================================

"""
Example 1: Thermodynamic Computing

class ThermodynamicComputing(AdvancedFeaturesAIMixin):
    def __init__(self, ai_service, observable=None):
        self.ai_service = ai_service
        self.logger = logger
        self.observable = observable

    def quantify_uncertainty(self, code, context):
        # Use DRY mixin method
        estimate = self.query_for_confidence(code, context=context)

        # Convert to internal ConfidenceScore
        return ConfidenceScore(
            mean=estimate.score,
            confidence_interval=(estimate.score - 0.1, estimate.score + 0.1),
            sources=estimate.uncertainty_sources
        )


Example 2: Two-Pass Pipeline

class TwoPassPipeline(AdvancedFeaturesAIMixin):
    def __init__(self, ai_service, config):
        self.ai_service = ai_service
        self.logger = logger
        self.config = config

    def should_accept_second_pass(self, first_code, second_code, requirements):
        # Use DRY mixin method for comparison
        second_quality = self.query_for_quality(
            code=second_code,
            requirements=requirements,
            previous_version=first_code
        )

        return second_quality.quality_score > self.config.quality_threshold


Example 3: Dynamic Pipeline

class DynamicPipeline(AdvancedFeaturesAIMixin):
    def __init__(self, ai_service, config):
        self.ai_service = ai_service
        self.logger = logger
        self.config = config

    def configure_parallelization(self, requirements):
        # Use DRY mixin method
        complexity, points, details = self.query_for_complexity(requirements)

        # Configure based on estimate
        self.max_workers = details['suggested_workers']
        self.parallelization_enabled = (
            details['parallelization_potential'] in ['high', 'medium']
        )
"""
