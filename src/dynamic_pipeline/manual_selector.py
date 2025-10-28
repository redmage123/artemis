#!/usr/bin/env python3
"""
Module: manual_selector.py

WHY: Users need explicit control over pipeline stages for debugging, testing, or
     custom workflows that don't fit automated selection strategies.

RESPONSIBILITY: Select stages based on explicit user-provided stage names.

PATTERNS:
    - Strategy: Implements user-controlled stage selection
    - Set-based Filtering: O(1) membership checks for efficiency
    - Validation: Warns about missing stages to prevent silent failures
"""

from typing import Dict, Any, List, Set, Optional

from artemis_exceptions import PipelineException, wrap_exception
from artemis_services import PipelineLogger
from dynamic_pipeline.pipeline_stage import PipelineStage
from dynamic_pipeline.stage_selection_strategy import StageSelectionStrategy


class ManualSelector(StageSelectionStrategy):
    """
    Selects stages based on explicit user configuration.

    Why it exists: Users may want specific stage combinations for
    debugging, testing, or custom workflows.

    Design pattern: Strategy implementation
    """

    def __init__(self, selected_stage_names: List[str], logger: Optional[PipelineLogger] = None):
        self.selected_stage_names = set(selected_stage_names)  # O(1) lookup
        self.logger = logger or PipelineLogger(verbose=True)

    @wrap_exception(PipelineException, "Failed to select stages manually")
    def select_stages(
        self,
        available_stages: List[PipelineStage],
        context: Dict[str, Any]
    ) -> List[PipelineStage]:
        """Select stages matching configured names"""

        # Filter stages by name using set membership (O(1) per check)
        selected = [
            stage for stage in available_stages
            if stage.name in self.selected_stage_names
        ]

        # Warn about missing stages using set difference
        available_names = {stage.name for stage in available_stages}
        missing = self.selected_stage_names - available_names

        if missing:
            self.logger.log(
                f"Warning: Requested stages not found: {missing}",
                "WARNING"
            )

        self.logger.log(
            f"Manually selected {len(selected)}/{len(available_stages)} stages",
            "INFO"
        )

        return selected
