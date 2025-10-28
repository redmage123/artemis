#!/usr/bin/env python3
"""
BACKWARD COMPATIBILITY WRAPPER

Original file: 2,183 lines (TwoPassPipeline + all supporting classes)
Refactored to: two_pass/ package (8 modules, 2,284 lines total)
This wrapper: ~100 lines (95.4% reduction!)

REFACTORING COMPLETE:

Extracted modules (8):
  ✅ two_pass/events.py (65 lines) - TwoPassEventType enum
  ✅ two_pass/exceptions.py (51 lines) - Exception hierarchy
  ✅ two_pass/models.py (226 lines) - PassResult, PassDelta, PassMemento
  ✅ two_pass/strategies.py (845 lines) - PassStrategy, FirstPass, SecondPass
  ✅ two_pass/comparator.py (147 lines) - PassComparator
  ✅ two_pass/rollback.py (189 lines) - RollbackManager
  ✅ two_pass/pipeline.py (672 lines) - TwoPassPipeline main class
  ✅ two_pass/factory.py (89 lines) - TwoPassPipelineFactory

ARCHITECTURE:
The two-pass pipeline uses Strategy Pattern for different pass implementations,
Memento Pattern for state capture/restore, and Observer Pattern for event broadcasting.

Two-Pass Approach:
1. First Pass (fast): Quick analysis to identify fatal flaws
2. Memento: Capture learnings and insights
3. Second Pass (refined): Full implementation using first pass insights
4. Comparison: Validate quality improvement
5. Rollback: Restore first pass if second pass degrades quality

New code should import from two_pass package:
    from two_pass import TwoPassPipeline, TwoPassPipelineFactory
    from two_pass import PassResult, PassDelta, PassMemento
    from two_pass import FirstPassStrategy, SecondPassStrategy

This wrapper re-exports all extracted components for backward compatibility.
"""

# Re-export events
from two_pass.events import TwoPassEventType

# Re-export exceptions
from two_pass.exceptions import (
    TwoPassPipelineException,
    FirstPassException,
    SecondPassException,
    PassComparisonException,
    RollbackException,
    MementoException
)

# Re-export models
from two_pass.models import (
    PassResult,
    PassDelta,
    PassMemento
)

# Re-export strategies
from two_pass.strategies import (
    PassStrategy,
    FirstPassStrategy,
    SecondPassStrategy
)

# Re-export comparator
from two_pass.comparator import PassComparator

# Re-export rollback
from two_pass.rollback import RollbackManager

# Re-export pipeline
from two_pass.pipeline import TwoPassPipeline

# Re-export factory
from two_pass.factory import TwoPassPipelineFactory

# Re-export for backward compatibility
__all__ = [
    # Events
    "TwoPassEventType",

    # Exceptions
    "TwoPassPipelineException",
    "FirstPassException",
    "SecondPassException",
    "PassComparisonException",
    "RollbackException",
    "MementoException",

    # Models
    "PassResult",
    "PassDelta",
    "PassMemento",

    # Strategies
    "PassStrategy",
    "FirstPassStrategy",
    "SecondPassStrategy",

    # Comparator
    "PassComparator",

    # Rollback
    "RollbackManager",

    # Pipeline
    "TwoPassPipeline",

    # Factory
    "TwoPassPipelineFactory"
]
