#!/usr/bin/env python3
"""
Module: observer/metrics_observer.py

WHY: Collects pipeline metrics for performance analysis, retrospectives,
     and continuous improvement. Tracks durations, success/failure rates,
     retry counts, and developer performance.

RESPONSIBILITY:
    - Collect metrics from all pipeline events
    - Track stage durations by measuring start/end times
    - Count success/failure rates
    - Track retry counts per stage
    - Monitor developer statistics

PATTERNS:
    - Observer pattern implementation
    - Strategy pattern for event-specific metric handling
    - Aggregator pattern for metrics collection

DESIGN DECISIONS:
    - Store all events for detailed analysis
    - Track stage start times for duration calculation
    - Use guard clauses to handle missing data gracefully
    - Provide both full metrics and summary (without full event list)
"""

from typing import Dict, Any, List
from datetime import datetime

from .observer_interface import PipelineObserver
from .event_model import PipelineEvent
from .event_types import EventType


class MetricsObserver(PipelineObserver):
    """
    Observer that collects pipeline metrics.

    Tracks:
    - Stage durations
    - Success/failure rates
    - Retry counts
    - Developer performance
    """

    def __init__(self):
        self.metrics: Dict[str, Any] = {
            "pipeline_starts": 0,
            "pipeline_completions": 0,
            "pipeline_failures": 0,
            "stage_durations": {},
            "stage_failures": {},
            "stage_retries": {},
            "developer_stats": {},
            "events": []
        }
        self.stage_start_times: Dict[str, datetime] = {}

    def on_event(self, event: PipelineEvent) -> None:
        """Collect metrics from event"""
        # Track event
        self.metrics["events"].append(event.to_dict())

        # Dispatch to specific handlers
        self._handle_pipeline_metrics(event)
        self._handle_stage_metrics(event)
        self._handle_developer_metrics(event)

    def _handle_pipeline_metrics(self, event: PipelineEvent) -> None:
        """Handle pipeline-level metrics"""
        if event.event_type == EventType.PIPELINE_STARTED:
            self.metrics["pipeline_starts"] += 1
            return

        if event.event_type == EventType.PIPELINE_COMPLETED:
            self.metrics["pipeline_completions"] += 1
            return

        if event.event_type == EventType.PIPELINE_FAILED:
            self.metrics["pipeline_failures"] += 1

    def _handle_stage_metrics(self, event: PipelineEvent) -> None:
        """Handle stage-level metrics"""
        if event.event_type == EventType.STAGE_STARTED:
            self._record_stage_start(event)
            return

        if event.event_type == EventType.STAGE_COMPLETED:
            self._record_stage_completion(event)
            return

        if event.event_type == EventType.STAGE_FAILED:
            self._record_stage_failure(event)
            return

        if event.event_type == EventType.STAGE_RETRYING:
            self._record_stage_retry(event)

    def _record_stage_start(self, event: PipelineEvent) -> None:
        """Record stage start time"""
        if not event.stage_name:
            return

        self.stage_start_times[event.stage_name] = event.timestamp

    def _record_stage_completion(self, event: PipelineEvent) -> None:
        """Record stage completion and calculate duration"""
        if not event.stage_name:
            return

        if event.stage_name not in self.stage_start_times:
            return

        start = self.stage_start_times[event.stage_name]
        duration = (event.timestamp - start).total_seconds()

        if event.stage_name not in self.metrics["stage_durations"]:
            self.metrics["stage_durations"][event.stage_name] = []

        self.metrics["stage_durations"][event.stage_name].append(duration)

    def _record_stage_failure(self, event: PipelineEvent) -> None:
        """Record stage failure"""
        if not event.stage_name:
            return

        self.metrics["stage_failures"][event.stage_name] = \
            self.metrics["stage_failures"].get(event.stage_name, 0) + 1

    def _record_stage_retry(self, event: PipelineEvent) -> None:
        """Record stage retry"""
        if not event.stage_name:
            return

        self.metrics["stage_retries"][event.stage_name] = \
            self.metrics["stage_retries"].get(event.stage_name, 0) + 1

    def _handle_developer_metrics(self, event: PipelineEvent) -> None:
        """Handle developer-level metrics"""
        developer_events = [
            EventType.DEVELOPER_STARTED,
            EventType.DEVELOPER_COMPLETED,
            EventType.DEVELOPER_FAILED
        ]

        if event.event_type not in developer_events:
            return

        if not event.developer_name:
            return

        self._ensure_developer_stats_exist(event.developer_name)
        self._update_developer_stats(event)

    def _ensure_developer_stats_exist(self, developer_name: str) -> None:
        """Ensure developer stats dictionary exists"""
        if developer_name in self.metrics["developer_stats"]:
            return

        self.metrics["developer_stats"][developer_name] = {
            "started": 0,
            "completed": 0,
            "failed": 0
        }

    def _update_developer_stats(self, event: PipelineEvent) -> None:
        """Update developer statistics based on event type"""
        stats = self.metrics["developer_stats"][event.developer_name]

        if event.event_type == EventType.DEVELOPER_STARTED:
            stats["started"] += 1
            return

        if event.event_type == EventType.DEVELOPER_COMPLETED:
            stats["completed"] += 1
            return

        if event.event_type == EventType.DEVELOPER_FAILED:
            stats["failed"] += 1

    def get_metrics(self) -> Dict[str, Any]:
        """Get collected metrics"""
        return self.metrics

    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary without full event list"""
        summary = self.metrics.copy()
        summary["event_count"] = len(summary["events"])
        del summary["events"]  # Don't include full event list in summary
        return summary
