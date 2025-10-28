"""
Module: two_pass/factory.py

WHY: Factory for creating TwoPassPipeline instances with default configuration.
RESPONSIBILITY: TwoPassPipelineFactory creates configured pipeline instances.
PATTERNS: Factory Pattern, Builder Pattern.

This module handles:
- Create TwoPassPipeline with sensible defaults
- Configure strategies
- Set up observers

EXTRACTED FROM: two_pass_pipeline.py (lines 2040-end, 66 lines)
"""

from typing import Optional, Callable, Dict, Any

from two_pass.pipeline import TwoPassPipeline
from two_pass.strategies import FirstPassStrategy, SecondPassStrategy
from pipeline_observer import PipelineObservable

class TwoPassPipelineFactory:
    """
    Factory for creating pre-configured two-pass pipelines.

    Why it exists: Simplifies pipeline creation with sensible defaults.
    Provides common configurations without manual component wiring.

    Design pattern: Factory Pattern
    """

    @staticmethod
    def create_default_pipeline(
        observable: Optional[PipelineObservable] = None,
        verbose: bool = True
    ) -> TwoPassPipeline:
        """
        Create pipeline with default strategies.

        Why needed: Most common use case - fast first pass, thorough second pass.

        Args:
            observable: Event broadcaster
            verbose: Enable logging

        Returns:
            Configured TwoPassPipeline
        """
        first_pass = FirstPassStrategy(observable=observable, verbose=verbose)
        second_pass = SecondPassStrategy(observable=observable, verbose=verbose)

        return TwoPassPipeline(
            first_pass_strategy=first_pass,
            second_pass_strategy=second_pass,
            observable=observable,
            auto_rollback=True,
            rollback_threshold=-0.1,
            verbose=verbose
        )

    @staticmethod
    def create_no_rollback_pipeline(
        observable: Optional[PipelineObservable] = None,
        verbose: bool = True
    ) -> TwoPassPipeline:
        """
        Create pipeline without auto-rollback.

        Why needed: Use case where second pass always kept (experimentation, data collection).

        Args:
            observable: Event broadcaster
            verbose: Enable logging

        Returns:
            Configured TwoPassPipeline with auto-rollback disabled
        """
        first_pass = FirstPassStrategy(observable=observable, verbose=verbose)
        second_pass = SecondPassStrategy(observable=observable, verbose=verbose)

        return TwoPassPipeline(
            first_pass_strategy=first_pass,
            second_pass_strategy=second_pass,
            observable=observable,
            auto_rollback=False,
            verbose=verbose
        )

__all__ = ['TwoPassPipelineFactory']
