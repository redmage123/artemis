#!/usr/bin/env python3
"""
Stage Notification Helper - Core notification functionality

WHY: Reduces Observer pattern boilerplate in stages from 10+ lines to 1 line.
RESPONSIBILITY: Send pipeline events with minimal code in stage implementations.
PATTERNS:
- Helper pattern for DRY (Don't Repeat Yourself)
- Facade pattern wrapping PipelineObservable complexity
- Null Object pattern (gracefully handles None observable)

Example:
    # Without helper (10 lines):
    if self.observable:
        event = PipelineEvent(
            event_type=EventType.STAGE_STARTED,
            card_id=card_id,
            stage_name="my_stage",
            data={"key": "value"}
        )
        self.observable.notify(event)

    # With helper (1 line):
    self.notifier.notify(EventType.STAGE_STARTED, card_id, {'key': 'value'})
"""

from typing import Any, Dict, Optional
from pipeline_observer import PipelineObservable, PipelineEvent, EventType


class StageNotificationHelper:
    """
    Helper class to simplify stage event notifications.

    WHY: Eliminates repetitive event creation and null-checking boilerplate.
    RESPONSIBILITY: Encapsulate event creation and notification logic.
    PATTERNS: Facade pattern (simplified interface to PipelineObservable)

    Attributes:
        observable: Optional PipelineObservable for event notifications
        stage_name: Name of the stage for event identification
    """

    def __init__(self, observable: Optional[PipelineObservable], stage_name: str):
        """
        Initialize notification helper.

        WHY: Encapsulates observable and stage_name for DRY notifications.

        Args:
            observable: PipelineObservable instance or None (Null Object pattern)
            stage_name: Name of the stage for event identification
        """
        self.observable = observable
        self.stage_name = stage_name

    def notify(
        self,
        event_type: EventType,
        card_id: str,
        data: Dict[str, Any] = None,
        **kwargs
    ) -> None:
        """
        Send notification if observable is available.

        WHY: Single point for event creation and notification (DRY).
        PERFORMANCE: Early return avoids event creation when no observers.

        Args:
            event_type: Type of event (STAGE_STARTED, STAGE_PROGRESS, etc.)
            card_id: Card ID for the event
            data: Event data dictionary (default: empty dict)
            **kwargs: Additional keyword arguments passed to PipelineEvent
        """
        # Guard clause: No observable, no notification (Null Object pattern)
        if not self.observable:
            return

        # Create and send event
        event = PipelineEvent(
            event_type=event_type,
            card_id=card_id,
            stage_name=self.stage_name,
            data=data or {},
            **kwargs
        )
        self.observable.notify(event)

    def notify_progress(
        self,
        card_id: str,
        step: str,
        progress_percent: int,
        **extra_data
    ) -> None:
        """
        Convenience method for progress notifications.

        WHY: Standardizes progress event format across all stages.
        PERFORMANCE: Direct notification without intermediate steps.

        Args:
            card_id: Card ID
            step: Current step name
            progress_percent: Progress percentage (0-100)
            **extra_data: Additional data to include in event
        """
        data = {
            'step': step,
            'progress_percent': progress_percent,
            **extra_data
        }
        self.notify(EventType.STAGE_PROGRESS, card_id, data)


def create_notification_helper(
    observable: Optional[PipelineObservable],
    stage_name: str
) -> StageNotificationHelper:
    """
    Factory function to create notification helper.

    WHY: Provides clear entry point for stage initialization.
    PATTERNS: Factory pattern for consistent object creation.

    Args:
        observable: PipelineObservable instance or None
        stage_name: Name of the stage

    Returns:
        StageNotificationHelper instance
    """
    return StageNotificationHelper(observable, stage_name)
