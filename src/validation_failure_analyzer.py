#!/usr/bin/env python3
"""
BACKWARD COMPATIBILITY WRAPPER

This module maintains backward compatibility while the codebase migrates
to the new modular structure in validation/.

All functionality has been refactored into:
- validation/models.py - FailureCategory, FailureAnalysis
- validation/categorizer.py - Failure categorization
- validation/constraint_extractors.py - Constraint extraction
- validation/message_extractor.py - Message extraction
- validation/analyzer.py - ValidationFailureAnalyzer
- validation/factory.py - FailureAnalyzerFactory

To migrate your code:
    OLD: from validation_failure_analyzer import ValidationFailureAnalyzer
    NEW: from validation import ValidationFailureAnalyzer

No breaking changes - all imports remain identical.
"""

# Re-export all public APIs from the modular package
from validation import (
    FailureCategory,
    FailureAnalysis,
    ValidationFailureAnalyzer,
    FailureAnalyzerFactory
)

__all__ = [
    'FailureCategory',
    'FailureAnalysis',
    'ValidationFailureAnalyzer',
    'FailureAnalyzerFactory'
]
