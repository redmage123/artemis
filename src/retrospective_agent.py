#!/usr/bin/env python3
"""
Retrospective Agent - Backward Compatibility Wrapper

WHY: Maintain backward compatibility after modularization
RESPONSIBILITY: Re-export all components from stages.retrospective
PATTERNS: Facade Pattern, Backward Compatibility Wrapper

This module maintains backward compatibility by re-exporting all
components from the modularized stages.retrospective package.

Original file (725 lines) has been refactored into modular components.
All imports should continue to work seamlessly.
"""

# Re-export all components from modularized package
from stages.retrospective import (
    # Main agent
    RetrospectiveAgent,

    # Data models
    RetrospectiveItem,
    SprintMetrics,
    RetrospectiveReport,
    RetrospectiveContext,

    # Components (for advanced usage)
    MetricsExtractor,
    SuccessAnalyzer,
    FailureAnalyzer,
    ActionItemGenerator,
    LearningExtractor,
    HealthAssessor,
    RecommendationGenerator,
    RetrospectiveStorage,
)

__all__ = [
    # Main agent
    'RetrospectiveAgent',

    # Data models
    'RetrospectiveItem',
    'SprintMetrics',
    'RetrospectiveReport',
    'RetrospectiveContext',

    # Components
    'MetricsExtractor',
    'SuccessAnalyzer',
    'FailureAnalyzer',
    'ActionItemGenerator',
    'LearningExtractor',
    'HealthAssessor',
    'RecommendationGenerator',
    'RetrospectiveStorage',
]
