#!/usr/bin/env python3
"""
Validation Event Notifier

WHY: Real-time validation monitoring enables dashboards, metrics collection,
     and supervisor learning from validation patterns (Observer Pattern).

RESPONSIBILITY:
- Notify observers of validation events
- Handle event serialization and delivery
- Graceful degradation if observer unavailable

PATTERNS:
- Observer Pattern: Decouple validation from monitoring
- Guard Clauses: Early returns to avoid nested conditionals
- Null Object Pattern: Safe handling of missing observers
"""

from typing import Dict, Optional, Any


class ValidationEventNotifier:
    """
    Notifies observers of validation events using Observer Pattern.

    WHY: Enables real-time monitoring of validation during code generation:
         - UI dashboards show live validation status
         - Supervisor learns from validation patterns
         - Metrics collectors track hallucination trends
    """

    def __init__(self, observable: Optional[Any], developer_name: str, logger: Optional[Any] = None):
        """
        Initialize event notifier.

        Args:
            observable: Observable instance for event notifications (can be None)
            developer_name: Name of developer agent
            logger: Logger instance for debugging
        """
        self.observable = observable
        self.developer_name = developer_name
        self.logger = logger

    def notify_validation_event(self, event_type: str, data: Dict) -> None:
        """
        Notify observers of validation events.

        Args:
            event_type: Type of validation event (validation_started, validation_passed, etc.)
            data: Event data including stage, attempt, feedback, score
        """
        # Guard: No observable available
        if not self.observable:
            return

        try:
            # Try to use EventBuilder from pipeline_observer
            event = self._build_event_with_pipeline_observer(event_type, data)
            self.observable.notify(event)

        except Exception as e:
            # Don't fail if observer notification fails
            self._log_notification_error(e)

    def notify_rag_validation_event(self, rag_result: Any, passed: bool) -> None:
        """
        Notify observers of RAG validation events.

        Args:
            rag_result: RAG validation result
            passed: Whether validation passed
        """
        # Guard: No observable available
        if not self.observable:
            return

        try:
            # Try to use EventBuilder from pipeline_observer
            event = self._build_rag_event_with_pipeline_observer(rag_result, passed)
            self.observable.notify(event)

        except Exception as e:
            self._log_notification_error(e)

    def notify_self_critique_event(self, event_type: str, data: Dict) -> None:
        """
        Notify observers of self-critique events.

        Uses graceful degradation - tries EventBuilder, falls back to plain dict.

        Args:
            event_type: Type of event (critique_started, critique_passed, etc.)
            data: Event data
        """
        # Guard: No observable available
        if not self.observable:
            return

        try:
            # Try EventBuilder first
            event = self._build_event_with_pipeline_observer(
                f'self_critique_{event_type}',
                data
            )
            self.observable.notify(event)

        except ImportError:
            # Fallback: Notify with plain dict
            event = {
                'type': f'self_critique_{event_type}',
                'developer': self.developer_name,
                **data
            }
            self.observable.notify(event)

        except Exception as e:
            # Silent fail - don't break validation for notification errors
            self._log_notification_error(e, level="DEBUG")

    def _build_event_with_pipeline_observer(self, event_type: str, data: Dict) -> Dict:
        """
        Build event using EventBuilder from pipeline_observer.

        Args:
            event_type: Event type
            data: Event data

        Returns:
            Built event dictionary

        Raises:
            ImportError: If pipeline_observer not available
        """
        from pipeline_observer import EventBuilder

        return EventBuilder.validation_event(
            developer_name=self.developer_name,
            event_type=event_type,
            validation_data=data
        )

    def _build_rag_event_with_pipeline_observer(self, rag_result: Any, passed: bool) -> Dict:
        """
        Build RAG validation event using EventBuilder.

        Args:
            rag_result: RAG validation result
            passed: Whether validation passed

        Returns:
            Built event dictionary

        Raises:
            ImportError: If pipeline_observer not available
        """
        from pipeline_observer import EventBuilder

        return EventBuilder.rag_validation_event(
            developer_name=self.developer_name,
            rag_result=rag_result,
            passed=passed
        )

    def _log_notification_error(self, error: Exception, level: str = "DEBUG") -> None:
        """
        Log notification error (doesn't raise - graceful degradation).

        Args:
            error: Exception that occurred
            level: Log level (DEBUG, INFO, WARNING, ERROR)
        """
        if not self.logger:
            return

        self.logger.log(f"Observer notification failed: {error}", level)
