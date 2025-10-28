#!/usr/bin/env python3
"""
Stage Notification Decorators - Automatic notifications for methods

WHY: Enables declarative notification on method completion.
RESPONSIBILITY: Decorator-based automatic notifications.
PATTERNS:
- Decorator pattern for cross-cutting concerns
- Strategy pattern for data extraction
- DRY principle for notification logic

Example:
    @notify_on_completion()
    def _process_features(self, card_id, features):
        return {'features_count': len(features)}
        # STAGE_COMPLETED sent automatically with return value

    @notify_on_completion(data_extractor=lambda result: {'count': result})
    def _count_items(self, card_id, items):
        return len(items)
        # STAGE_COMPLETED sent with extracted data
"""

from functools import wraps
from typing import Any, Callable, Dict, Optional

from pipeline_observer import EventType


def notify_on_completion(
    event_type: EventType = EventType.STAGE_COMPLETED,
    data_extractor: Optional[Callable[[Any], Dict[str, Any]]] = None
) -> Callable:
    """
    Decorator to automatically send notifications after method completes.

    WHY: Reduces repetitive notification code at end of methods.
    RESPONSIBILITY: Wrap method to add automatic notification behavior.
    PATTERNS: Decorator pattern for cross-cutting concerns.

    PERFORMANCE: Minimal overhead, only creates event if notifier exists.

    Args:
        event_type: Type of event to send (default: STAGE_COMPLETED)
        data_extractor: Optional function to extract data from result
                       Signature: (result: Any) -> Dict[str, Any]

    Returns:
        Decorated function that sends notification on completion

    Example:
        # Automatic notification with dict return
        @notify_on_completion()
        def process(self, card_id, data):
            return {'processed': len(data)}

        # Custom data extraction from non-dict return
        @notify_on_completion(data_extractor=lambda x: {'value': x})
        def calculate(self, card_id, nums):
            return sum(nums)

        # Custom event type
        @notify_on_completion(event_type=EventType.STAGE_PROGRESS)
        def step(self, card_id, step_num):
            return {'step': step_num}
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, card_id: str, *args, **kwargs) -> Any:
            """
            Wrapper that executes method and sends notification.

            WHY: Separates business logic from notification concerns.
            PERFORMANCE: Early return if no notifier (no event creation).
            """
            # Execute original method
            result = func(self, card_id, *args, **kwargs)

            # Guard clause: No notifier, skip notification
            if not (hasattr(self, 'notifier') and self.notifier):
                return result

            # Extract notification data from result
            notification_data = _extract_notification_data(result, data_extractor)

            # Send notification
            self.notifier.notify(event_type, card_id, notification_data)

            return result

        return wrapper
    return decorator


def _extract_notification_data(
    result: Any,
    data_extractor: Optional[Callable[[Any], Dict[str, Any]]]
) -> Dict[str, Any]:
    """
    Extract notification data from method result.

    WHY: Centralizes data extraction logic for DRY.
    RESPONSIBILITY: Convert method result to notification data dict.
    PATTERNS: Strategy pattern with data_extractor function.

    PERFORMANCE: Direct dict return for dict results (no conversion).

    Args:
        result: Method return value
        data_extractor: Optional function to extract data from result

    Returns:
        Dictionary suitable for event notification

    Example:
        # With custom extractor
        data = _extract_notification_data(42, lambda x: {'value': x})
        # Returns: {'value': 42}

        # With dict result
        data = _extract_notification_data({'count': 5}, None)
        # Returns: {'count': 5}

        # With other type
        data = _extract_notification_data("result", None)
        # Returns: {'result': "result"}
    """
    # Strategy 1: Use custom extractor if provided
    if data_extractor:
        return data_extractor(result)

    # Strategy 2: Return dict results directly (performance)
    if isinstance(result, dict):
        return result

    # Strategy 3: Wrap other types in dict
    return {'result': result}


def notify_progress_on_call(
    step_name: str,
    progress_percent: int
) -> Callable:
    """
    Decorator to send progress notification when method is called.

    WHY: Standardizes progress reporting across stages.
    RESPONSIBILITY: Send progress event at method entry.
    PATTERNS: Decorator pattern for declarative progress tracking.

    Args:
        step_name: Name of the progress step
        progress_percent: Progress percentage (0-100)

    Returns:
        Decorated function that sends progress notification

    Example:
        @notify_progress_on_call("analyzing_code", 25)
        def _analyze_code(self, card_id):
            # Progress notification sent automatically
            return self._do_analysis()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, card_id: str, *args, **kwargs) -> Any:
            """Wrapper that sends progress notification before execution"""
            # Send progress notification if notifier exists
            if hasattr(self, 'notifier') and self.notifier:
                self.notifier.notify_progress(
                    card_id=card_id,
                    step=step_name,
                    progress_percent=progress_percent
                )

            # Execute original method
            return func(self, card_id, *args, **kwargs)

        return wrapper
    return decorator
