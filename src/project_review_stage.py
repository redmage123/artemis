#!/usr/bin/env python3
"""
Project Review Stage - Backward Compatibility Wrapper

WHY: Maintain backward compatibility while using modularized implementation
RESPONSIBILITY: Re-export ProjectReviewStage from refactored package
PATTERNS: Facade Pattern, Adapter Pattern

This module provides backward compatibility for code importing from:
    from project_review_stage import ProjectReviewStage

The actual implementation has been refactored into stages.project_review package:
    - stages/project_review/project_review_stage_core.py - Main orchestrator
    - stages/project_review/architecture_reviewer.py - Architecture review
    - stages/project_review/sprint_validator.py - Sprint validation
    - stages/project_review/quality_analyzer.py - Quality analysis
    - stages/project_review/review_scorer.py - Score calculation
    - stages/project_review/approval_handler.py - Approval/rejection handling
    - stages/project_review/feedback_compiler.py - Feedback compilation

Migration Guide:
    Old: from project_review_stage import ProjectReviewStage
    New: from stages.project_review import ProjectReviewStage

All existing imports will continue to work without modification.
"""

# Re-export from modular package for backward compatibility
from stages.project_review import (
    ProjectReviewStage,
    ArchitectureReviewer,
    SprintValidator,
    QualityAnalyzer,
    ReviewScorer,
    ApprovalHandler,
    FeedbackCompiler,
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
