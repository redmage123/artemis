#!/usr/bin/env python3
"""
WHY: Define complete recovery workflow for specific issue types
RESPONSIBILITY: Compose multiple actions into cohesive recovery workflow
PATTERNS: Composite pattern, workflow orchestration, state transition routing
"""

from dataclasses import dataclass
from typing import List

from state_machine.issue_type import IssueType
from state_machine.pipeline_state import PipelineState
from state_machine.workflow_action import WorkflowAction


@dataclass
class Workflow:
    """Recovery workflow for an issue"""
    name: str
    issue_type: IssueType
    actions: List[WorkflowAction]
    success_state: PipelineState
    failure_state: PipelineState
    rollback_on_failure: bool = False
    escalate_on_failure: bool = True
