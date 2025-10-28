#!/usr/bin/env python3
"""
System Management Workflow Definitions

WHAT:
Recovery workflows for system-level failures including zombie processes,
file locks, and permission errors.

WHY:
System-level issues prevent pipeline operation through resource conflicts,
access restrictions, and orphaned processes. These workflows restore system health.

RESPONSIBILITY:
- Define recovery workflows for system failures
- Configure process cleanup strategies
- Handle file system and permission issues

PATTERNS:
- Builder Pattern: Each build_* method constructs a complete workflow
- Resource Cleanup: Systematic cleanup of system resources
- Permission Repair: Automated permission fixes

INTEGRATION:
- Used by: WorkflowBuilder, WorkflowRegistry
- Uses: workflow_handlers for system operations
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
# SYSTEM WORKFLOW BUILDERS
# ============================================================================

def build_zombie_process_workflow() -> Workflow:
    """
    Build workflow for zombie process cleanup

    WHAT:
    Creates workflow to cleanup zombie (defunct) processes.

    WHY:
    Zombie processes occur when child processes exit but parent doesn't
    reap them. They consume process table entries and can eventually
    prevent new process creation.

    STRATEGY:
    1. Cleanup zombie processes
       - Identify zombie processes (state 'Z')
       - Kill parent processes if necessary
       - Reap zombie processes
       - Verify cleanup success

    NOTE:
    Zombie cleanup doesn't stop pipeline (DEGRADED).

    RETURNS:
        Workflow: Configured zombie process cleanup workflow
    """
    return Workflow(
        name="Zombie Process Cleanup",
        issue_type=IssueType.ZOMBIE_PROCESS,
        actions=[
            WorkflowAction(
                action_name="Cleanup zombie processes",
                handler=WorkflowHandlers.cleanup_zombie_processes
            )
        ],
        success_state=PipelineState.RUNNING,
        failure_state=PipelineState.DEGRADED
    )


def build_file_lock_workflow() -> Workflow:
    """
    Build workflow for file lock release

    WHAT:
    Creates workflow to release stuck file locks.

    WHY:
    File locks can get stuck when processes crash without cleanup.
    Stuck locks prevent other processes from accessing files, blocking
    pipeline progress.

    STRATEGY:
    1. Release file locks
       - Identify locked files
       - Find processes holding locks
       - Release locks (kill process if necessary)
       - Verify files are accessible

    RETURNS:
        Workflow: Configured file lock release workflow
    """
    return Workflow(
        name="File Lock Release",
        issue_type=IssueType.FILE_LOCK,
        actions=[
            WorkflowAction(
                action_name="Release file locks",
                handler=WorkflowHandlers.release_file_locks
            )
        ],
        success_state=PipelineState.RUNNING,
        failure_state=PipelineState.FAILED
    )


def build_permission_denied_workflow() -> Workflow:
    """
    Build workflow for permission error fixes

    WHAT:
    Creates workflow to fix permission errors on files and directories.

    WHY:
    Permission errors occur when pipeline processes lack read/write/execute
    access to required resources. Fixing permissions allows operations to proceed.

    STRATEGY:
    1. Fix permissions
       - Identify files/directories with permission issues
       - Apply appropriate permissions (chmod)
       - Set ownership if needed (chown)
       - Verify access is restored

    RETURNS:
        Workflow: Configured permission fix workflow
    """
    return Workflow(
        name="Permission Fix",
        issue_type=IssueType.PERMISSION_DENIED,
        actions=[
            WorkflowAction(
                action_name="Fix permissions",
                handler=WorkflowHandlers.fix_permissions
            )
        ],
        success_state=PipelineState.RUNNING,
        failure_state=PipelineState.FAILED
    )


# ============================================================================
# WORKFLOW CATALOG
# ============================================================================

def get_system_workflows() -> Dict[IssueType, Workflow]:
    """
    Get all system management workflows

    WHAT:
    Returns complete mapping of system issue types to workflows.

    WHY:
    Provides single point of access for all system workflows.
    Used by WorkflowRegistry to build complete workflow catalog.

    RETURNS:
        Dict[IssueType, Workflow]: System workflows by issue type
    """
    return {
        IssueType.ZOMBIE_PROCESS: build_zombie_process_workflow(),
        IssueType.FILE_LOCK: build_file_lock_workflow(),
        IssueType.PERMISSION_DENIED: build_permission_denied_workflow(),
    }
