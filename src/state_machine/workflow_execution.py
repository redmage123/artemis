#!/usr/bin/env python3
"""
WHY: Record execution history of recovery workflows for analysis and learning
RESPONSIBILITY: Track workflow execution with actions, timing, and outcomes
PATTERNS: Command pattern, audit trail, execution history
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional

from state_machine.issue_type import IssueType


@dataclass
class WorkflowExecution:
    """Record of a workflow execution"""
    workflow_name: str
    issue_type: IssueType
    start_time: datetime
    end_time: Optional[datetime] = None
    success: bool = False
    actions_taken: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
