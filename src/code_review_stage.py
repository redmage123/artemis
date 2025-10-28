#!/usr/bin/env python3
"""
Code Review Stage - Backward Compatibility Wrapper

WHY: Maintain 100% backward compatibility while using refactored modular implementation.
RESPONSIBILITY: Re-export CodeReviewStage from new modular package.
PATTERNS: Facade pattern - delegate to modular implementation.

This file maintains backward compatibility for existing imports:
    from code_review_stage import CodeReviewStage

All functionality has been refactored into stages/code_review_stage/ package
with the following modules:
- models.py: Data structures and types
- review_executor.py: Core review execution logic
- review_notifier.py: Event and notification handling
- storage_manager.py: RAG and Knowledge Graph storage
- refactoring_suggestions.py: Refactoring suggestion generation
- __init__.py: Public API facade

REFACTORING SUMMARY:
- Original file: 693 lines
- Wrapper file: ~30 lines
- Reduction: 95.7%
- Modules created: 6
- All imports maintained for backward compatibility
"""

# Re-export everything from the modular package for backward compatibility
from stages.code_review_stage import (
    CodeReviewStage,
    ReviewStatus,
    ReviewMetrics,
    DeveloperReviewResult,
    StageProgress,
    CodeReviewStageResult
)

# Maintain backward compatibility - export main class
__all__ = [
    'CodeReviewStage',
    'ReviewStatus',
    'ReviewMetrics',
    'DeveloperReviewResult',
    'StageProgress',
    'CodeReviewStageResult'
]
