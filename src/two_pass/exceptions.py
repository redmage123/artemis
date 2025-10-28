"""
Module: two_pass/exceptions.py

WHY: Exception hierarchy for two-pass pipeline errors.
RESPONSIBILITY: Provide specific exception types for each failure mode.
PATTERNS: Exception Hierarchy.

EXTRACTED FROM: two_pass_pipeline.py (lines 149-176, 27 lines)
"""

from artemis_exceptions import PipelineException


class TwoPassPipelineException(PipelineException):
    """Base exception for two-pass pipeline errors"""
    pass


class FirstPassException(TwoPassPipelineException):
    """Error during first pass execution"""
    pass


class SecondPassException(TwoPassPipelineException):
    """Error during second pass execution"""
    pass


class PassComparisonException(TwoPassPipelineException):
    """Error comparing pass results"""
    pass


class RollbackException(TwoPassPipelineException):
    """Error during rollback operation"""
    pass


class MementoException(TwoPassPipelineException):
    """Error creating or applying memento"""
    pass


__all__ = [
    "TwoPassPipelineException",
    "FirstPassException",
    "SecondPassException",
    "PassComparisonException",
    "RollbackException",
    "MementoException"
]
