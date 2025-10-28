#!/usr/bin/env python3
"""
WHY: Notify observers of developer lifecycle events (started, completed, failed)
RESPONSIBILITY: Emit pipeline events for developer state changes
PATTERNS: Observer (event notification), Event Sourcing (lifecycle tracking)

Event notification provides:
- Developer started events
- Developer completed events
- Developer failed events
- Event data propagation to observers
"""

from typing import Dict, Optional
from pipeline_observer import PipelineObservable, EventBuilder, PipelineEvent, EventType


class DeveloperEventNotifier:
    """
    Notifies observers of developer events

    Emits events for developer lifecycle (started, completed, failed).
    """

    def __init__(self, observable: Optional[PipelineObservable] = None):
        """
        Initialize event notifier

        Args:
            observable: Pipeline observable for event emission
        """
        self.observable = observable

    def notify_developer_started(
        self,
        card_id: str,
        developer_name: str,
        developer_type: str,
        task_title: str
    ) -> None:
        """
        Notify that developer has started

        Args:
            card_id: Kanban card ID
            developer_name: Name of developer
            developer_type: Type of developer (conservative/aggressive/innovative)
            task_title: Task title
        """
        # Guard clause - check if observable exists
        if not self.observable:
            return

        event = EventBuilder.developer_started(
            card_id,
            developer_name,
            developer_type=developer_type,
            task_title=task_title
        )
        self.observable.notify(event)

    def notify_developer_completed(
        self,
        card_id: str,
        developer_name: str,
        files_created: int,
        result: Dict
    ) -> None:
        """
        Notify that developer has completed successfully

        Args:
            card_id: Kanban card ID
            developer_name: Name of developer
            files_created: Number of files created
            result: Developer result data
        """
        # Guard clause - check if observable exists
        if not self.observable:
            return

        event = EventBuilder.developer_completed(
            card_id,
            developer_name,
            files_created=files_created,
            result=result
        )
        self.observable.notify(event)

    def notify_developer_failed(
        self,
        card_id: str,
        developer_name: str,
        error: Exception,
        result: Dict
    ) -> None:
        """
        Notify that developer has failed

        Args:
            card_id: Kanban card ID
            developer_name: Name of developer
            error: Exception that caused failure
            result: Developer result data (with error details)
        """
        # Guard clause - check if observable exists
        if not self.observable:
            return

        event = PipelineEvent(
            event_type=EventType.DEVELOPER_FAILED,
            card_id=card_id,
            developer_name=developer_name,
            error=error,
            data=result
        )
        self.observable.notify(event)
