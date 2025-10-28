#!/usr/bin/env python3
"""
Module: mode_selection_strategy.py

WHY this module exists:
    Abstract base class for pipeline mode selection strategies. Different selection
    algorithms for different contexts.

RESPONSIBILITY:
    - Define abstract interface for mode selection
    - Provide contract for selection strategies
    - Enable strategy pattern implementation

PATTERNS:
    - Strategy Pattern: Interchangeable selection algorithms
    - Abstract Base Class: Define common interface
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

from advanced_pipeline.pipeline_mode import PipelineMode


class ModeSelectionStrategy(ABC):
    """
    Abstract strategy for selecting pipeline execution mode.

    WHY: Different selection algorithms for different contexts. Some tasks
    have explicit mode requirements, others benefit from automatic selection
    based on task characteristics.

    Design pattern: Strategy Pattern

    Responsibilities:
        - Analyze task characteristics
        - Select appropriate execution mode
        - Provide rationale for selection
    """

    @abstractmethod
    def select_mode(self, context: Dict[str, Any]) -> PipelineMode:
        """
        Select execution mode based on context.

        Args:
            context: Task context with characteristics (complexity, priority, etc.)

        Returns:
            Selected PipelineMode
        """
        pass
