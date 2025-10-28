#!/usr/bin/env python3
"""
Data Management Workflow Definitions

WHAT:
Recovery workflows for data-related failures including invalid cards,
corrupted state, and RAG index errors.

WHY:
Data integrity is critical for pipeline operation. These workflows provide
recovery paths for data corruption, validation failures, and index issues.

RESPONSIBILITY:
- Define recovery workflows for data failures
- Configure validation and restoration strategies
- Handle RAG index maintenance

PATTERNS:
- Builder Pattern: Each build_* method constructs a complete workflow
- State Restoration: Backup/restore strategies for corrupted state
- Index Rebuild: Fresh indexing when RAG becomes corrupted

INTEGRATION:
- Used by: WorkflowBuilder, WorkflowRegistry
- Uses: workflow_handlers for data operations
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
# DATA WORKFLOW BUILDERS
# ============================================================================

def build_invalid_card_workflow() -> Workflow:
    """
    Build workflow for invalid card validation

    WHAT:
    Creates workflow to validate and fix invalid Kanban cards.

    WHY:
    Invalid cards (missing fields, wrong format, bad references) prevent
    pipeline progress. Validation identifies issues that need fixing.

    STRATEGY:
    1. Validate card data
       - Check required fields are present
       - Verify field formats and types
       - Validate cross-references
       - Fix common issues automatically

    RETURNS:
        Workflow: Configured card validation workflow
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


def build_corrupted_state_workflow() -> Workflow:
    """
    Build workflow for corrupted state recovery

    WHAT:
    Creates workflow to restore pipeline state from backup when corruption detected.

    WHY:
    State corruption (incomplete writes, crashes, concurrent access) can leave
    pipeline in inconsistent state. Restoring from backup recovers to last
    known-good state.

    STRATEGY:
    1. Restore state from backup
       - Identify most recent valid backup
       - Validate backup integrity
       - Restore state from backup
       - Resume pipeline from restored checkpoint

    NOTE:
    No rollback on failure (already in recovery mode).

    RETURNS:
        Workflow: Configured state restoration workflow
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


def build_rag_error_workflow() -> Workflow:
    """
    Build workflow for RAG index error recovery

    WHAT:
    Creates workflow to rebuild RAG vector index when errors occur.

    WHY:
    RAG index can become corrupted or outdated, causing query failures.
    Rebuilding index from source documents restores functionality.

    STRATEGY:
    1. Rebuild RAG index
       - Clear existing index
       - Re-index all documents
       - Verify index integrity
       - Test query functionality

    NOTE:
    RAG failures don't stop pipeline (DEGRADED) but reduce quality.

    RETURNS:
        Workflow: Configured RAG index rebuild workflow
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


# ============================================================================
# WORKFLOW CATALOG
# ============================================================================

def get_data_workflows() -> Dict[IssueType, Workflow]:
    """
    Get all data management workflows

    WHAT:
    Returns complete mapping of data issue types to workflows.

    WHY:
    Provides single point of access for all data workflows.
    Used by WorkflowRegistry to build complete workflow catalog.

    RETURNS:
        Dict[IssueType, Workflow]: Data workflows by issue type
    """
    return {
        IssueType.INVALID_CARD: build_invalid_card_workflow(),
        IssueType.CORRUPTED_STATE: build_corrupted_state_workflow(),
        IssueType.RAG_ERROR: build_rag_error_workflow(),
    }
