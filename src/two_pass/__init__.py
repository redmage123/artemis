"""
Two-Pass Pipeline Package - Modularized two-pass execution system

WHY: Fast feedback (first pass) with learning-enhanced execution (second pass).
RESPONSIBILITY: Provide complete two-pass pipeline system with rollback capability.
PATTERNS: Strategy, Memento, Observer, Factory.

COMPLETE REFACTORING: All classes extracted to focused modules.

EXTRACTED FROM: two_pass_pipeline.py (2,183 lines → 2,168 lines in 8 modules)

This package contains:
- events.py: TwoPassEventType enum (65 lines)
- exceptions.py: Exception hierarchy (51 lines)
- models.py: PassResult, PassDelta, PassMemento (226 lines)
- strategies.py: PassStrategy, FirstPassStrategy, SecondPassStrategy (845 lines)
- comparator.py: PassComparator (147 lines)
- rollback.py: RollbackManager (189 lines)
- pipeline.py: TwoPassPipeline (672 lines)
- factory.py: TwoPassPipelineFactory (89 lines)
"""

# Events
from two_pass.events import TwoPassEventType

# Exceptions
from two_pass.exceptions import (
    TwoPassPipelineException,
    FirstPassException,
    SecondPassException,
    PassComparisonException,
    RollbackException,
    MementoException
)

# Models
from two_pass.models import (
    PassResult,
    PassDelta,
    PassMemento
)

# Strategies
from two_pass.strategies import (
    PassStrategy,
    FirstPassStrategy,
    SecondPassStrategy
)

# Comparator
from two_pass.comparator import PassComparator

# Rollback
from two_pass.rollback import RollbackManager

# Pipeline
from two_pass.pipeline import TwoPassPipeline

# Factory
from two_pass.factory import TwoPassPipelineFactory


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
