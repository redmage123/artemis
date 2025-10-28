#!/usr/bin/env python3
"""
WHY: Separate progress tracking concerns from supervision logic
RESPONSIBILITY: Manage agent progress data state
PATTERNS: State Pattern, Encapsulation

This module provides a clean interface for tracking and updating agent progress
data that can be sent with heartbeats to the supervisor.

Design Decisions:
- Immutable snapshots via copy() to prevent concurrent modification
- Dual interface (update vs set) for incremental vs complete updates
- Type-safe dictionary operations
"""

from typing import Dict, Any


class ProgressTracker:
    """
    Manages progress data for supervised agents

    Provides thread-safe progress tracking with both incremental
    and complete update capabilities.
    """

    def __init__(self) -> None:
        """Initialize empty progress tracker"""
        self._progress_data: Dict[str, Any] = {}

    def update(self, progress_data: Dict[str, Any]) -> None:
        """
        Update progress data incrementally

        Args:
            progress_data: New or updated progress fields
                          (e.g., {"step": "analyzing", "percent": 50})

        Example:
            tracker.update({"step": "parsing"})
            tracker.update({"percent": 25})
            # Result: {"step": "parsing", "percent": 25}
        """
        self._progress_data.update(progress_data)

    def set(self, progress_data: Dict[str, Any]) -> None:
        """
        Replace all progress data

        Args:
            progress_data: Complete new progress state

        Example:
            tracker.set({"step": "analyzing", "total": 100})
            # Previous data is completely replaced
        """
        self._progress_data = progress_data.copy()

    def get_snapshot(self) -> Dict[str, Any]:
        """
        Get immutable copy of current progress data

        Returns:
            Copy of progress data to prevent external modification

        Example:
            snapshot = tracker.get_snapshot()
            # Safe to pass to heartbeat thread
        """
        return self._progress_data.copy()

    def clear(self) -> None:
        """Clear all progress data"""
        self._progress_data.clear()

    def __repr__(self) -> str:
        return f"ProgressTracker({self._progress_data!r})"
