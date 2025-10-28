#!/usr/bin/env python3
"""
WHY: Provide real-time pipeline status tracking using Redis for persistent state and Pub/Sub
RESPONSIBILITY: Export pipeline tracker models and tracker class for status broadcasting
PATTERNS: Observer (Pub/Sub events), Repository (Redis state storage)

This package provides real-time pipeline tracking with:
- Persistent pipeline state storage in Redis
- Real-time status updates via Pub/Sub
- Progress tracking per stage
- WebSocket-compatible event broadcasting

Example:
    from redis import RedisPipelineTracker, StageStatus, PipelineStatus

    tracker = RedisPipelineTracker()

    # Start tracking pipeline
    tracker.start_pipeline(
        card_id="card-001",
        total_stages=5,
        metadata={"title": "Build Feature X"}
    )

    # Update stage status
    tracker.update_stage_status(
        card_id="card-001",
        stage_name="development",
        status=StageStatus.RUNNING,
        progress_percent=50
    )

    # Complete pipeline
    tracker.complete_pipeline(
        card_id="card-001",
        status=PipelineStatus.COMPLETED
    )
"""

from redis.models import StageStatus, PipelineStatus
from redis.tracker import RedisPipelineTracker

__all__ = [
    'StageStatus',
    'PipelineStatus',
    'RedisPipelineTracker'
]
