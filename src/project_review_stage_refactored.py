#!/usr/bin/env python3
"""
Project Review Stage - Backward Compatibility Wrapper

WHY: Maintain backward compatibility with existing code
RESPONSIBILITY: Re-export refactored components
PATTERNS: Facade Pattern, Deprecation Warning

This file provides backward compatibility for code that imports from
the old project_review_stage.py file. All functionality has been moved
to the stages/project_review/ package.

DEPRECATED: Import from stages.project_review instead
"""

import warnings

# Re-export all components from the refactored package
from stages.project_review import (
    ProjectReviewStage,
    ArchitectureReviewer,
    SprintValidator,
    QualityAnalyzer,
    ReviewScorer,
    ApprovalHandler,
    FeedbackCompiler,
)

# Show deprecation warning when this module is imported
warnings.warn(
    "Importing from project_review_stage.py is deprecated. "
    "Please import from stages.project_review instead.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = [
    'ProjectReviewStage',
    'ArchitectureReviewer',
    'SprintValidator',
    'QualityAnalyzer',
    'ReviewScorer',
    'ApprovalHandler',
    'FeedbackCompiler',
]
