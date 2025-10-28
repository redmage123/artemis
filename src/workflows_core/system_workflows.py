#!/usr/bin/env python3
"""
WHY: Build recovery workflows for system-level failures
RESPONSIBILITY: Construct recovery workflows for zombie processes, file locks, permissions
PATTERNS: Builder pattern, factory methods, workflow composition

System workflows handle:
- Zombie processes
- File locks
- Permission errors

Each workflow defines actions to resolve system-level issues.
"""

from typing import Dict
from workflows_core.models import Workflow, WorkflowAction, IssueType, PipelineState
from workflow_handlers import WorkflowHandlers


class SystemWorkflowBuilder:
    """
    Build recovery workflows for system issues

    WHAT:
    Factory class that constructs recovery workflows for system-level failures:
    zombie processes, file locks, permission errors.

    WHY:
    System issues can block execution. This builder provides standardized
    recovery procedures for system-level problems.

    PATTERNS:
    - Static Factory Methods: Each build_*_workflow() creates specific workflow
    - Builder Pattern: Constructs complex workflow objects step-by-step
    """

    @staticmethod
    def build_zombie_process_workflow() -> Workflow:
        """
        Build workflow for zombie process cleanup

        ACTIONS:
        1. Cleanup zombie processes

        Returns workflow that cleans up zombie processes.
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

    @staticmethod
    def build_file_lock_workflow() -> Workflow:
        """
        Build workflow for file lock release

        ACTIONS:
        1. Release file locks

        Returns workflow that releases file locks.
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

    @staticmethod
    def build_permission_denied_workflow() -> Workflow:
        """
        Build workflow for permission error fix

        ACTIONS:
        1. Fix permissions

        Returns workflow that fixes file permissions.
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

    @staticmethod
    def build_all() -> Dict[IssueType, Workflow]:
        """
        Build all system workflows

        Returns:
            Dict mapping IssueType to Workflow for all system issues
        """
        return {
            IssueType.ZOMBIE_PROCESS: SystemWorkflowBuilder.build_zombie_process_workflow(),
            IssueType.FILE_LOCK: SystemWorkflowBuilder.build_file_lock_workflow(),
            IssueType.PERMISSION_DENIED: SystemWorkflowBuilder.build_permission_denied_workflow(),
        }
