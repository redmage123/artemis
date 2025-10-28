#!/usr/bin/env python3
"""
Module: observer/logging_observer.py

WHY: Provides detailed logging of pipeline execution by observing
     all pipeline events and routing them to appropriate log levels.

RESPONSIBILITY:
    - Log all pipeline events at appropriate levels
    - Determine log level based on event type (ERROR/SUCCESS/INFO/DEBUG)
    - Format log messages with relevant context

PATTERNS:
    - Observer pattern implementation
    - Strategy pattern for log level determination
    - Template method for message formatting

DESIGN DECISIONS:
    - Failed events log at ERROR level for visibility
    - Completed events log at SUCCESS level for positive feedback
    - Started events log at INFO level for execution tracking
    - Other events log at DEBUG level to reduce noise
"""

from artemis_services import PipelineLogger

from .observer_interface import PipelineObserver
from .event_model import PipelineEvent


class LoggingObserver(PipelineObserver):
    """
    Observer that logs all pipeline events.

    Provides detailed logging of pipeline execution.
    """

    def __init__(self, verbose: bool = True):
        self.logger = PipelineLogger(verbose=verbose)

    def on_event(self, event: PipelineEvent) -> None:
        """Log pipeline event"""
        level = self._determine_log_level(event)
        message = self._format_log_message(event)
        self.logger.log(message, level)

    def _determine_log_level(self, event: PipelineEvent) -> str:
        """Determine appropriate log level based on event type"""
        event_value = event.event_type.value

        if event_value.endswith("_failed"):
            return "ERROR"

        if event_value.endswith("_completed"):
            return "SUCCESS"

        if event_value.endswith("_started"):
            return "INFO"

        return "DEBUG"

    def _format_log_message(self, event: PipelineEvent) -> str:
        """Format log message from event"""
        parts = [event.event_type.value.upper()]

        if event.card_id:
            parts.append(f"card_id={event.card_id}")

        if event.stage_name:
            parts.append(f"stage={event.stage_name}")

        if event.developer_name:
            parts.append(f"developer={event.developer_name}")

        if event.error:
            parts.append(f"error={event.error}")

        return " | ".join(parts)
