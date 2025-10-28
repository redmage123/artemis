#!/usr/bin/env python3
"""
WHY: Record state transitions for audit trail and debugging
RESPONSIBILITY: Immutable record of each state change with metadata
PATTERNS: Value object, audit trail, event sourcing
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional

from state_machine.pipeline_state import PipelineState
from state_machine.event_type import EventType


@dataclass
class StateTransition:
    """Record of a state transition"""
    from_state: PipelineState
    to_state: PipelineState
    event: EventType
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    reason: Optional[str] = None
