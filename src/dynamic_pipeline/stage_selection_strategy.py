#!/usr/bin/env python3
"""
Module: stage_selection_strategy.py

WHY: Different projects require different pipeline stages. A simple script doesn't need
     extensive validation, while an enterprise system needs all quality gates.

RESPONSIBILITY: Define the strategy interface for dynamic stage selection.

PATTERNS:
    - Strategy Pattern: Encapsulates stage selection algorithms
    - Open/Closed: New selection strategies can be added without modification
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List

from dynamic_pipeline.pipeline_stage import PipelineStage


class StageSelectionStrategy(ABC):
    """
    Strategy for selecting which stages to include in pipeline.

    Why it exists: Encapsulates stage selection logic, allowing different
    selection algorithms (complexity-based, resource-based, user-defined).

    Design pattern: Strategy Pattern

    Responsibilities:
    - Analyze project/context to select appropriate stages
    - Return ordered list of stages to execute
    - Provide rationale for selections (logging/debugging)
    """

    @abstractmethod
    def select_stages(
        self,
        available_stages: List[PipelineStage],
        context: Dict[str, Any]
    ) -> List[PipelineStage]:
        """
        Select which stages to include based on strategy.

        Why needed: Core strategy method. Different implementations provide
        different selection logic (complexity, resources, manual).

        Args:
            available_stages: All possible stages
            context: Decision context (complexity, resources, config)

        Returns:
            Ordered list of selected stages
        """
        pass
