#!/usr/bin/env python3
"""
Stage Lifecycle Manager - Context manager for stage lifecycle events

WHY: Automates STAGE_STARTED/COMPLETED/FAILED notifications.
RESPONSIBILITY: Manage stage lifecycle events with exception handling.
PATTERNS:
- Context Manager pattern for automatic resource management
- Observer pattern integration for event notifications
- Exception handling with automatic failure notifications

Example:
    with self.notifier.stage_lifecycle(card_id, {'task': task_title}):
        # STAGE_STARTED sent automatically
        result = self._do_work()
        # STAGE_COMPLETED sent automatically on success
        # STAGE_FAILED sent automatically on exception
"""

from contextlib import contextmanager
from typing import Any, Dict, Optional, TYPE_CHECKING

from pipeline_observer import EventType

if TYPE_CHECKING:
    from .notification_helper import StageNotificationHelper


@contextmanager
def stage_lifecycle(
    notifier: "StageNotificationHelper",
    card_id: str,
    initial_data: Optional[Dict[str, Any]] = None
):
    """
    Context manager for automatic stage lifecycle notifications.

    WHY: Eliminates try/finally boilerplate for stage event notifications.
    RESPONSIBILITY: Send STARTED/COMPLETED/FAILED events automatically.
    PATTERNS: Context Manager pattern ensures notifications even on exceptions.

    Automatically sends:
    - STAGE_STARTED when entering context
    - STAGE_COMPLETED when exiting normally
    - STAGE_FAILED when exception occurs

    PERFORMANCE: Minimal overhead, events only sent if observable exists.

    Args:
        notifier: StageNotificationHelper instance
        card_id: Card ID for notifications
        initial_data: Optional data for STAGE_STARTED event

    Yields:
        notifier (for method chaining if needed)

    Example:
        with stage_lifecycle(self.notifier, card_id, {'task': 'analysis'}):
            result = self._analyze_code()
            # STAGE_COMPLETED sent automatically here
    """
    # Send STAGE_STARTED on entry
    notifier.notify(EventType.STAGE_STARTED, card_id, initial_data)

    try:
        yield notifier
    except Exception as e:
        # Send STAGE_FAILED on exception
        notifier.notify(EventType.STAGE_FAILED, card_id, {
            'error': str(e),
            'error_type': type(e).__name__
        })
        raise
    else:
        # Send STAGE_COMPLETED on success
        notifier.notify(EventType.STAGE_COMPLETED, card_id)


class StageLifecycleContextManager:
    """
    Context manager wrapper for stage lifecycle events.

    WHY: Provides instance method version of lifecycle manager.
    RESPONSIBILITY: Bridge between StageNotificationHelper and context manager.
    PATTERNS: Wrapper pattern around module-level context manager.

    This class allows the lifecycle manager to be used as an instance method
    on StageNotificationHelper while keeping the core logic separate.
    """

    def __init__(self, notifier: "StageNotificationHelper"):
        """
        Initialize lifecycle context manager.

        Args:
            notifier: StageNotificationHelper instance to wrap
        """
        self.notifier = notifier

    @contextmanager
    def __call__(self, card_id: str, initial_data: Optional[Dict[str, Any]] = None):
        """
        Make instance callable as context manager.

        WHY: Enables usage as self.notifier.stage_lifecycle(card_id, data)
        """
        with stage_lifecycle(self.notifier, card_id, initial_data) as notifier:
            yield notifier
