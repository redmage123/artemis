#!/usr/bin/env python3
"""
WHY: Provide unified public API for self-critique validation package.

RESPONSIBILITY:
- Export all public classes and enums
- Provide convenient access to validator and factory
- Hide internal implementation details
- Maintain backward compatibility

PATTERNS:
- Facade Pattern: Single import point for entire package
- Explicit Exports: __all__ defines public API
"""

from .models import (
    CritiqueLevel,
    CritiqueSeverity,
    CritiqueFinding,
    UncertaintyMetrics,
    CodeCitation,
    CritiqueResult
)

from .validator_core import (
    SelfCritiqueValidator,
    SelfCritiqueFactory
)

from .improvement_suggester import (
    UncertaintyAnalyzer,
    CitationTracker
)

from .critique_generator import CritiqueGenerator
from .validation_checker import ValidationChecker
from .feedback_processor import FeedbackProcessor


__all__ = [
    # Enums
    'CritiqueLevel',
    'CritiqueSeverity',

    # Data Models
    'CritiqueFinding',
    'UncertaintyMetrics',
    'CodeCitation',
    'CritiqueResult',

    # Main API
    'SelfCritiqueValidator',
    'SelfCritiqueFactory',

    # Components (for advanced usage)
    'UncertaintyAnalyzer',
    'CitationTracker',
    'CritiqueGenerator',
    'ValidationChecker',
    'FeedbackProcessor',
]
