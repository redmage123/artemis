from artemis_logger import get_logger
logger = get_logger('notification_observer')
'\nModule: observer/notification_observer.py\n\nWHY: Sends notifications for important events to external systems\n     (Slack, email, webhooks, Discord). Filters events to only notify\n     on significant events.\n\nRESPONSIBILITY:\n    - Filter events to identify important ones\n    - Format notification messages\n    - Store notification history\n    - Provide extensible notification interface\n\nPATTERNS:\n    - Observer pattern implementation\n    - Strategy pattern for notification formatting\n    - Filter pattern for event importance\n\nDESIGN DECISIONS:\n    - Only notify on important events to prevent noise\n    - Store all notifications for audit trail\n    - Verbose mode prints to console for debugging\n    - Extensible design allows adding notification channels\n'
from typing import Dict, Any, List
from .observer_interface import PipelineObserver
from .event_model import PipelineEvent
from .event_types import EventType

class NotificationObserver(PipelineObserver):
    """
    Observer that sends notifications for important events.

    Can be extended to send:
    - Slack notifications
    - Email alerts
    - Webhook calls
    - Discord messages
    """

    def __init__(self, verbose: bool=True):
        self.verbose = verbose
        self.notifications: List[Dict[str, Any]] = []

    def on_event(self, event: PipelineEvent) -> None:
        """Send notifications for important events"""
        if not self._is_important_event(event):
            return
        notification = {'type': event.event_type.value, 'timestamp': event.timestamp.isoformat(), 'card_id': event.card_id, 'stage_name': event.stage_name, 'message': self._format_notification(event)}
        self.notifications.append(notification)
        if self.verbose:
            
            logger.log(f"[Notification] {notification['message']}", 'INFO')

    def _is_important_event(self, event: PipelineEvent) -> bool:
        """Check if event is important enough to notify"""
        important_events = [EventType.PIPELINE_COMPLETED, EventType.PIPELINE_FAILED, EventType.STAGE_FAILED, EventType.INTEGRATION_CONFLICT]
        return event.event_type in important_events

    def _format_notification(self, event: PipelineEvent) -> str:
        """Format notification message"""
        if event.event_type == EventType.PIPELINE_COMPLETED:
            return f'Pipeline completed successfully for {event.card_id}'
        if event.event_type == EventType.PIPELINE_FAILED:
            return f'Pipeline failed for {event.card_id}: {event.error}'
        if event.event_type == EventType.STAGE_FAILED:
            return f'Stage {event.stage_name} failed for {event.card_id}: {event.error}'
        if event.event_type == EventType.INTEGRATION_CONFLICT:
            return f'Integration conflict in {event.card_id}'
        return f'Event: {event.event_type.value}'

    def get_notifications(self) -> List[Dict[str, Any]]:
        """Get all notifications"""
        return self.notifications.copy()