#!/usr/bin/env python3
"""
WHY: Build recovery workflows for data-related failures
RESPONSIBILITY: Construct recovery workflows for invalid cards, corrupted state, RAG errors
PATTERNS: Builder pattern, factory methods, workflow composition

Data workflows handle:
- Invalid card data
- Corrupted state
- RAG errors

Each workflow defines actions to resolve data integrity issues.
"""

from typing import Dict
from workflows_core.models import Workflow, WorkflowAction, IssueType, PipelineState
from workflow_handlers import WorkflowHandlers


class DataWorkflowBuilder:
    """
    Build recovery workflows for data issues

    WHAT:
    Factory class that constructs recovery workflows for data-related failures:
    invalid card, corrupted state, RAG errors.

    WHY:
    Data integrity is critical. This builder provides standardized
    recovery procedures for data issues.

    PATTERNS:
    - Static Factory Methods: Each build_*_workflow() creates specific workflow
    - Builder Pattern: Constructs complex workflow objects step-by-step
    """

    @staticmethod
    def build_invalid_card_workflow() -> Workflow:
        """
        Build workflow for invalid card data handling

        ACTIONS:
        1. Validate card data

        Returns workflow that validates and fixes card data.
        """
        return Workflow(
            name="Card Validation",
            issue_type=IssueType.INVALID_CARD,
            actions=[
                WorkflowAction(
                    action_name="Validate card data",
                    handler=WorkflowHandlers.validate_card_data
                )
            ],
            success_state=PipelineState.RUNNING,
            failure_state=PipelineState.FAILED
        )

    @staticmethod
    def build_corrupted_state_workflow() -> Workflow:
        """
        Build workflow for corrupted state recovery

        ACTIONS:
        1. Restore state from backup

        Returns workflow that restores corrupted state from backup.
        """
        return Workflow(
            name="State Restoration",
            issue_type=IssueType.CORRUPTED_STATE,
            actions=[
                WorkflowAction(
                    action_name="Restore state from backup",
                    handler=WorkflowHandlers.restore_state_from_backup
                )
            ],
            success_state=PipelineState.RUNNING,
            failure_state=PipelineState.FAILED,
            rollback_on_failure=False
        )

    @staticmethod
    def build_rag_error_workflow() -> Workflow:
        """
        Build workflow for RAG error handling

        ACTIONS:
        1. Rebuild RAG index

        Returns workflow that rebuilds RAG index.
        """
        return Workflow(
            name="RAG Index Rebuild",
            issue_type=IssueType.RAG_ERROR,
            actions=[
                WorkflowAction(
                    action_name="Rebuild RAG index",
                    handler=WorkflowHandlers.rebuild_rag_index
                )
            ],
            success_state=PipelineState.RUNNING,
            failure_state=PipelineState.DEGRADED
        )

    @staticmethod
    def build_all() -> Dict[IssueType, Workflow]:
        """
        Build all data workflows

        Returns:
            Dict mapping IssueType to Workflow for all data issues
        """
        return {
            IssueType.INVALID_CARD: DataWorkflowBuilder.build_invalid_card_workflow(),
            IssueType.CORRUPTED_STATE: DataWorkflowBuilder.build_corrupted_state_workflow(),
            IssueType.RAG_ERROR: DataWorkflowBuilder.build_rag_error_workflow(),
        }
