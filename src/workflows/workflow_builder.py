#!/usr/bin/env python3
"""
Workflow Builder - Factory for Recovery Workflows

WHAT:
Factory class that constructs complete recovery workflows for all pipeline
failure scenarios. Provides backward-compatible interface matching original
WorkflowBuilder API.

WHY:
Centralizes workflow construction logic while delegating actual workflow
definitions to specialized modules. Acts as facade over workflow definitions
package, providing simple API for workflow retrieval.

RESPONSIBILITY:
- Provide factory methods for all workflow types
- Delegate to workflow definition modules
- Maintain backward compatibility with original API
- Provide build_all_workflows() for complete catalog

PATTERNS:
- Builder Pattern: Constructs complex workflow objects
- Factory Pattern: Creates workflows based on issue type
- Facade Pattern: Simplifies access to workflow definitions
- Static Factory Methods: Class methods for workflow construction

INTEGRATION:
- Used by: SupervisorAgent, WorkflowRegistry
- Uses: workflows.definitions modules for actual definitions
- API: Compatible with original artemis_workflows.WorkflowBuilder

EXAMPLE:
    # Get all workflows
    workflows = WorkflowBuilder.build_all_workflows()

    # Get specific workflow
    timeout_workflow = WorkflowBuilder.build_timeout_workflow()
"""

from typing import Dict, Any, Optional, List, Callable

from state_machine import IssueType, Workflow

# Import workflow builders from definitions package
from workflows.definitions import (
    # Infrastructure
    build_timeout_workflow,
    build_hanging_process_workflow,
    build_memory_exhausted_workflow,
    build_disk_full_workflow,
    build_network_error_workflow,

    # Code
    build_compilation_error_workflow,
    build_test_failure_workflow,
    build_security_vulnerability_workflow,
    build_linting_error_workflow,

    # Dependencies
    build_missing_dependency_workflow,
    build_version_conflict_workflow,
    build_import_error_workflow,

    # LLM
    build_llm_api_error_workflow,
    build_llm_timeout_workflow,
    build_llm_rate_limit_workflow,
    build_invalid_llm_response_workflow,

    # Stage
    build_architecture_invalid_workflow,
    build_code_review_failed_workflow,
    build_integration_conflict_workflow,
    build_validation_failed_workflow,

    # Multi-agent
    build_arbitration_deadlock_workflow,
    build_developer_conflict_workflow,
    build_messenger_error_workflow,

    # Data
    build_invalid_card_workflow,
    build_corrupted_state_workflow,
    build_rag_error_workflow,

    # System
    build_zombie_process_workflow,
    build_file_lock_workflow,
    build_permission_denied_workflow,

    # Aggregate
    get_all_workflow_definitions,
)


# ============================================================================
# WORKFLOW BUILDER (BACKWARD COMPATIBLE API)
# ============================================================================

