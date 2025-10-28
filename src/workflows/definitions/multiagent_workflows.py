#!/usr/bin/env python3
"""
Multi-Agent Coordination Workflow Definitions

WHAT:
Recovery workflows for multi-agent failures including arbitration deadlocks,
developer conflicts, and messenger errors.

WHY:
Multi-agent systems can experience coordination failures when agents disagree,
deadlock, or communication channels fail. These workflows restore coordination.

RESPONSIBILITY:
- Define recovery workflows for multi-agent failures
- Configure deadlock breaking strategies
- Handle agent communication failures

PATTERNS:
- Builder Pattern: Each build_* method constructs a complete workflow
- Deadlock Resolution: Timeout-based and priority-based strategies
- Communication Recovery: Restart and reconnect strategies

INTEGRATION:
- Used by: WorkflowBuilder, WorkflowRegistry
- Uses: workflow_handlers for agent coordination
- Returns: Workflow objects with configured actions
"""

from typing import Dict, Any, Optional, List, Callable
from state_machine import (
    IssueType,
    Workflow,
    WorkflowAction,
    PipelineState
)
from workflow_handlers import WorkflowHandlers


# ============================================================================
# MULTI-AGENT WORKFLOW BUILDERS
# ============================================================================

def build_arbitration_deadlock_workflow() -> Workflow:
    """
    Build workflow for arbitration deadlock resolution

    WHAT:
    Creates workflow to break deadlocks in developer arbitration process.

    WHY:
    Deadlocks occur when developers can't reach consensus and arbitrator
    can't decide. Breaking deadlock with timeout or priority rules allows
    pipeline to continue.

    STRATEGY:
    1. Break arbitration deadlock
       - Force timeout on longest-running arbitration
       - Apply priority rules (prefer simpler solutions)
       - Escalate to supervisor for final decision

    RETURNS:
        Workflow: Configured arbitration deadlock resolution workflow
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


def build_developer_conflict_workflow() -> Workflow:
    """
    Build workflow for developer conflict resolution

    WHAT:
    Creates workflow to merge conflicting solutions from multiple developers.

    WHY:
    Multiple developers can produce different solutions for the same task.
    Intelligent merging combines best aspects of each solution.

    STRATEGY:
    1. Merge developer solutions
       - Analyze differences between solutions
       - Identify complementary vs conflicting changes
       - Apply merge strategy (keep best of each)

    NOTE:
    Conflicts don't stop pipeline (DEGRADED) but may reduce quality.

    RETURNS:
        Workflow: Configured developer conflict merge workflow
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


def build_messenger_error_workflow() -> Workflow:
    """
    Build workflow for messenger error recovery

    WHAT:
    Creates workflow to restart messenger when communication fails.

    WHY:
    Messenger handles agent-to-agent communication. Failures prevent
    coordination. Restarting messenger restores communication channels.

    STRATEGY:
    1. Restart messenger
       - Stop existing messenger process
       - Clear message queues
       - Start fresh messenger instance
       - Reconnect all agents

    NOTE:
    Messenger failures don't stop pipeline (DEGRADED) but reduce efficiency.

    RETURNS:
        Workflow: Configured messenger restart workflow
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


# ============================================================================
# WORKFLOW CATALOG
# ============================================================================

def get_multiagent_workflows() -> Dict[IssueType, Workflow]:
    """
    Get all multi-agent coordination workflows

    WHAT:
    Returns complete mapping of multi-agent issue types to workflows.

    WHY:
    Provides single point of access for all multi-agent workflows.
    Used by WorkflowRegistry to build complete workflow catalog.

    RETURNS:
        Dict[IssueType, Workflow]: Multi-agent workflows by issue type
    """
    return {
        IssueType.ARBITRATION_DEADLOCK: build_arbitration_deadlock_workflow(),
        IssueType.DEVELOPER_CONFLICT: build_developer_conflict_workflow(),
        IssueType.MESSENGER_ERROR: build_messenger_error_workflow(),
    }
