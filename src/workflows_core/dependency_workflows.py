#!/usr/bin/env python3
"""
WHY: Build recovery workflows for dependency-related failures
RESPONSIBILITY: Construct recovery workflows for missing dependencies, version conflicts, imports
PATTERNS: Builder pattern, factory methods, workflow composition

Dependency workflows handle:
- Missing dependencies
- Version conflicts
- Import errors

Each workflow defines actions to resolve dependency issues.
"""

from typing import Dict
from workflows_core.models import Workflow, WorkflowAction, IssueType, PipelineState
from workflow_handlers import WorkflowHandlers


class DependencyWorkflowBuilder:
    """
    Build recovery workflows for dependency issues

    WHAT:
    Factory class that constructs recovery workflows for dependency-related failures:
    missing dependencies, version conflicts, import errors.

    WHY:
    Dependency issues can block development. This builder provides standardized
    recovery procedures for each type of dependency issue.

    PATTERNS:
    - Static Factory Methods: Each build_*_workflow() creates specific workflow
    - Builder Pattern: Constructs complex workflow objects step-by-step
    """

    @staticmethod
    def build_missing_dependency_workflow() -> Workflow:
        """
        Build workflow for missing dependency fix

        ACTIONS:
        1. Install missing dependency

        Returns workflow that installs missing packages.
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

    @staticmethod
    def build_version_conflict_workflow() -> Workflow:
        """
        Build workflow for version conflict resolution

        ACTIONS:
        1. Resolve version conflict (update compatible versions)

        Returns workflow that resolves version conflicts.
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

    @staticmethod
    def build_import_error_workflow() -> Workflow:
        """
        Build workflow for import error fix

        ACTIONS:
        1. Fix import error (install package or fix import path)

        Returns workflow that resolves import errors.
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

    @staticmethod
    def build_all() -> Dict[IssueType, Workflow]:
        """
        Build all dependency workflows

        Returns:
            Dict mapping IssueType to Workflow for all dependency issues
        """
        return {
            IssueType.MISSING_DEPENDENCY: DependencyWorkflowBuilder.build_missing_dependency_workflow(),
            IssueType.VERSION_CONFLICT: DependencyWorkflowBuilder.build_version_conflict_workflow(),
            IssueType.IMPORT_ERROR: DependencyWorkflowBuilder.build_import_error_workflow(),
        }
