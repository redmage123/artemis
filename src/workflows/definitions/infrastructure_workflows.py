#!/usr/bin/env python3
"""
Infrastructure Workflow Definitions

WHAT:
Recovery workflows for infrastructure-related failures including timeouts,
hanging processes, memory exhaustion, disk space, and network errors.

WHY:
Infrastructure issues are the most common runtime failures. These workflows
provide automated recovery paths to restore pipeline operation without manual
intervention.

RESPONSIBILITY:
- Define recovery workflows for infrastructure failures
- Configure retry strategies and timeouts
- Set success/failure state transitions

PATTERNS:
- Builder Pattern: Each build_* method constructs a complete workflow
- Strategy Pattern: Different recovery strategies for different issues
- Chain of Responsibility: Actions execute in sequence until recovery

INTEGRATION:
- Used by: WorkflowBuilder, WorkflowRegistry
- Uses: workflow_handlers for action execution
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
# INFRASTRUCTURE WORKFLOW BUILDERS
# ============================================================================

def build_timeout_workflow() -> Workflow:
    """
    Build workflow for timeout recovery

    WHAT:
    Creates workflow to handle operation timeouts by increasing limits
    and killing hanging processes.

    WHY:
    Timeouts often occur when operations take longer than expected but are
    still making progress. Increasing timeout and cleaning up stuck processes
    often resolves the issue.

    STRATEGY:
    1. Increase timeout threshold (no retry - immediate action)
    2. Kill hanging process (retry up to 2 times)

    RETURNS:
        Workflow: Configured timeout recovery workflow
    """
    return Workflow(
        name="Timeout Recovery",
        issue_type=IssueType.TIMEOUT,
        actions=[
            WorkflowAction(
                action_name="Increase timeout",
                handler=WorkflowHandlers.increase_timeout,
                retry_on_failure=False
            ),
            WorkflowAction(
                action_name="Kill hanging process",
                handler=WorkflowHandlers.kill_hanging_process,
                retry_on_failure=True,
                max_retries=2
            )
        ],
        success_state=PipelineState.RUNNING,
        failure_state=PipelineState.FAILED,
        rollback_on_failure=False
    )


def build_hanging_process_workflow() -> Workflow:
    """
    Build workflow for hanging process recovery

    WHAT:
    Creates workflow to kill stuck processes and cleanup temporary files.

    WHY:
    Hanging processes prevent pipeline progress and consume resources.
    Killing them and cleaning up allows pipeline to continue.

    STRATEGY:
    1. Kill hanging process (retry up to 3 times)
    2. Cleanup temp files (ensure clean state)

    RETURNS:
        Workflow: Configured hanging process recovery workflow
    """
    return Workflow(
        name="Hanging Process Recovery",
        issue_type=IssueType.HANGING_PROCESS,
        actions=[
            WorkflowAction(
                action_name="Kill hanging process",
                handler=WorkflowHandlers.kill_hanging_process,
                retry_on_failure=True,
                max_retries=3
            ),
            WorkflowAction(
                action_name="Cleanup temp files",
                handler=WorkflowHandlers.cleanup_temp_files
            )
        ],
        success_state=PipelineState.RUNNING,
        failure_state=PipelineState.FAILED
    )


def build_memory_exhausted_workflow() -> Workflow:
    """
    Build workflow for memory exhaustion recovery

    WHAT:
    Creates workflow to free memory and cleanup temporary files.

    WHY:
    Memory exhaustion causes crashes and failed operations. Freeing memory
    and removing temp files often provides enough headroom to continue.

    STRATEGY:
    1. Free memory (force garbage collection, clear caches)
    2. Cleanup temp files (remove unnecessary data)

    RETURNS:
        Workflow: Configured memory recovery workflow
    """
    return Workflow(
        name="Memory Recovery",
        issue_type=IssueType.MEMORY_EXHAUSTED,
        actions=[
            WorkflowAction(
                action_name="Free memory",
                handler=WorkflowHandlers.free_memory
            ),
            WorkflowAction(
                action_name="Cleanup temp files",
                handler=WorkflowHandlers.cleanup_temp_files
            )
        ],
        success_state=PipelineState.RUNNING,
        failure_state=PipelineState.FAILED
    )


def build_disk_full_workflow() -> Workflow:
    """
    Build workflow for disk full recovery

    WHAT:
    Creates workflow to free disk space by cleaning temp files and verifying space.

    WHY:
    Full disk prevents writes and causes failures. Cleanup temp files first,
    then verify sufficient space is available.

    STRATEGY:
    1. Cleanup temp files (free disk space)
    2. Check disk space (verify recovery)

    RETURNS:
        Workflow: Configured disk space recovery workflow
    """
    return Workflow(
        name="Disk Space Recovery",
        issue_type=IssueType.DISK_FULL,
        actions=[
            WorkflowAction(
                action_name="Cleanup temp files",
                handler=WorkflowHandlers.cleanup_temp_files
            ),
            WorkflowAction(
                action_name="Check disk space",
                handler=WorkflowHandlers.check_disk_space
            )
        ],
        success_state=PipelineState.RUNNING,
        failure_state=PipelineState.FAILED
    )


def build_network_error_workflow() -> Workflow:
    """
    Build workflow for network error recovery

    WHAT:
    Creates workflow to retry failed network operations with exponential backoff.

    WHY:
    Network errors are often transient. Retrying with backoff usually succeeds
    once network conditions improve.

    STRATEGY:
    1. Retry network request (up to 3 times with backoff)

    RETURNS:
        Workflow: Configured network error recovery workflow
    """
    return Workflow(
        name="Network Error Recovery",
        issue_type=IssueType.NETWORK_ERROR,
        actions=[
            WorkflowAction(
                action_name="Retry network request",
                handler=WorkflowHandlers.retry_network_request,
                retry_on_failure=True,
                max_retries=3
            )
        ],
        success_state=PipelineState.RUNNING,
        failure_state=PipelineState.DEGRADED
    )


# ============================================================================
# WORKFLOW CATALOG
# ============================================================================

def get_infrastructure_workflows() -> Dict[IssueType, Workflow]:
    """
    Get all infrastructure recovery workflows

    WHAT:
    Returns complete mapping of infrastructure issue types to workflows.

    WHY:
    Provides single point of access for all infrastructure workflows.
    Used by WorkflowRegistry to build complete workflow catalog.

    RETURNS:
        Dict[IssueType, Workflow]: Infrastructure workflows by issue type
    """
    return {
        IssueType.TIMEOUT: build_timeout_workflow(),
        IssueType.HANGING_PROCESS: build_hanging_process_workflow(),
        IssueType.MEMORY_EXHAUSTED: build_memory_exhausted_workflow(),
        IssueType.DISK_FULL: build_disk_full_workflow(),
        IssueType.NETWORK_ERROR: build_network_error_workflow(),
    }