class WorkflowBuilder:
    """
    Build recovery workflows for all issue types

    WHAT:
    Factory class that constructs complete recovery workflows for 30+ different
    pipeline failure scenarios, from timeout errors to LLM rate limits to zombie processes.

    WHY:
    Pipeline failures are inevitable in autonomous systems. Rather than failing fast,
    Artemis attempts intelligent recovery using predefined workflows. Each workflow
    contains a sequence of actions to diagnose and fix the specific issue.

    This builder centralizes workflow construction, making it easy to:
    - Add new recovery workflows
    - Modify existing workflows
    - Test recovery logic
    - Document recovery procedures

    PATTERNS:
    - Builder Pattern: Constructs complex workflow objects step-by-step
    - Factory Pattern: Creates workflows based on issue type
    - Static Factory Methods: Each build_*_workflow() creates specific workflow
    - Facade Pattern: Provides simple API over workflow definitions

    WORKFLOW CATEGORIES:
    1. Infrastructure (5 workflows): timeout, hanging process, memory, disk, network
    2. Code (4 workflows): compilation, tests, security, linting
    3. Dependencies (3 workflows): missing deps, version conflicts, imports
    4. LLM (4 workflows): API errors, timeouts, rate limits, invalid responses
    5. Stages (4 workflows): architecture, code review, integration, validation
    6. Multi-agent (3 workflows): arbitration deadlock, developer conflicts, messenger
    7. Data (3 workflows): invalid card, corrupted state, RAG errors
    8. System (3 workflows): zombie processes, file locks, permissions

    INTEGRATION:
    - Used by: SupervisorAgent to execute recovery workflows
    - Uses: WorkflowHandlers for action execution
    - Creates: Workflow objects with action sequences

    EXAMPLE WORKFLOW:
        timeout_workflow = WorkflowBuilder.build_timeout_workflow()
        # Actions: [increase_timeout, kill_hanging_process]
        # On success → PipelineState.RUNNING (continue pipeline)
        # On failure → PipelineState.FAILED (abort pipeline)
    """

    @staticmethod
    def build_all_workflows() -> Dict[IssueType, Workflow]:
        """
        Build all recovery workflows

        WHAT:
        Creates complete map of IssueType → Workflow for all 30+ failure scenarios.

        WHY:
        SupervisorAgent needs quick O(1) lookup of recovery workflow for any issue.
        Building all workflows upfront (at initialization) is more efficient than
        building on-demand and enables validation that all issue types have workflows.

        RETURNS:
            Dict[IssueType, Workflow]: Complete workflow map (30+ entries)

        WORKFLOW CATEGORIES:
            - Infrastructure: 5 workflows
            - Code: 4 workflows
            - Dependencies: 3 workflows
            - LLM: 4 workflows
            - Stages: 4 workflows
            - Multi-agent: 3 workflows
            - Data: 3 workflows
            - System: 3 workflows
        """
        return get_all_workflow_definitions()

    # ========================================================================
    # INFRASTRUCTURE WORKFLOWS
    # ========================================================================

    @staticmethod
    def build_timeout_workflow() -> Workflow:
        """Workflow for timeout issues"""
        return build_timeout_workflow()

    @staticmethod
    def build_hanging_process_workflow() -> Workflow:
        """Workflow for hanging process issues"""
        return build_hanging_process_workflow()

    @staticmethod
    def build_memory_exhausted_workflow() -> Workflow:
        """Workflow for memory exhaustion issues"""
        return build_memory_exhausted_workflow()

    @staticmethod
    def build_disk_full_workflow() -> Workflow:
        """Workflow for disk full issues"""
        return build_disk_full_workflow()

    @staticmethod
    def build_network_error_workflow() -> Workflow:
        """Workflow for network error issues"""
        return build_network_error_workflow()

    # ========================================================================
    # CODE ISSUE WORKFLOWS
    # ========================================================================

    @staticmethod
    def build_compilation_error_workflow() -> Workflow:
        """Workflow for compilation error issues"""
        return build_compilation_error_workflow()

    @staticmethod
    def build_test_failure_workflow() -> Workflow:
        """Workflow for test failure issues"""
        return build_test_failure_workflow()

    @staticmethod
    def build_security_vulnerability_workflow() -> Workflow:
        """Workflow for security vulnerability issues"""
        return build_security_vulnerability_workflow()

    @staticmethod
    def build_linting_error_workflow() -> Workflow:
        """Workflow for linting error issues"""
        return build_linting_error_workflow()

    # ========================================================================
    # DEPENDENCY ISSUE WORKFLOWS
    # ========================================================================

    @staticmethod
    def build_missing_dependency_workflow() -> Workflow:
        """Workflow for missing dependency issues"""
        return build_missing_dependency_workflow()

    @staticmethod
    def build_version_conflict_workflow() -> Workflow:
        """Workflow for version conflict issues"""
        return build_version_conflict_workflow()

    @staticmethod
    def build_import_error_workflow() -> Workflow:
        """Workflow for import error issues"""
        return build_import_error_workflow()

    # ========================================================================
    # LLM ISSUE WORKFLOWS
    # ========================================================================

    @staticmethod
    def build_llm_api_error_workflow() -> Workflow:
        """Workflow for LLM API error issues"""
        return build_llm_api_error_workflow()

    @staticmethod
    def build_llm_timeout_workflow() -> Workflow:
        """Workflow for LLM timeout issues"""
        return build_llm_timeout_workflow()

    @staticmethod
    def build_llm_rate_limit_workflow() -> Workflow:
        """Workflow for LLM rate limit issues"""
        return build_llm_rate_limit_workflow()

    @staticmethod
    def build_invalid_llm_response_workflow() -> Workflow:
        """Workflow for invalid LLM response issues"""
        return build_invalid_llm_response_workflow()

    # ========================================================================
    # STAGE-SPECIFIC WORKFLOWS
    # ========================================================================

    @staticmethod
    def build_architecture_invalid_workflow() -> Workflow:
        """Workflow for invalid architecture issues"""
        return build_architecture_invalid_workflow()

    @staticmethod
    def build_code_review_failed_workflow() -> Workflow:
        """Workflow for code review failure issues"""
        return build_code_review_failed_workflow()

    @staticmethod
    def build_integration_conflict_workflow() -> Workflow:
        """Workflow for integration conflict issues"""
        return build_integration_conflict_workflow()

    @staticmethod
    def build_validation_failed_workflow() -> Workflow:
        """Workflow for validation failure issues"""
        return build_validation_failed_workflow()

    # ========================================================================
    # MULTI-AGENT WORKFLOWS
    # ========================================================================

    @staticmethod
    def build_arbitration_deadlock_workflow() -> Workflow:
        """Workflow for arbitration deadlock issues"""
        return build_arbitration_deadlock_workflow()

    @staticmethod
    def build_developer_conflict_workflow() -> Workflow:
        """Workflow for developer conflict issues"""
        return build_developer_conflict_workflow()

    @staticmethod
    def build_messenger_error_workflow() -> Workflow:
        """Workflow for messenger error issues"""
        return build_messenger_error_workflow()

    # ========================================================================
    # DATA ISSUE WORKFLOWS
    # ========================================================================

    @staticmethod
    def build_invalid_card_workflow() -> Workflow:
        """Workflow for invalid card issues"""
        return build_invalid_card_workflow()

    @staticmethod
    def build_corrupted_state_workflow() -> Workflow:
        """Workflow for corrupted state issues"""
        return build_corrupted_state_workflow()

    @staticmethod
    def build_rag_error_workflow() -> Workflow:
        """Workflow for RAG error issues"""
        return build_rag_error_workflow()

    # ========================================================================
    # SYSTEM ISSUE WORKFLOWS
    # ========================================================================

    @staticmethod
    def build_zombie_process_workflow() -> Workflow:
        """Workflow for zombie process issues"""
        return build_zombie_process_workflow()

    @staticmethod
    def build_file_lock_workflow() -> Workflow:
        """Workflow for file lock issues"""
        return build_file_lock_workflow()

    @staticmethod
    def build_permission_denied_workflow() -> Workflow:
        """Workflow for permission denied issues"""
        return build_permission_denied_workflow()
