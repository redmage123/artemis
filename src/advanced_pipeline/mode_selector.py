#!/usr/bin/env python3
"""
Module: mode_selector.py

WHY this module exists:
    Facade for mode selection with strategy pattern support. Provides simple
    interface while supporting multiple selection strategies.

RESPONSIBILITY:
    - Manage selection strategy
    - Select mode for given task
    - Log selection rationale
    - Emit selection events
    - Provide default strategy (automatic)

PATTERNS:
    - Facade Pattern: Simple interface for complex functionality
    - Strategy Pattern: Delegate to pluggable strategies
    - Observer Pattern: Event emission
"""

from typing import Dict, Any, Optional
from datetime import datetime

from pipeline_observer import PipelineObservable, PipelineEvent, EventType
from artemis_exceptions import PipelineException, wrap_exception
from artemis_services import PipelineLogger
from advanced_pipeline.pipeline_mode import PipelineMode
from advanced_pipeline.pipeline_config import AdvancedPipelineConfig
from advanced_pipeline.mode_selection_strategy import ModeSelectionStrategy
from advanced_pipeline.automatic_mode_selector import AutomaticModeSelector


class ModeSelector:
    """
    Facade for mode selection with strategy pattern.

    WHY: Provides simple interface for mode selection while supporting
    multiple selection strategies (manual, automatic, custom).

    Design pattern: Facade + Strategy

    Responsibilities:
        - Manage selection strategy
        - Select mode for given task
        - Log selection rationale
        - Emit selection events
    """

    def __init__(
        self,
        config: AdvancedPipelineConfig,
        strategy: Optional[ModeSelectionStrategy] = None,
        observable: Optional[PipelineObservable] = None
    ):
        """
        Initialize mode selector.

        Args:
            config: Pipeline configuration
            strategy: Selection strategy (uses AutomaticModeSelector if None)
            observable: Pipeline observable for events
        """
        self.config = config
        self.observable = observable
        self.logger = PipelineLogger(verbose=True)

        # Use provided strategy or create automatic selector
        self.strategy = strategy or AutomaticModeSelector(config, self.logger)

    @wrap_exception(PipelineException, "Mode selection failed")
    def select_mode(self, context: Dict[str, Any]) -> PipelineMode:
        """
        Select execution mode for task.

        WHAT: Delegates to configured strategy, logs selection, emits event.

        Args:
            context: Task context

        Returns:
            Selected PipelineMode
        """
        # Guard clause: if auto mode selection disabled, use STANDARD
        if not self.config.auto_mode_selection:
            return PipelineMode.STANDARD

        # Delegate to strategy
        selected_mode = self.strategy.select_mode(context)

        # Emit mode selection event
        self._emit_mode_selection_event(selected_mode, context)

        return selected_mode

    def _emit_mode_selection_event(
        self,
        mode: PipelineMode,
        context: Dict[str, Any]
    ) -> None:
        """
        Emit mode selection event.

        WHY: Allows monitoring of mode selection decisions for analysis
        and debugging.

        Args:
            mode: Selected mode
            context: Task context
        """
        # Guard clause: check if observable configured
        if not self.observable:
            return

        event_data = {
            "event_type": "mode_selected",
            "mode": mode.value,
            "card_id": context.get("card_id"),
            "timestamp": datetime.now().isoformat()
        }

        event = PipelineEvent(
            event_type=EventType.STAGE_PROGRESS,
            stage_name="ModeSelector",
            data=event_data
        )

        self.observable.notify(event)
