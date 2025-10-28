#!/usr/bin/env python3
"""
WHY: Track complete state and timing information for individual pipeline stages
RESPONSIBILITY: Maintain stage execution details including timing, retries, and errors
PATTERNS: Value object, state tracking, metrics collection
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional

from state_machine.stage_state import StageState


@dataclass
class StageStateInfo:
    """State information for a single stage"""
    stage_name: str
    state: StageState
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    retry_count: int = 0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
