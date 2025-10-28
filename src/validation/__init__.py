#!/usr/bin/env python3
"""
WHY: Provide validation failure analysis to enable intelligent prompt refinement
RESPONSIBILITY: Export failure analyzer, models, and factory for external use
PATTERNS: Strategy (categorization), Factory (analyzer creation)

This package analyzes validation failures and extracts actionable constraints:
- Categorizes failures by type (missing imports, incomplete code, etc.)
- Extracts specific constraints for retry attempts
- Provides severity scoring
- Recommends retry strategies

Example:
    from validation import ValidationFailureAnalyzer, FailureCategory

    analyzer = ValidationFailureAnalyzer(logger)
    analysis = analyzer.analyze_failures(validation_results, code)

    print(f"Category: {analysis.category.value}")
    print(f"Constraints: {analysis.constraints}")
    print(f"Severity: {analysis.severity}")
    print(f"Retry recommended: {analysis.retry_recommended}")
"""

from validation.models import FailureCategory, FailureAnalysis
from validation.analyzer import ValidationFailureAnalyzer
from validation.factory import FailureAnalyzerFactory

__all__ = [
    'FailureCategory',
    'FailureAnalysis',
    'ValidationFailureAnalyzer',
    'FailureAnalyzerFactory'
]
