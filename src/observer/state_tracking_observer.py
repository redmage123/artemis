#!/usr/bin/env python3
"""
Module: observer/state_tracking_observer.py

WHY: Maintains real-time snapshot of pipeline state for
     monitoring dashboards, health checks, and status queries.

RESPONSIBILITY:
    - Track current card ID and stage
    - Monitor active developers (set for O(1) operations)
    - Update pipeline status (idle/running/completed/failed/paused)
    - Maintain recent error history (bounded queue)

PATTERNS:
    - Observer pattern implementation
    - State pattern for pipeline status tracking
    - Bounded queue for error history (FIFO)

DESIGN DECISIONS:
    - Uses set for active_developers instead of list for O(1) add/remove
    - Bounded error list prevents unbounded memory growth
    - discard() for set removal (doesn't raise if missing)
    - Guard clauses prevent unnecessary state updates
"""

from typing import Dict, Any, List, Optional, Set

from .observer_interface import PipelineObserver
from .event_model import PipelineEvent
from .event_types import EventType


class StateTrackingObserver(PipelineObserver):
    """
    Observer that tracks current pipeline state.

    Performance optimization: Uses set for active_developers instead of list
    for O(1) add/remove operations instead of O(n).

    Thread-safety: Not thread-safe (assumes single-threaded pipeline)
    """

    def __init__(self):
        self.current_card_id: Optional[str] = None
        self.current_stage: Optional[str] = None
        # Performance: Use set for O(1) add/remove instead of O(n) list operations
        self.active_developers: Set[str] = set()
        self.pipeline_status: str = "idle"
        self.recent_errors: List[str] = []
        self.max_errors = 10

    def on_event(self, event: PipelineEvent) -> None:
        """Update state based on event"""
        # Update card ID
        if event.card_id:
            self.current_card_id = event.card_id

        # Dispatch to specific handlers
        self._handle_pipeline_state(event)
        self._handle_stage_state(event)
        self._handle_developer_state(event)
        self._handle_error_tracking(event)

    def _handle_pipeline_state(self, event: PipelineEvent) -> None:
        """Handle pipeline state changes"""
        if event.event_type == EventType.PIPELINE_STARTED:
            self.pipeline_status = "running"
            self.recent_errors = []
            return

        if event.event_type == EventType.PIPELINE_COMPLETED:
            self.pipeline_status = "completed"
            self.current_stage = None
            return

        if event.event_type == EventType.PIPELINE_FAILED:
            self.pipeline_status = "failed"
            return

        if event.event_type == EventType.PIPELINE_PAUSED:
            self.pipeline_status = "paused"

    def _handle_stage_state(self, event: PipelineEvent) -> None:
        """Handle stage state changes"""
        if event.event_type == EventType.STAGE_STARTED:
            self.current_stage = event.stage_name
            return

        stage_end_events = [
            EventType.STAGE_COMPLETED,
            EventType.STAGE_FAILED,
            EventType.STAGE_SKIPPED
        ]

        if event.event_type in stage_end_events:
            if event.stage_name == self.current_stage:
                self.current_stage = None

    def _handle_developer_state(self, event: PipelineEvent) -> None:
        """Handle developer state changes (O(1) set operations)"""
        if event.event_type == EventType.DEVELOPER_STARTED:
            if event.developer_name:
                self.active_developers.add(event.developer_name)
            return

        developer_end_events = [
            EventType.DEVELOPER_COMPLETED,
            EventType.DEVELOPER_FAILED
        ]

        if event.event_type in developer_end_events:
            if event.developer_name:
                # discard doesn't raise if not found
                self.active_developers.discard(event.developer_name)

    def _handle_error_tracking(self, event: PipelineEvent) -> None:
        """Track recent errors"""
        if not event.error:
            return

        self.recent_errors.append(str(event.error))

        if len(self.recent_errors) > self.max_errors:
            self.recent_errors.pop(0)

    def get_state(self) -> Dict[str, Any]:
        """Get current pipeline state"""
        return {
            "card_id": self.current_card_id,
            "current_stage": self.current_stage,
            "active_developers": self.active_developers.copy(),
            "pipeline_status": self.pipeline_status,
            "recent_errors": self.recent_errors.copy()
        }
