#!/usr/bin/env python3
"""
Stage Notifications Package - DRY Observer Pattern Integration

WHY: Reduces 90+ lines of repetitive Observer pattern boilerplate to ~10 lines.
RESPONSIBILITY: Provide reusable notification helpers and decorators for stages.
PATTERNS:
- DRY (Don't Repeat Yourself)
- Context Manager for automatic lifecycle notifications
- Decorator for automatic completion notifications
- Facade pattern for simplified observable access

Package Structure:
- notification_helper.py: Core notification functionality
- lifecycle_manager.py: Context manager for stage lifecycle
- decorators.py: Decorators for automatic notifications

Example:
    from notifications.stage import StageNotificationHelper, notify_on_completion

    class MyStage:
        def __init__(self, observable=None):
            self.notifier = StageNotificationHelper(observable, 'my_stage')

        def execute(self, card_id, task_title):
            # Old way: 10+ lines of boilerplate
            # New way: 1 line context manager
            with self.notifier.stage_lifecycle(card_id, {'task': task_title}):
                result = self._do_work()
            return result

        @notify_on_completion()
        def _process_step(self, card_id, data):
            # Automatic notification on completion
            return {'processed': len(data)}
"""

from .notification_helper import (
    StageNotificationHelper,
    create_notification_helper,
)
from .lifecycle_manager import (
    stage_lifecycle,
    StageLifecycleContextManager,
)
from .decorators import (
    notify_on_completion,
    notify_progress_on_call,
)

# Monkey-patch lifecycle manager onto StageNotificationHelper
# WHY: Enables self.notifier.stage_lifecycle() syntax for ergonomics
StageNotificationHelper.stage_lifecycle = property(
    lambda self: StageLifecycleContextManager(self)
)

__all__ = [
    # Core helper
    "StageNotificationHelper",
    "create_notification_helper",
    # Context managers
    "stage_lifecycle",
    "StageLifecycleContextManager",
    # Decorators
    "notify_on_completion",
    "notify_progress_on_call",
]
