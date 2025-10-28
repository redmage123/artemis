#!/usr/bin/env python3
"""
Notifications Package - Event notification utilities

WHY: Centralized location for all notification-related functionality.
RESPONSIBILITY: Package-level exports for notification components.

Subpackages:
- stage: Stage lifecycle notification helpers and decorators
"""

from .stage import (
    StageNotificationHelper,
    create_notification_helper,
    notify_on_completion,
    notify_progress_on_call,
    stage_lifecycle,
    StageLifecycleContextManager,
)

__all__ = [
    # Stage notifications
    "StageNotificationHelper",
    "create_notification_helper",
    "notify_on_completion",
    "notify_progress_on_call",
    "stage_lifecycle",
    "StageLifecycleContextManager",
]
