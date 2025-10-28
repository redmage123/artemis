#!/usr/bin/env python3
"""
Module: event_emitter.py

WHY this module exists:
    Provides unified event emission for pipeline execution events.

RESPONSIBILITY:
    - Emit execution start/complete/failed events
    - Format event data consistently
    - Integrate with pipeline observer system

PATTERNS:
    - Observer Pattern for event notifications
    - Guard clauses for optional observable
"""

from typing import Dict, Any, Optional
from datetime import datetime
from pipeline_observer import PipelineObservable, PipelineEvent, EventType
from advanced_pipeline.pipeline_mode import PipelineMode


class EventEmitter:
    """
    Emits pipeline execution events to observers.

    WHY: Unified event emission for all execution modes. Enables
    monitoring and debugging of advanced pipeline features.

    RESPONSIBILITY: Emit consistent events for pipeline lifecycle

    PATTERNS: Observer pattern for loose coupling
    """

    def __init__(self, observable: Optional[PipelineObservable] = None):
        """
        Initialize event emitter.

        Args:
            observable: Optional pipeline observable for events
        """
        self.observable = observable

    def emit_execution_started(
        self,
        mode: PipelineMode,
        context: Dict[str, Any]
    ) -> None:
        """
        Emit execution started event.

        Args:
            mode: Execution mode
            context: Execution context
        """
        self._emit_event("execution_started", mode, context)

    def emit_execution_completed(
        self,
        mode: PipelineMode,
        context: Dict[str, Any],
        result: Dict[str, Any]
    ) -> None:
        """
        Emit execution completed event.

        Args:
            mode: Execution mode
            context: Execution context
            result: Execution result
        """
        self._emit_event("execution_completed", mode, context, result)

    def emit_execution_failed(
        self,
        mode: PipelineMode,
        context: Dict[str, Any],
        error: str
    ) -> None:
        """
        Emit execution failed event.

        Args:
            mode: Execution mode
            context: Execution context
            error: Error message
        """
        self._emit_event("execution_failed", mode, context, {"error": error})

    def _emit_event(
        self,
        event_type: str,
        mode: PipelineMode,
        context: Dict[str, Any],
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Emit pipeline execution event.

        WHY: Unified event emission for all execution modes. Enables
        monitoring and debugging of advanced pipeline features.

        Args:
            event_type: Type of execution event
            mode: Execution mode
            context: Execution context
            data: Additional event data
        """
        # Guard clause: check if observable configured
        if not self.observable:
            return

        event_data = {
            "event_type": event_type,
            "mode": mode.value,
            "timestamp": datetime.now().isoformat(),
            **(data or {})
        }

        event = PipelineEvent(
            event_type=EventType.STAGE_PROGRESS,
            card_id=context.get("card_id"),
            stage_name="AdvancedPipelineStrategy",
            data=event_data
        )

        self.observable.notify(event)
