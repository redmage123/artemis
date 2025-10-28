#!/usr/bin/env python3
"""
Workflow Definitions Package - Recovery Workflow Catalog

WHAT:
Comprehensive collection of recovery workflows organized by failure category.
Each module contains workflows for a specific domain (infrastructure, code, etc.).

WHY:
Modular organization allows easy maintenance, testing, and extension of workflows.
Each category is independent, making it simple to add new workflows or modify
existing ones without affecting other categories.

RESPONSIBILITY:
- Export all workflow builder functions
- Provide catalog functions for each category
- Aggregate workflows into complete registry

PATTERNS:
- Module Organization: One module per workflow category
- Factory Functions: Each module exports get_*_workflows()
- Aggregation: This __init__ combines all workflows

INTEGRATION:
- Used by: WorkflowBuilder, WorkflowRegistry
- Exports: Individual workflow builders and category catalogs

CATEGORIES:
1. Infrastructure (5 workflows): timeout, hanging, memory, disk, network
2. Code (4 workflows): compilation, tests, security, linting
3. Dependencies (3 workflows): missing deps, conflicts, imports
4. LLM (4 workflows): API errors, timeouts, rate limits, invalid responses
5. Stage (4 workflows): architecture, review, integration, validation
6. Multi-agent (3 workflows): deadlock, conflicts, messenger
7. Data (3 workflows): invalid card, corrupted state, RAG errors
8. System (3 workflows): zombies, file locks, permissions

Total: 30 recovery workflows
"""

from typing import Dict, Any, Optional, List, Callable

from state_machine import IssueType, Workflow

# Import workflow builders from each category
from workflows.definitions.infrastructure_workflows import (
    build_timeout_workflow,
    build_hanging_process_workflow,
    build_memory_exhausted_workflow,
    build_disk_full_workflow,
    build_network_error_workflow,
    get_infrastructure_workflows,
)

from workflows.definitions.code_workflows import (
    build_compilation_error_workflow,
    build_test_failure_workflow,
    build_security_vulnerability_workflow,
    build_linting_error_workflow,
    get_code_workflows,
)

from workflows.definitions.dependency_workflows import (
    build_missing_dependency_workflow,
    build_version_conflict_workflow,
    build_import_error_workflow,
    get_dependency_workflows,
)

from workflows.definitions.llm_workflows import (
    build_llm_api_error_workflow,
    build_llm_timeout_workflow,
    build_llm_rate_limit_workflow,
    build_invalid_llm_response_workflow,
    get_llm_workflows,
)

from workflows.definitions.stage_workflows import (
    build_architecture_invalid_workflow,
    build_code_review_failed_workflow,
    build_integration_conflict_workflow,
    build_validation_failed_workflow,
    get_stage_workflows,
)

from workflows.definitions.multiagent_workflows import (
    build_arbitration_deadlock_workflow,
    build_developer_conflict_workflow,
    build_messenger_error_workflow,
    get_multiagent_workflows,
)

from workflows.definitions.data_workflows import (
    build_invalid_card_workflow,
    build_corrupted_state_workflow,
    build_rag_error_workflow,
    get_data_workflows,
)

from workflows.definitions.system_workflows import (
    build_zombie_process_workflow,
    build_file_lock_workflow,
    build_permission_denied_workflow,
    get_system_workflows,
)


# ============================================================================
# AGGREGATE WORKFLOW CATALOG
# ============================================================================

def get_all_workflow_definitions() -> Dict[IssueType, Workflow]:
    """
    Get complete catalog of all workflow definitions

    WHAT:
    Aggregates workflows from all categories into single comprehensive catalog.

    WHY:
    Provides single point of access for all 30+ recovery workflows.
    Used by WorkflowRegistry to build complete workflow map.

    RETURNS:
        Dict[IssueType, Workflow]: Complete workflow catalog (30+ entries)

    WORKFLOW BREAKDOWN:
        - Infrastructure: 5 workflows
        - Code: 4 workflows
        - Dependencies: 3 workflows
        - LLM: 4 workflows
        - Stage: 4 workflows
        - Multi-agent: 3 workflows
        - Data: 3 workflows
        - System: 3 workflows
    """
    workflows = {}

    # Aggregate all category workflows
    workflows.update(get_infrastructure_workflows())
    workflows.update(get_code_workflows())
    workflows.update(get_dependency_workflows())
    workflows.update(get_llm_workflows())
    workflows.update(get_stage_workflows())
    workflows.update(get_multiagent_workflows())
    workflows.update(get_data_workflows())
    workflows.update(get_system_workflows())

    return workflows


__all__ = [
    # Infrastructure workflows
    "build_timeout_workflow",
    "build_hanging_process_workflow",
    "build_memory_exhausted_workflow",
    "build_disk_full_workflow",
    "build_network_error_workflow",
    "get_infrastructure_workflows",

    # Code workflows
    "build_compilation_error_workflow",
    "build_test_failure_workflow",
    "build_security_vulnerability_workflow",
    "build_linting_error_workflow",
    "get_code_workflows",

    # Dependency workflows
    "build_missing_dependency_workflow",
    "build_version_conflict_workflow",
    "build_import_error_workflow",
    "get_dependency_workflows",

    # LLM workflows
    "build_llm_api_error_workflow",
    "build_llm_timeout_workflow",
    "build_llm_rate_limit_workflow",
    "build_invalid_llm_response_workflow",
    "get_llm_workflows",

    # Stage workflows
    "build_architecture_invalid_workflow",
    "build_code_review_failed_workflow",
    "build_integration_conflict_workflow",
    "build_validation_failed_workflow",
    "get_stage_workflows",

    # Multi-agent workflows
    "build_arbitration_deadlock_workflow",
    "build_developer_conflict_workflow",
    "build_messenger_error_workflow",
    "get_multiagent_workflows",

    # Data workflows
    "build_invalid_card_workflow",
    "build_corrupted_state_workflow",
    "build_rag_error_workflow",
    "get_data_workflows",

    # System workflows
    "build_zombie_process_workflow",
    "build_file_lock_workflow",
    "build_permission_denied_workflow",
    "get_system_workflows",

    # Aggregate catalog
    "get_all_workflow_definitions",
]
