#!/usr/bin/env python3
"""
WHY: Build recovery workflows for infrastructure failures (timeout, memory, disk, network)
RESPONSIBILITY: Construct recovery workflows for infrastructure-related issues
PATTERNS: Builder pattern, factory methods, workflow composition

Infrastructure workflows handle:
- Timeout issues
- Hanging processes
- Memory exhaustion
- Disk space problems
- Network errors

Each workflow defines a sequence of recovery actions to diagnose and fix the issue.
"""

from typing import Dict
from workflows_core.models import Workflow, WorkflowAction, IssueType, PipelineState
from workflow_handlers import WorkflowHandlers


class InfrastructureWorkflowBuilder:
    """
    Build recovery workflows for infrastructure issues

    WHAT:
    Factory class that constructs recovery workflows for infrastructure failures:
    timeout, hanging process, memory exhaustion, disk full, network errors.

    WHY:
    Infrastructure failures are common in autonomous systems. This builder
    provides standardized recovery procedures for each type of infrastructure issue.

    PATTERNS:
    - Static Factory Methods: Each build_*_workflow() creates specific workflow
    - Builder Pattern: Constructs complex workflow objects step-by-step
    """

    @staticmethod
    def build_timeout_workflow() -> Workflow:
        """
        Build workflow for timeout recovery

        ACTIONS:
        1. Increase timeout threshold
        2. Kill hanging process if needed

        Returns workflow that attempts to resolve timeout by increasing limits
        and terminating stuck processes.
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

    @staticmethod
    def build_hanging_process_workflow() -> Workflow:
        """
        Build workflow for hanging process recovery

        ACTIONS:
        1. Kill hanging process
        2. Cleanup temporary files

        Returns workflow that terminates stuck processes and cleans up resources.
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

    @staticmethod
    def build_memory_exhausted_workflow() -> Workflow:
        """
        Build workflow for memory exhaustion recovery

        ACTIONS:
        1. Free memory
        2. Cleanup temporary files

        Returns workflow that reclaims memory and removes temporary files.
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

    @staticmethod
    def build_disk_full_workflow() -> Workflow:
        """
        Build workflow for disk space recovery

        ACTIONS:
        1. Cleanup temporary files
        2. Check disk space

        Returns workflow that reclaims disk space and verifies availability.
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

    @staticmethod
    def build_network_error_workflow() -> Workflow:
        """
        Build workflow for network error recovery

        ACTIONS:
        1. Retry network request with exponential backoff

        Returns workflow that attempts to recover from transient network issues.
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

    @staticmethod
    def build_all() -> Dict[IssueType, Workflow]:
        """
        Build all infrastructure workflows

        Returns:
            Dict mapping IssueType to Workflow for all infrastructure issues
        """
        return {
            IssueType.TIMEOUT: InfrastructureWorkflowBuilder.build_timeout_workflow(),
            IssueType.HANGING_PROCESS: InfrastructureWorkflowBuilder.build_hanging_process_workflow(),
            IssueType.MEMORY_EXHAUSTED: InfrastructureWorkflowBuilder.build_memory_exhausted_workflow(),
            IssueType.DISK_FULL: InfrastructureWorkflowBuilder.build_disk_full_workflow(),
            IssueType.NETWORK_ERROR: InfrastructureWorkflowBuilder.build_network_error_workflow(),
        }
