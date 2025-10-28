#!/usr/bin/env python3
"""
WHY: Build recovery workflows for multi-agent coordination failures
RESPONSIBILITY: Construct recovery workflows for arbitration, developer conflicts, messenger errors
PATTERNS: Builder pattern, factory methods, workflow composition

Multi-agent workflows handle:
- Arbitration deadlocks
- Developer conflicts
- Messenger errors

Each workflow defines actions to resolve multi-agent coordination issues.
"""

from typing import Dict
from workflows_core.models import Workflow, WorkflowAction, IssueType, PipelineState
from workflow_handlers import WorkflowHandlers


class MultiAgentWorkflowBuilder:
    """
    Build recovery workflows for multi-agent issues

    WHAT:
    Factory class that constructs recovery workflows for multi-agent failures:
    arbitration deadlock, developer conflicts, messenger errors.

    WHY:
    Multi-agent systems can deadlock or conflict. This builder provides
    standardized recovery procedures for coordination issues.

    PATTERNS:
    - Static Factory Methods: Each build_*_workflow() creates specific workflow
    - Builder Pattern: Constructs complex workflow objects step-by-step
    """

    @staticmethod
    def build_arbitration_deadlock_workflow() -> Workflow:
        """
        Build workflow for arbitration deadlock resolution

        ACTIONS:
        1. Break arbitration deadlock

        Returns workflow that breaks deadlocks in arbitration.
        """
        return Workflow(
            name="Arbitration Deadlock Resolution",
            issue_type=IssueType.ARBITRATION_DEADLOCK,
            actions=[
                WorkflowAction(
                    action_name="Break arbitration deadlock",
                    handler=WorkflowHandlers.break_arbitration_deadlock
                )
            ],
            success_state=PipelineState.RUNNING,
            failure_state=PipelineState.FAILED
        )

    @staticmethod
    def build_developer_conflict_workflow() -> Workflow:
        """
        Build workflow for developer conflict resolution

        ACTIONS:
        1. Merge developer solutions

        Returns workflow that merges conflicting developer solutions.
        """
        return Workflow(
            name="Developer Conflict Merge",
            issue_type=IssueType.DEVELOPER_CONFLICT,
            actions=[
                WorkflowAction(
                    action_name="Merge developer solutions",
                    handler=WorkflowHandlers.merge_developer_solutions
                )
            ],
            success_state=PipelineState.RUNNING,
            failure_state=PipelineState.DEGRADED
        )

    @staticmethod
    def build_messenger_error_workflow() -> Workflow:
        """
        Build workflow for messenger error recovery

        ACTIONS:
        1. Restart messenger

        Returns workflow that restarts the messenger service.
        """
        return Workflow(
            name="Messenger Restart",
            issue_type=IssueType.MESSENGER_ERROR,
            actions=[
                WorkflowAction(
                    action_name="Restart messenger",
                    handler=WorkflowHandlers.restart_messenger
                )
            ],
            success_state=PipelineState.RUNNING,
            failure_state=PipelineState.DEGRADED
        )

    @staticmethod
    def build_all() -> Dict[IssueType, Workflow]:
        """
        Build all multi-agent workflows

        Returns:
            Dict mapping IssueType to Workflow for all multi-agent issues
        """
        return {
            IssueType.ARBITRATION_DEADLOCK: MultiAgentWorkflowBuilder.build_arbitration_deadlock_workflow(),
            IssueType.DEVELOPER_CONFLICT: MultiAgentWorkflowBuilder.build_developer_conflict_workflow(),
            IssueType.MESSENGER_ERROR: MultiAgentWorkflowBuilder.build_messenger_error_workflow(),
        }
