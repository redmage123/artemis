#!/usr/bin/env python3
"""
WHY: Provide factory for creating failure analyzers
RESPONSIBILITY: Create configured analyzer instances
PATTERNS: Factory (creation abstraction), Open/Closed Principle

Factory enables different analyzer configurations without code changes.
"""

from typing import Optional
from artemis_stage_interface import LoggerInterface
from validation.analyzer import ValidationFailureAnalyzer


class FailureAnalyzerFactory:
    """
    Factory for creating failure analyzers

    WHY: Enables different analyzer configurations without code changes.
    PATTERNS: Factory pattern (Open/Closed principle).
    """

    @staticmethod
    def create_analyzer(logger: Optional[LoggerInterface] = None) -> ValidationFailureAnalyzer:
        """
        Create failure analyzer

        Args:
            logger: Optional logger

        Returns:
            ValidationFailureAnalyzer instance
        """
        return ValidationFailureAnalyzer(logger=logger)
