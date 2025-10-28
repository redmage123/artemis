#!/usr/bin/env python3
"""
WHY: Capture complete pipeline state at a point in time for debugging and recovery
RESPONSIBILITY: Provide serializable snapshot of entire pipeline state
PATTERNS: Memento pattern, snapshot/restore, state serialization
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional

from state_machine.pipeline_state import PipelineState
from state_machine.stage_state_info import StageStateInfo
from state_machine.issue_type import IssueType


@dataclass
class PipelineSnapshot:
    """Complete snapshot of pipeline state"""
    state: PipelineState
    timestamp: datetime
    card_id: str
    stages: Dict[str, StageStateInfo]
    active_stage: Optional[str] = None
    health_status: str = "healthy"
    circuit_breakers_open: List[str] = field(default_factory=list)
    active_issues: List[IssueType] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
