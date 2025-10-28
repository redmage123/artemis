#!/usr/bin/env python3
"""
WHY: Centralized workflow construction for all issue types
RESPONSIBILITY: Aggregate all workflow builders and provide unified interface
PATTERNS: Builder pattern, facade pattern, static factory methods

This module serves as the main entry point for workflow construction,
delegating to specialized builders for each category of issue.

USAGE:
    workflows = WorkflowBuilder.build_all_workflows()
    timeout_workflow = WorkflowBuilder.build_timeout_workflow()
"""

from typing import Dict
from workflows_core.models import Workflow, IssueType

# Import specialized builders
from workflows_core.infrastructure_workflows import InfrastructureWorkflowBuilder
from workflows_core.code_workflows import CodeWorkflowBuilder
from workflows_core.dependency_workflows import DependencyWorkflowBuilder
from workflows_core.llm_workflows import LLMWorkflowBuilder
from workflows_core.stage_workflows import StageWorkflowBuilder
from workflows_core.multiagent_workflows import MultiAgentWorkflowBuilder
from workflows_core.data_workflows import DataWorkflowBuilder
from workflows_core.system_workflows import SystemWorkflowBuilder


class WorkflowBuilder:
    """
    Main workflow builder - aggregates all specialized builders

    WHAT:
    Factory class that constructs complete recovery workflows for 30+ different
    pipeline failure scenarios by delegating to specialized builders.

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
    - Facade Pattern: Provides unified interface to specialized builders
    - Static Factory Methods: Each build_*_workflow() creates specific workflow

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

    EXAMPLE:
        timeout_workflow = WorkflowBuilder.build_timeout_workflow()
        # Actions: [increase_timeout, kill_hanging_process]
        # On success -> PipelineState.RUNNING (continue pipeline)
        # On failure -> PipelineState.FAILED (abort pipeline)
    """

    @staticmethod
    def build_all_workflows() -> Dict[IssueType, Workflow]:
        """
        Build all recovery workflows

        WHAT:
        Creates complete map of IssueType -> Workflow for all 30+ failure scenarios
        by delegating to specialized builders.

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
        workflows = {}

        # Build all workflow categories
        workflows.update(InfrastructureWorkflowBuilder.build_all())
        workflows.update(CodeWorkflowBuilder.build_all())
        workflows.update(DependencyWorkflowBuilder.build_all())
        workflows.update(LLMWorkflowBuilder.build_all())
        workflows.update(StageWorkflowBuilder.build_all())
        workflows.update(MultiAgentWorkflowBuilder.build_all())
        workflows.update(DataWorkflowBuilder.build_all())
        workflows.update(SystemWorkflowBuilder.build_all())

        return workflows

    # ========================================================================
    # INFRASTRUCTURE WORKFLOWS (Delegate to InfrastructureWorkflowBuilder)
    # ========================================================================

    @staticmethod
    def build_timeout_workflow() -> Workflow:
        """Workflow for timeout issues"""
        return InfrastructureWorkflowBuilder.build_timeout_workflow()

    @staticmethod
    def build_hanging_process_workflow() -> Workflow:
        """Workflow for hanging process issues"""
        return InfrastructureWorkflowBuilder.build_hanging_process_workflow()

    @staticmethod
    def build_memory_exhausted_workflow() -> Workflow:
        """Workflow for memory exhaustion issues"""
        return InfrastructureWorkflowBuilder.build_memory_exhausted_workflow()

    @staticmethod
    def build_disk_full_workflow() -> Workflow:
        """Workflow for disk full issues"""
        return InfrastructureWorkflowBuilder.build_disk_full_workflow()

    @staticmethod
    def build_network_error_workflow() -> Workflow:
        """Workflow for network error issues"""
        return InfrastructureWorkflowBuilder.build_network_error_workflow()

    # ========================================================================
    # CODE WORKFLOWS (Delegate to CodeWorkflowBuilder)
    # ========================================================================

    @staticmethod
    def build_compilation_error_workflow() -> Workflow:
        """Workflow for compilation error issues"""
        return CodeWorkflowBuilder.build_compilation_error_workflow()

    @staticmethod
    def build_test_failure_workflow() -> Workflow:
        """Workflow for test failure issues"""
        return CodeWorkflowBuilder.build_test_failure_workflow()

    @staticmethod
    def build_security_vulnerability_workflow() -> Workflow:
        """Workflow for security vulnerability issues"""
        return CodeWorkflowBuilder.build_security_vulnerability_workflow()

    @staticmethod
    def build_linting_error_workflow() -> Workflow:
        """Workflow for linting error issues"""
        return CodeWorkflowBuilder.build_linting_error_workflow()

    # ========================================================================
    # DEPENDENCY WORKFLOWS (Delegate to DependencyWorkflowBuilder)
    # ========================================================================

    @staticmethod
    def build_missing_dependency_workflow() -> Workflow:
        """Workflow for missing dependency issues"""
        return DependencyWorkflowBuilder.build_missing_dependency_workflow()

    @staticmethod
    def build_version_conflict_workflow() -> Workflow:
        """Workflow for version conflict issues"""
        return DependencyWorkflowBuilder.build_version_conflict_workflow()

    @staticmethod
    def build_import_error_workflow() -> Workflow:
        """Workflow for import error issues"""
        return DependencyWorkflowBuilder.build_import_error_workflow()

    # ========================================================================
    # LLM WORKFLOWS (Delegate to LLMWorkflowBuilder)
    # ========================================================================

    @staticmethod
    def build_llm_api_error_workflow() -> Workflow:
        """Workflow for LLM API error issues"""
        return LLMWorkflowBuilder.build_llm_api_error_workflow()

    @staticmethod
    def build_llm_timeout_workflow() -> Workflow:
        """Workflow for LLM timeout issues"""
        return LLMWorkflowBuilder.build_llm_timeout_workflow()

    @staticmethod
    def build_llm_rate_limit_workflow() -> Workflow:
        """Workflow for LLM rate limit issues"""
        return LLMWorkflowBuilder.build_llm_rate_limit_workflow()

    @staticmethod
    def build_invalid_llm_response_workflow() -> Workflow:
        """Workflow for invalid LLM response issues"""
        return LLMWorkflowBuilder.build_invalid_llm_response_workflow()

    # ========================================================================
    # STAGE WORKFLOWS (Delegate to StageWorkflowBuilder)
    # ========================================================================

    @staticmethod
    def build_architecture_invalid_workflow() -> Workflow:
        """Workflow for invalid architecture issues"""
        return StageWorkflowBuilder.build_architecture_invalid_workflow()

    @staticmethod
    def build_code_review_failed_workflow() -> Workflow:
        """Workflow for code review failure issues"""
        return StageWorkflowBuilder.build_code_review_failed_workflow()

    @staticmethod
    def build_integration_conflict_workflow() -> Workflow:
        """Workflow for integration conflict issues"""
        return StageWorkflowBuilder.build_integration_conflict_workflow()

    @staticmethod
    def build_validation_failed_workflow() -> Workflow:
        """Workflow for validation failure issues"""
        return StageWorkflowBuilder.build_validation_failed_workflow()

    # ========================================================================
    # MULTI-AGENT WORKFLOWS (Delegate to MultiAgentWorkflowBuilder)
    # ========================================================================

    @staticmethod
    def build_arbitration_deadlock_workflow() -> Workflow:
        """Workflow for arbitration deadlock issues"""
        return MultiAgentWorkflowBuilder.build_arbitration_deadlock_workflow()

    @staticmethod
    def build_developer_conflict_workflow() -> Workflow:
        """Workflow for developer conflict issues"""
        return MultiAgentWorkflowBuilder.build_developer_conflict_workflow()

    @staticmethod
    def build_messenger_error_workflow() -> Workflow:
        """Workflow for messenger error issues"""
        return MultiAgentWorkflowBuilder.build_messenger_error_workflow()

    # ========================================================================
    # DATA WORKFLOWS (Delegate to DataWorkflowBuilder)
    # ========================================================================

    @staticmethod
    def build_invalid_card_workflow() -> Workflow:
        """Workflow for invalid card issues"""
        return DataWorkflowBuilder.build_invalid_card_workflow()

    @staticmethod
    def build_corrupted_state_workflow() -> Workflow:
        """Workflow for corrupted state issues"""
        return DataWorkflowBuilder.build_corrupted_state_workflow()

    @staticmethod
    def build_rag_error_workflow() -> Workflow:
        """Workflow for RAG error issues"""
        return DataWorkflowBuilder.build_rag_error_workflow()

    # ========================================================================
    # SYSTEM WORKFLOWS (Delegate to SystemWorkflowBuilder)
    # ========================================================================

    @staticmethod
    def build_zombie_process_workflow() -> Workflow:
        """Workflow for zombie process issues"""
        return SystemWorkflowBuilder.build_zombie_process_workflow()

    @staticmethod
    def build_file_lock_workflow() -> Workflow:
        """Workflow for file lock issues"""
        return SystemWorkflowBuilder.build_file_lock_workflow()

    @staticmethod
    def build_permission_denied_workflow() -> Workflow:
        """Workflow for permission denied issues"""
        return SystemWorkflowBuilder.build_permission_denied_workflow()
