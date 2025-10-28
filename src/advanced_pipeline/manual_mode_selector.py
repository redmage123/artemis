#!/usr/bin/env python3
"""
Module: manual_mode_selector.py

WHY this module exists:
    Provides manual/fixed mode selection strategy for explicit control over
    pipeline execution mode.

RESPONSIBILITY:
    - Return pre-configured execution mode
    - Ignore context and always return fixed mode
    - Enable testing and explicit mode specification

PATTERNS:
    - Strategy Pattern: Concrete strategy implementation
    - Null Object Pattern: Ignores context
"""

from typing import Dict, Any

from advanced_pipeline.mode_selection_strategy import ModeSelectionStrategy
from advanced_pipeline.pipeline_mode import PipelineMode


class ManualModeSelector(ModeSelectionStrategy):
    """
    Manual mode selection - uses explicitly specified mode.

    WHY: Allows explicit control when automatic selection inappropriate.
    Useful for testing, debugging, or specific requirements.
    """

    def __init__(self, mode: PipelineMode):
        """
        Initialize with fixed mode.

        Args:
            mode: Mode to always return
        """
        self.mode = mode

    def select_mode(self, context: Dict[str, Any]) -> PipelineMode:
        """Return configured mode regardless of context."""
        return self.mode
