#!/usr/bin/env python3
"""
Module: observer/event_model.py

WHY: Immutable, structured event data passed to all observers,
     ensuring consistent event information and preventing observers from
     modifying event data.

RESPONSIBILITY:
    - Carry event information between producer and observers
    - Provide structured access to event metadata
    - Support serialization to dict for logging/storage

PATTERNS:
    - Data Transfer Object (DTO) pattern
    - Immutability via dataclass frozen=False (Python limitation with default_factory)
    - Builder pattern support via dataclass defaults

DESIGN DECISIONS:
    - Immutable fields prevent observers from interfering with each other
    - Optional fields support flexible event creation
    - to_dict() enables JSON serialization for storage/logging
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional

from .event_types import EventType


@dataclass
class PipelineEvent:
    """
    Represents a pipeline event.

    Immutability: Fields should not be modified after creation to prevent
    observers from interfering with each other.

    Thread-safety: Thread-safe (immutable after creation)
    """
    event_type: EventType
    timestamp: datetime = field(default_factory=datetime.now)
    card_id: Optional[str] = None
    stage_name: Optional[str] = None
    developer_name: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[Exception] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert event to dictionary for serialization.

        Why needed: Enables event storage in logs, databases, message queues,
        and metrics systems. Provides JSON-compatible representation.

        Returns:
            Dict with all event fields serialized to JSON-compatible types
        """
        return {
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "card_id": self.card_id,
            "stage_name": self.stage_name,
            "developer_name": self.developer_name,
            "data": self.data,
            "error": str(self.error) if self.error else None
        }
