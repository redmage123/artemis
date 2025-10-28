#!/usr/bin/env python3
"""
Dependency Management Workflow Definitions

WHAT:
Recovery workflows for dependency-related failures including missing packages,
version conflicts, and import errors.

WHY:
Dependency issues are common in polyglot projects with complex dependency trees.
These workflows provide automated resolution paths using package managers.

RESPONSIBILITY:
- Define recovery workflows for dependency failures
- Configure retry strategies for package installation
- Handle version conflict resolution

PATTERNS:
- Builder Pattern: Each build_* method constructs a complete workflow
- Retry with Backoff: Package installation can fail due to network issues
- Conflict Resolution: Automated strategies for version conflicts

INTEGRATION:
- Used by: WorkflowBuilder, WorkflowRegistry
- Uses: workflow_handlers for package manager operations
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
# DEPENDENCY WORKFLOW BUILDERS
# ============================================================================

def build_missing_dependency_workflow() -> Workflow:
    """
    Build workflow for missing dependency resolution

    WHAT:
    Creates workflow to install missing dependencies using appropriate package manager.

    WHY:
    Missing dependencies prevent compilation and execution. Installing them
    automatically resolves the issue without manual intervention.

    STRATEGY:
    1. Install missing dependency (retry up to 3 times for network reliability)

    RETURNS:
        Workflow: Configured missing dependency fix workflow
    """
    return Workflow(
        name="Missing Dependency Fix",
        issue_type=IssueType.MISSING_DEPENDENCY,
        actions=[
            WorkflowAction(
                action_name="Install missing dependency",
                handler=WorkflowHandlers.install_missing_dependency,
                retry_on_failure=True,
                max_retries=3
            )
        ],
        success_state=PipelineState.RUNNING,
        failure_state=PipelineState.FAILED
    )


def build_version_conflict_workflow() -> Workflow:
    """
    Build workflow for version conflict resolution

    WHAT:
    Creates workflow to resolve version conflicts between dependencies.

    WHY:
    Version conflicts occur when multiple dependencies require incompatible
    versions of the same package. Automated resolution attempts to find
    compatible versions.

    STRATEGY:
    1. Resolve version conflict (retry up to 2 times)
       - Try upgrading conflicting packages
       - Try downgrading to compatible versions
       - Use package manager's resolver

    RETURNS:
        Workflow: Configured version conflict resolution workflow
    """
    return Workflow(
        name="Version Conflict Resolution",
        issue_type=IssueType.VERSION_CONFLICT,
        actions=[
            WorkflowAction(
                action_name="Resolve version conflict",
                handler=WorkflowHandlers.resolve_version_conflict,
                retry_on_failure=True,
                max_retries=2
            )
        ],
        success_state=PipelineState.RUNNING,
        failure_state=PipelineState.FAILED
    )


def build_import_error_workflow() -> Workflow:
    """
    Build workflow for import error fixes

    WHAT:
    Creates workflow to fix import errors by installing packages or fixing paths.

    WHY:
    Import errors occur when Python can't find required modules. This can be
    due to missing packages, incorrect PYTHONPATH, or wrong import statements.

    STRATEGY:
    1. Fix import error (retry up to 2 times)
       - Check if package needs installation
       - Verify PYTHONPATH is correct
       - Check for circular imports

    RETURNS:
        Workflow: Configured import error fix workflow
    """
    return Workflow(
        name="Import Error Fix",
        issue_type=IssueType.IMPORT_ERROR,
        actions=[
            WorkflowAction(
                action_name="Fix import error",
                handler=WorkflowHandlers.fix_import_error,
                retry_on_failure=True,
                max_retries=2
            )
        ],
        success_state=PipelineState.RUNNING,
        failure_state=PipelineState.FAILED
    )


# ============================================================================
# WORKFLOW CATALOG
# ============================================================================

def get_dependency_workflows() -> Dict[IssueType, Workflow]:
    """
    Get all dependency management workflows

    WHAT:
    Returns complete mapping of dependency issue types to workflows.

    WHY:
    Provides single point of access for all dependency workflows.
    Used by WorkflowRegistry to build complete workflow catalog.

    RETURNS:
        Dict[IssueType, Workflow]: Dependency workflows by issue type
    """
    return {
        IssueType.MISSING_DEPENDENCY: build_missing_dependency_workflow(),
        IssueType.VERSION_CONFLICT: build_version_conflict_workflow(),
        IssueType.IMPORT_ERROR: build_import_error_workflow(),
    }
