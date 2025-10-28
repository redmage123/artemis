#!/usr/bin/env python3
"""
WHY: Track pipeline execution status in real-time using Redis for state and Pub/Sub for events
RESPONSIBILITY: Manage pipeline state, publish events, query status
PATTERNS: Repository (Redis storage), Observer (Pub/Sub), Facade (simplified API)

RedisPipelineTracker provides:
- Persistent pipeline state storage (24-hour TTL)
- Real-time status updates via Pub/Sub
- Per-stage progress tracking
- WebSocket-compatible event broadcasting
- Fallback to no-op when Redis unavailable
"""

import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from redis_client import RedisClient, get_redis_client
from redis.models import StageStatus, PipelineStatus


class RedisPipelineTracker:
    """
    Real-time pipeline status tracker using Redis

    Features:
    - Persistent pipeline state storage
    - Real-time status updates via Pub/Sub
    - Progress tracking per stage
    - WebSocket-compatible event broadcasting
    """

    def __init__(
        self,
        redis_client: Optional[RedisClient] = None,
        key_prefix: str = "artemis:pipeline"
    ):
        """
        Initialize pipeline tracker

        Args:
            redis_client: Redis client (uses default if not provided)
            key_prefix: Redis key prefix for namespacing
        """
        # Guard clause - use provided client or get default
        if redis_client:
            self.redis = redis_client
        else:
            self.redis = get_redis_client(raise_on_error=False)

        self.key_prefix = key_prefix
        self.enabled = self.redis is not None

        # Guard clause - warn if Redis unavailable
        if not self.enabled:
            print("⚠️  Redis not available - Real-time tracking disabled")

    def _get_pipeline_key(self, card_id: str) -> str:
        """Get Redis key for pipeline state"""
        return f"{self.key_prefix}:{card_id}"

    def _get_stage_key(self, card_id: str, stage_name: str) -> str:
        """Get Redis key for stage state"""
        return f"{self.key_prefix}:{card_id}:stage:{stage_name}"

    def _get_channel_name(self, card_id: str) -> str:
        """Get Pub/Sub channel name for pipeline"""
        return f"{self.key_prefix}:events:{card_id}"

    def start_pipeline(
        self,
        card_id: str,
        total_stages: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Start tracking a new pipeline execution

        Args:
            card_id: Card ID
            total_stages: Total number of stages
            metadata: Additional metadata (task title, priority, etc.)

        Returns:
            True if started successfully
        """
        # Guard clause - check if enabled
        if not self.enabled:
            return False

        try:
            pipeline_data = {
                "card_id": card_id,
                "status": PipelineStatus.RUNNING.value,
                "total_stages": total_stages,
                "completed_stages": 0,
                "current_stage": None,
                "start_time": datetime.utcnow().isoformat(),
                "end_time": None,
                "metadata": metadata or {}
            }

            # Store pipeline state
            pipeline_key = self._get_pipeline_key(card_id)
            self.redis.set(
                pipeline_key,
                json.dumps(pipeline_data),
                ex=86400  # 24 hour TTL
            )

            # Publish start event
            self._publish_event(card_id, {
                "event": "pipeline_started",
                "card_id": card_id,
                "total_stages": total_stages,
                "timestamp": datetime.utcnow().isoformat()
            })

            return True

        except Exception as e:
            print(f"⚠️  Failed to start pipeline tracking: {e}")
            return False

    def update_stage_status(
        self,
        card_id: str,
        stage_name: str,
        status: StageStatus,
        progress_percent: Optional[int] = None,
        message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update stage status

        Args:
            card_id: Card ID
            stage_name: Stage name
            status: Stage status
            progress_percent: Progress percentage (0-100)
            message: Status message
            metadata: Additional metadata

        Returns:
            True if updated successfully
        """
        # Guard clause - check if enabled
        if not self.enabled:
            return False

        try:
            stage_data = {
                "stage_name": stage_name,
                "status": status.value,
                "progress_percent": progress_percent,
                "message": message,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": metadata or {}
            }

            # Store stage state
            stage_key = self._get_stage_key(card_id, stage_name)
            self.redis.set(
                stage_key,
                json.dumps(stage_data),
                ex=86400  # 24 hour TTL
            )

            # Update pipeline current stage
            pipeline_key = self._get_pipeline_key(card_id)
            pipeline_json = self.redis.get(pipeline_key)

            if pipeline_json:
                pipeline_data = json.loads(pipeline_json)
                pipeline_data["current_stage"] = stage_name

                # Increment completed stages if stage completed
                if status == StageStatus.COMPLETED:
                    pipeline_data["completed_stages"] += 1

                self.redis.set(pipeline_key, json.dumps(pipeline_data), ex=86400)

            # Publish stage update event
            self._publish_event(card_id, {
                "event": "stage_updated",
                "card_id": card_id,
                "stage_name": stage_name,
                "status": status.value,
                "progress_percent": progress_percent,
                "message": message,
                "timestamp": datetime.utcnow().isoformat()
            })

            return True

        except Exception as e:
            print(f"⚠️  Failed to update stage status: {e}")
            return False

    def complete_pipeline(
        self,
        card_id: str,
        status: PipelineStatus = PipelineStatus.COMPLETED,
        final_message: Optional[str] = None
    ) -> bool:
        """
        Mark pipeline as complete

        Args:
            card_id: Card ID
            status: Final status (COMPLETED or FAILED)
            final_message: Final status message

        Returns:
            True if completed successfully
        """
        # Guard clause - check if enabled
        if not self.enabled:
            return False

        try:
            pipeline_key = self._get_pipeline_key(card_id)
            pipeline_json = self.redis.get(pipeline_key)

            if pipeline_json:
                pipeline_data = json.loads(pipeline_json)
                pipeline_data["status"] = status.value
                pipeline_data["end_time"] = datetime.utcnow().isoformat()
                pipeline_data["current_stage"] = None

                # Calculate duration
                start_time = datetime.fromisoformat(pipeline_data["start_time"])
                end_time = datetime.utcnow()
                duration_seconds = (end_time - start_time).total_seconds()
                pipeline_data["duration_seconds"] = duration_seconds

                self.redis.set(pipeline_key, json.dumps(pipeline_data), ex=86400)

                # Publish completion event
                self._publish_event(card_id, {
                    "event": "pipeline_completed",
                    "card_id": card_id,
                    "status": status.value,
                    "duration_seconds": duration_seconds,
                    "message": final_message,
                    "timestamp": datetime.utcnow().isoformat()
                })

                return True

            return False

        except Exception as e:
            print(f"⚠️  Failed to complete pipeline tracking: {e}")
            return False

    def get_pipeline_status(self, card_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current pipeline status

        Args:
            card_id: Card ID

        Returns:
            Pipeline status dict or None
        """
        # Guard clause - check if enabled
        if not self.enabled:
            return None

        try:
            pipeline_key = self._get_pipeline_key(card_id)
            pipeline_json = self.redis.get(pipeline_key)

            # Guard clause - check if pipeline exists
            if not pipeline_json:
                return None

            return json.loads(pipeline_json)

        except Exception as e:
            print(f"⚠️  Failed to get pipeline status: {e}")
            return None

    def get_stage_status(self, card_id: str, stage_name: str) -> Optional[Dict[str, Any]]:
        """
        Get stage status

        Args:
            card_id: Card ID
            stage_name: Stage name

        Returns:
            Stage status dict or None
        """
        # Guard clause - check if enabled
        if not self.enabled:
            return None

        try:
            stage_key = self._get_stage_key(card_id, stage_name)
            stage_json = self.redis.get(stage_key)

            # Guard clause - check if stage exists
            if not stage_json:
                return None

            return json.loads(stage_json)

        except Exception as e:
            print(f"⚠️  Failed to get stage status: {e}")
            return None

    def get_all_stage_statuses(self, card_id: str) -> List[Dict[str, Any]]:
        """
        Get all stage statuses for a pipeline

        Args:
            card_id: Card ID

        Returns:
            List of stage status dicts
        """
        # Guard clause - check if enabled
        if not self.enabled:
            return []

        try:
            pattern = f"{self.key_prefix}:{card_id}:stage:*"
            stage_keys = list(self.redis.client.scan_iter(match=pattern))

            statuses = []
            for key in stage_keys:
                stage_json = self.redis.get(key)

                # Guard clause - skip if no data
                if not stage_json:
                    continue

                statuses.append(json.loads(stage_json))

            return statuses

        except Exception as e:
            print(f"⚠️  Failed to get all stage statuses: {e}")
            return []

    def _publish_event(self, card_id: str, event_data: Dict[str, Any]) -> None:
        """
        Publish event to Pub/Sub channel

        Args:
            card_id: Card ID
            event_data: Event data to publish
        """
        # Guard clause - check if enabled
        if not self.enabled:
            return

        try:
            channel = self._get_channel_name(card_id)
            message = json.dumps(event_data)
            self.redis.publish(channel, message)

        except Exception as e:
            print(f"⚠️  Failed to publish event: {e}")

    def subscribe_to_pipeline(self, card_id: str):
        """
        Subscribe to pipeline events (for WebSocket clients)

        Args:
            card_id: Card ID

        Returns:
            PubSub object for receiving events or None
        """
        # Guard clause - check if enabled
        if not self.enabled:
            return None

        try:
            channel = self._get_channel_name(card_id)
            pubsub = self.redis.client.pubsub()
            pubsub.subscribe(channel)
            return pubsub

        except Exception as e:
            print(f"⚠️  Failed to subscribe to pipeline: {e}")
            return None
