#!/usr/bin/env python3
"""
Code Review Stage - Backward Compatibility Wrapper

WHY: Maintain backward compatibility during modularization transition
RESPONSIBILITY: Re-export all components from modularized package
PATTERNS: Facade Pattern, Backward Compatibility

This is a compatibility shim. All new code should import from:
    from stages.code_review_stage import CodeReviewStage

DEPRECATED: This file will be removed in a future version.
"""

import warnings

# Show deprecation warning when this module is imported
warnings.warn(
    "Importing from 'code_review_stage' is deprecated. "
    "Please use 'from stages.code_review_stage import CodeReviewStage' instead. "
    "This compatibility layer will be removed in a future version.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export all components from the modularized package
from stages.code_review_stage import (
    CodeReviewStage,
    MultiDeveloperReviewCoordinator,
    ReviewResultAggregator,
    ReviewNotificationManager,
    ReviewStorageHandler,
    FileTypeDetector,
    RefactoringSuggestionGenerator,
    RefactoringRecommendations,
)

__all__ = [
    'CodeReviewStage',
    'MultiDeveloperReviewCoordinator',
    'ReviewResultAggregator',
    'ReviewNotificationManager',
    'ReviewStorageHandler',
    'FileTypeDetector',
    'RefactoringSuggestionGenerator',
    'RefactoringRecommendations',
]
