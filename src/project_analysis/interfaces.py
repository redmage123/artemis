#!/usr/bin/env python3
"""
WHY: Abstract interface for dimension analyzers
RESPONSIBILITY: Define contract for all analyzer implementations
PATTERNS: Abstract Base Class, Interface Segregation Principle

This module provides the base interface that all dimension analyzers must implement,
ensuring consistent behavior and enabling polymorphic usage across the system.
"""

from abc import ABC, abstractmethod
from typing import Dict

from project_analysis.models import AnalysisResult


class DimensionAnalyzer(ABC):
    """
    WHY: Interface Segregation Principle - minimal, focused interface
    RESPONSIBILITY: Define contract for dimension-specific analyzers
    PATTERNS: Abstract Base Class, Strategy Pattern

    Abstract base class for dimension analyzers. Each analyzer implements ONE
    dimension analysis (Single Responsibility Principle), allowing the system
    to be extended without modification (Open/Closed Principle).

    All analyzers can be used polymorphically through this interface, supporting
    Liskov Substitution Principle.
    """

    @abstractmethod
    def analyze(self, card: Dict, context: Dict) -> AnalysisResult:
        """
        Analyze task in this dimension.

        Args:
            card: Kanban card containing task information
            context: Pipeline context (RAG recommendations, etc.)

        Returns:
            AnalysisResult with dimension-specific issues and recommendations
        """
        pass

    @abstractmethod
    def get_dimension_name(self) -> str:
        """
        Return dimension name for identification and reporting.

        Returns:
            String identifier for this analysis dimension
        """
        pass
