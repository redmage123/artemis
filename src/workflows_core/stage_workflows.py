#!/usr/bin/env python3
"""
WHY: Build recovery workflows for stage-specific failures
RESPONSIBILITY: Construct recovery workflows for architecture, code review, integration, validation
PATTERNS: Builder pattern, factory methods, workflow composition

Stage workflows handle:
- Invalid architecture
- Code review failures
- Integration conflicts
- Validation failures

Each workflow defines actions to resolve stage-specific issues.
"""

from typing import Dict
from workflows_core.models import Workflow, WorkflowAction, IssueType, PipelineState
from workflow_handlers import WorkflowHandlers


class StageWorkflowBuilder:
    """
    Build recovery workflows for stage-specific issues

    WHAT:
    Factory class that constructs recovery workflows for stage-related failures:
    architecture invalid, code review failed, integration conflict, validation failed.

    WHY:
    Stage failures require specific recovery procedures. This builder provides
    standardized workflows for each pipeline stage.

    PATTERNS:
    - Static Factory Methods: Each build_*_workflow() creates specific workflow
    - Builder Pattern: Constructs complex workflow objects step-by-step
    """

    @staticmethod
    def build_architecture_invalid_workflow() -> Workflow:
        """
        Build workflow for invalid architecture fix

        ACTIONS:
        1. Regenerate architecture

        Returns workflow that regenerates invalid architecture.
        """
        return Workflow(
            name="Architecture Regeneration",
            issue_type=IssueType.ARCHITECTURE_INVALID,
            actions=[
                WorkflowAction(
                    action_name="Regenerate architecture",
                    handler=WorkflowHandlers.regenerate_architecture,
                    retry_on_failure=True,
                    max_retries=2
                )
            ],
            success_state=PipelineState.RUNNING,
            failure_state=PipelineState.FAILED
        )

    @staticmethod
    def build_code_review_failed_workflow() -> Workflow:
        """
        Build workflow for code review failure handling

        ACTIONS:
        1. Request code review revision

        Returns workflow that requests code revisions.
        """
        return Workflow(
            name="Code Review Revision",
            issue_type=IssueType.CODE_REVIEW_FAILED,
            actions=[
                WorkflowAction(
                    action_name="Request code review revision",
                    handler=WorkflowHandlers.request_code_review_revision
                )
            ],
            success_state=PipelineState.RUNNING,
            failure_state=PipelineState.DEGRADED
        )

    @staticmethod
    def build_integration_conflict_workflow() -> Workflow:
        """
        Build workflow for integration conflict resolution

        ACTIONS:
        1. Resolve integration conflict

        Returns workflow that resolves integration conflicts.
        """
        return Workflow(
            name="Integration Conflict Resolution",
            issue_type=IssueType.INTEGRATION_CONFLICT,
            actions=[
                WorkflowAction(
                    action_name="Resolve integration conflict",
                    handler=WorkflowHandlers.resolve_integration_conflict
                )
            ],
            success_state=PipelineState.RUNNING,
            failure_state=PipelineState.FAILED
        )

    @staticmethod
    def build_validation_failed_workflow() -> Workflow:
        """
        Build workflow for validation failure handling

        ACTIONS:
        1. Rerun validation

        Returns workflow that retries validation.
        """
        return Workflow(
            name="Validation Retry",
            issue_type=IssueType.VALIDATION_FAILED,
            actions=[
                WorkflowAction(
                    action_name="Rerun validation",
                    handler=WorkflowHandlers.rerun_validation,
                    retry_on_failure=True,
                    max_retries=2
                )
            ],
            success_state=PipelineState.RUNNING,
            failure_state=PipelineState.DEGRADED
        )

    @staticmethod
    def build_all() -> Dict[IssueType, Workflow]:
        """
        Build all stage workflows

        Returns:
            Dict mapping IssueType to Workflow for all stage issues
        """
        return {
            IssueType.ARCHITECTURE_INVALID: StageWorkflowBuilder.build_architecture_invalid_workflow(),
            IssueType.CODE_REVIEW_FAILED: StageWorkflowBuilder.build_code_review_failed_workflow(),
            IssueType.INTEGRATION_CONFLICT: StageWorkflowBuilder.build_integration_conflict_workflow(),
            IssueType.VALIDATION_FAILED: StageWorkflowBuilder.build_validation_failed_workflow(),
        }
