#!/usr/bin/env python3
"""
Module: complexity_analyzer.py

WHY this module exists:
    Determines project complexity from context for dynamic pipeline selection.

RESPONSIBILITY:
    - Analyze task context to determine complexity level
    - Map story points to ProjectComplexity enum
    - Provide complexity thresholds configuration

PATTERNS:
    - Strategy Pattern for complexity determination
    - Configuration-driven threshold mapping
"""

from typing import Dict, Any
from dynamic_pipeline import ProjectComplexity


class ComplexityAnalyzer:
    """
    Analyzes task context to determine project complexity.

    WHY: Centralizes complexity determination logic used by dynamic pipeline
    for adaptive stage selection.

    RESPONSIBILITY: Map task characteristics to ProjectComplexity enum

    PATTERNS: Strategy pattern for configurable complexity mapping
    """

    def __init__(
        self,
        simple_threshold: int = 3,
        complex_threshold: int = 8
    ):
        """
        Initialize complexity analyzer.

        Args:
            simple_threshold: Maximum story points for simple complexity
            complex_threshold: Minimum story points for complex complexity
        """
        self.simple_threshold = simple_threshold
        self.complex_threshold = complex_threshold

    def analyze(self, context: Dict[str, Any]) -> ProjectComplexity:
        """
        Determine project complexity from context.

        WHY: Maps task characteristics to ProjectComplexity enum for
        dynamic pipeline stage selection.

        Args:
            context: Execution context with task details

        Returns:
            ProjectComplexity enum value
        """
        card = context.get("card", {})
        story_points = card.get("story_points", card.get("points", 5))

        # Map story points to complexity using dispatch table
        # WHY dispatch table: Declarative, easy to configure
        complexity_thresholds = [
            (self.complex_threshold, ProjectComplexity.COMPLEX),
            (self.simple_threshold + 2, ProjectComplexity.MODERATE),
            (0, ProjectComplexity.SIMPLE)
        ]

        return next(
            complexity for threshold, complexity in complexity_thresholds
            if story_points > threshold
        )
