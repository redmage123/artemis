#!/usr/bin/env python3
"""
WHY: Provide backward compatibility for existing code using self_critique_validator.

RESPONSIBILITY:
- Re-export all classes and enums from self_critique package
- Maintain identical API to original monolithic module
- Enable gradual migration to new package structure
- Preserve all functionality without code changes

PATTERNS:
- Proxy Pattern: Forward all imports to new package
- Backward Compatibility: Zero breaking changes
- Deprecation Path: Enable future migration warnings

MIGRATION NOTE:
This module is a compatibility wrapper. New code should import from self_critique package:

    # Old (deprecated but supported):
    from self_critique_validator import SelfCritiqueValidator

    # New (recommended):
    from self_critique import SelfCritiqueValidator

REFACTORING:
Original file: 653 lines
Wrapper file: ~70 lines
Reduction: ~89%

Module breakdown:
- models.py: 116 lines (data classes and enums)
- critique_generator.py: 259 lines (LLM critique generation)
- improvement_suggester.py: 335 lines (uncertainty analysis, citations)
- validation_checker.py: 115 lines (pass/fail determination)
- feedback_processor.py: 181 lines (feedback generation)
- validator_core.py: 175 lines (orchestration)
- __init__.py: 60 lines (package exports)
Total: 1,241 lines (in 7 focused modules vs 1 monolithic file)
"""

# Re-export all public API from self_critique package
from self_critique import (
    # Enums
    CritiqueLevel,
    CritiqueSeverity,

    # Data Models
    CritiqueFinding,
    UncertaintyMetrics,
    CodeCitation,
    CritiqueResult,

    # Main API
    SelfCritiqueValidator,
    SelfCritiqueFactory,

    # Components
    UncertaintyAnalyzer,
    CitationTracker,
)


__all__ = [
    'CritiqueLevel',
    'CritiqueSeverity',
    'CritiqueFinding',
    'UncertaintyMetrics',
    'CodeCitation',
    'CritiqueResult',
    'SelfCritiqueValidator',
    'SelfCritiqueFactory',
    'UncertaintyAnalyzer',
    'CitationTracker',
]


# Example usage preserved from original
if __name__ == "__main__":
    print("Self-Critique Validator - Layer 5 Hallucination Reduction")
    print("Ready for integration with validation pipeline")
    print("\nNOTE: This is a compatibility wrapper.")
    print("New code should import from 'self_critique' package directly.")
