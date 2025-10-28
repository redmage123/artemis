#!/usr/bin/env python3
"""
Pipeline Stage Workflow Definitions

WHAT:
Recovery workflows for stage-specific failures including architecture validation,
code review, integration conflicts, and validation failures.

WHY:
Each pipeline stage can fail in specific ways. These workflows provide
stage-aware recovery strategies that understand the context of failures.

RESPONSIBILITY:
- Define recovery workflows for stage failures
- Configure retry strategies for regeneration
- Handle stage-specific validation

PATTERNS:
- Builder Pattern: Each build_* method constructs a complete workflow
- Regeneration Strategy: Some failures require regenerating stage outputs
- Degraded Continuation: Some failures allow pipeline to continue with warnings

INTEGRATION:
- Used by: WorkflowBuilder, WorkflowRegistry
- Uses: workflow_handlers for stage operations
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
# STAGE WORKFLOW BUILDERS
# ============================================================================

def build_architecture_invalid_workflow() -> Workflow:
    """
    Build workflow for invalid architecture recovery

    WHAT:
    Creates workflow to regenerate architecture when validation fails.

    WHY:
    Architecture validation can fail if design is incomplete, inconsistent,
    or violates requirements. Regeneration with feedback often produces
    valid architecture.

    STRATEGY:
    1. Regenerate architecture (retry up to 2 times with validation feedback)

    RETURNS:
        Workflow: Configured architecture regeneration workflow
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


def build_code_review_failed_workflow() -> Workflow:
    """
    Build workflow for code review failure handling

    WHAT:
    Creates workflow to request code review revisions when review fails.

    WHY:
    Code review failures indicate quality issues that need addressing.
    Requesting revision with specific feedback allows developers to fix issues.

    STRATEGY:
    1. Request code review revision (with detailed feedback)

    NOTE:
    Review failures don't stop pipeline (DEGRADED) but require action.

    RETURNS:
        Workflow: Configured code review revision workflow
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


def build_integration_conflict_workflow() -> Workflow:
    """
    Build workflow for integration conflict resolution

    WHAT:
    Creates workflow to resolve conflicts when integrating component changes.

    WHY:
    Integration conflicts occur when multiple developers modify overlapping code.
    Automated conflict resolution attempts to merge changes intelligently.

    STRATEGY:
    1. Resolve integration conflict (analyze conflicts, apply merge strategy)

    RETURNS:
        Workflow: Configured integration conflict resolution workflow
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


def build_validation_failed_workflow() -> Workflow:
    """
    Build workflow for validation failure recovery

    WHAT:
    Creates workflow to rerun validation when it fails.

    WHY:
    Validation can fail due to transient issues (environment, timing).
    Rerunning validation helps distinguish real failures from false positives.

    STRATEGY:
    1. Rerun validation (retry up to 2 times)

    NOTE:
    Validation failures don't always stop pipeline (DEGRADED).

    RETURNS:
        Workflow: Configured validation retry workflow
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


# ============================================================================
# WORKFLOW CATALOG
# ============================================================================

def get_stage_workflows() -> Dict[IssueType, Workflow]:
    """
    Get all stage-specific workflows

    WHAT:
    Returns complete mapping of stage issue types to workflows.

    WHY:
    Provides single point of access for all stage workflows.
    Used by WorkflowRegistry to build complete workflow catalog.

    RETURNS:
        Dict[IssueType, Workflow]: Stage workflows by issue type
    """
    return {
        IssueType.ARCHITECTURE_INVALID: build_architecture_invalid_workflow(),
        IssueType.CODE_REVIEW_FAILED: build_code_review_failed_workflow(),
        IssueType.INTEGRATION_CONFLICT: build_integration_conflict_workflow(),
        IssueType.VALIDATION_FAILED: build_validation_failed_workflow(),
    }
