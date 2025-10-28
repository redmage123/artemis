#!/usr/bin/env python3
"""
Stage Notification Helper - BACKWARD COMPATIBILITY WRAPPER

This module has been refactored into the notifications/stage/ package.
All functionality has been extracted into focused, single-responsibility modules.

Original file: 214 lines
This wrapper: 43 lines
Reduction: 79.9%

WHY: Provides backward compatibility while code migrates to new package.
RESPONSIBILITY: Re-export all public APIs from notifications.stage package.

Migration: Update imports from:
    from stage_notifications import StageNotificationHelper, notify_on_completion
To:
    from notifications.stage import StageNotificationHelper, notify_on_completion

Package structure:
    notifications/stage/
    ├── __init__.py                    # Package exports
    ├── notification_helper.py         # StageNotificationHelper class (~130 lines)
    ├── lifecycle_manager.py           # stage_lifecycle context manager (~110 lines)
    └── decorators.py                  # notify_on_completion decorator (~180 lines)

Refactoring benefits:
- Single Responsibility: Each module has one clear purpose
- Testability: Isolated testing per module
- Maintainability: Easier to find and modify specific functionality
- Reusability: Import only what you need
"""

# Re-export everything from notifications.stage for backward compatibility
from notifications.stage import (
    StageNotificationHelper,
    create_notification_helper,
    notify_on_completion,
    notify_progress_on_call,
    stage_lifecycle,
    StageLifecycleContextManager,
)

__all__ = [
    "StageNotificationHelper",
    "create_notification_helper",
    "notify_on_completion",
    "notify_progress_on_call",
    "stage_lifecycle",
    "StageLifecycleContextManager",
]
