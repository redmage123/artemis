#!/usr/bin/env python3
"""
Artemis Recovery Workflows - Automated Issue Resolution

Defines recovery workflows for all possible issues in the Artemis pipeline.
Each workflow contains a sequence of actions to diagnose and fix the issue.

Workflow Categories:
1. Infrastructure Issues (timeout, memory, disk, network)
2. Code Issues (compilation, tests, security, linting)
3. Dependency Issues (missing deps, version conflicts)
4. LLM Issues (API errors, timeouts, rate limits)
5. Stage Issues (architecture, code review, integration)
6. Multi-Agent Issues (arbitration, conflicts)
7. Data Issues (invalid card, corrupted state, RAG)
8. System Issues (zombies, file locks, permissions)
"""

import os
import psutil
import shutil
import subprocess
import time
from typing import Dict, Any, Optional
from pathlib import Path

from artemis_state_machine import (
    IssueType,
    Workflow,
    WorkflowAction,
    PipelineState
)
from artemis_constants import (
    MAX_RETRY_ATTEMPTS,
    DEFAULT_RETRY_INTERVAL_SECONDS,
    RETRY_BACKOFF_FACTOR
)

# Import refactored handlers (with backward compatibility)
from workflow_handlers import WorkflowHandlers


# ============================================================================
# WORKFLOW BUILDER
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
        return {
            # Infrastructure issues
            IssueType.TIMEOUT: WorkflowBuilder.build_timeout_workflow(),
            IssueType.HANGING_PROCESS: WorkflowBuilder.build_hanging_process_workflow(),
            IssueType.MEMORY_EXHAUSTED: WorkflowBuilder.build_memory_exhausted_workflow(),
            IssueType.DISK_FULL: WorkflowBuilder.build_disk_full_workflow(),
            IssueType.NETWORK_ERROR: WorkflowBuilder.build_network_error_workflow(),

            # Code issues
            IssueType.COMPILATION_ERROR: WorkflowBuilder.build_compilation_error_workflow(),
            IssueType.TEST_FAILURE: WorkflowBuilder.build_test_failure_workflow(),
            IssueType.SECURITY_VULNERABILITY: WorkflowBuilder.build_security_vulnerability_workflow(),
            IssueType.LINTING_ERROR: WorkflowBuilder.build_linting_error_workflow(),

            # Dependency issues
            IssueType.MISSING_DEPENDENCY: WorkflowBuilder.build_missing_dependency_workflow(),
            IssueType.VERSION_CONFLICT: WorkflowBuilder.build_version_conflict_workflow(),
            IssueType.IMPORT_ERROR: WorkflowBuilder.build_import_error_workflow(),

            # LLM issues
            IssueType.LLM_API_ERROR: WorkflowBuilder.build_llm_api_error_workflow(),
            IssueType.LLM_TIMEOUT: WorkflowBuilder.build_llm_timeout_workflow(),
            IssueType.LLM_RATE_LIMIT: WorkflowBuilder.build_llm_rate_limit_workflow(),
            IssueType.INVALID_LLM_RESPONSE: WorkflowBuilder.build_invalid_llm_response_workflow(),

            # Stage-specific issues
            IssueType.ARCHITECTURE_INVALID: WorkflowBuilder.build_architecture_invalid_workflow(),
            IssueType.CODE_REVIEW_FAILED: WorkflowBuilder.build_code_review_failed_workflow(),
            IssueType.INTEGRATION_CONFLICT: WorkflowBuilder.build_integration_conflict_workflow(),
            IssueType.VALIDATION_FAILED: WorkflowBuilder.build_validation_failed_workflow(),

            # Multi-agent issues
            IssueType.ARBITRATION_DEADLOCK: WorkflowBuilder.build_arbitration_deadlock_workflow(),
            IssueType.DEVELOPER_CONFLICT: WorkflowBuilder.build_developer_conflict_workflow(),
            IssueType.MESSENGER_ERROR: WorkflowBuilder.build_messenger_error_workflow(),

            # Data issues
            IssueType.INVALID_CARD: WorkflowBuilder.build_invalid_card_workflow(),
            IssueType.CORRUPTED_STATE: WorkflowBuilder.build_corrupted_state_workflow(),
            IssueType.RAG_ERROR: WorkflowBuilder.build_rag_error_workflow(),

            # System issues
            IssueType.ZOMBIE_PROCESS: WorkflowBuilder.build_zombie_process_workflow(),
            IssueType.FILE_LOCK: WorkflowBuilder.build_file_lock_workflow(),
            IssueType.PERMISSION_DENIED: WorkflowBuilder.build_permission_denied_workflow(),
        }

    # ========================================================================
    # INFRASTRUCTURE WORKFLOWS
    # ========================================================================

    @staticmethod
    def build_timeout_workflow() -> Workflow:
        """Workflow for timeout issues"""
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
        """Workflow for hanging process issues"""
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
        """Workflow for memory exhaustion issues"""
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
        """Workflow for disk full issues"""
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
        """Workflow for network error issues"""
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

    # ========================================================================
    # CODE ISSUE WORKFLOWS
    # ========================================================================

    @staticmethod
    def build_compilation_error_workflow() -> Workflow:
        """Workflow for compilation error issues"""
        return Workflow(
            name="Compilation Error Recovery",
            issue_type=IssueType.COMPILATION_ERROR,
            actions=[
                WorkflowAction(
                    action_name="Retry compilation",
                    handler=WorkflowHandlers.retry_compilation,
                    retry_on_failure=True,
                    max_retries=2
                )
            ],
            success_state=PipelineState.RUNNING,
            failure_state=PipelineState.FAILED
        )

    @staticmethod
    def build_test_failure_workflow() -> Workflow:
        """Workflow for test failure issues"""
        return Workflow(
            name="Test Failure Recovery",
            issue_type=IssueType.TEST_FAILURE,
            actions=[
                WorkflowAction(
                    action_name="Rerun tests",
                    handler=WorkflowHandlers.rerun_tests,
                    retry_on_failure=True,
                    max_retries=2
                )
            ],
            success_state=PipelineState.RUNNING,
            failure_state=PipelineState.FAILED
        )

    @staticmethod
    def build_security_vulnerability_workflow() -> Workflow:
        """Workflow for security vulnerability issues"""
        return Workflow(
            name="Security Vulnerability Fix",
            issue_type=IssueType.SECURITY_VULNERABILITY,
            actions=[
                WorkflowAction(
                    action_name="Apply security patch",
                    handler=WorkflowHandlers.fix_security_vulnerability
                )
            ],
            success_state=PipelineState.RUNNING,
            failure_state=PipelineState.FAILED
        )

    @staticmethod
    def build_linting_error_workflow() -> Workflow:
        """Workflow for linting error issues"""
        return Workflow(
            name="Linting Error Fix",
            issue_type=IssueType.LINTING_ERROR,
            actions=[
                WorkflowAction(
                    action_name="Run linter auto-fix",
                    handler=WorkflowHandlers.run_linter_fix
                )
            ],
            success_state=PipelineState.RUNNING,
            failure_state=PipelineState.DEGRADED
        )

    # ========================================================================
    # DEPENDENCY ISSUE WORKFLOWS
    # ========================================================================

    @staticmethod
    def build_missing_dependency_workflow() -> Workflow:
        """Workflow for missing dependency issues"""
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
        """Workflow for version conflict issues"""
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
        """Workflow for import error issues"""
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

    # ========================================================================
    # LLM ISSUE WORKFLOWS
    # ========================================================================

    @staticmethod
    def build_llm_api_error_workflow() -> Workflow:
        """Workflow for LLM API error issues"""
        return Workflow(
            name="LLM API Error Recovery",
            issue_type=IssueType.LLM_API_ERROR,
            actions=[
                WorkflowAction(
                    action_name="Retry LLM request",
                    handler=WorkflowHandlers.retry_llm_request,
                    retry_on_failure=True,
                    max_retries=3
                ),
                WorkflowAction(
                    action_name="Switch LLM provider",
                    handler=WorkflowHandlers.switch_llm_provider
                )
            ],
            success_state=PipelineState.RUNNING,
            failure_state=PipelineState.DEGRADED
        )

    @staticmethod
    def build_llm_timeout_workflow() -> Workflow:
        """Workflow for LLM timeout issues"""
        return Workflow(
            name="LLM Timeout Recovery",
            issue_type=IssueType.LLM_TIMEOUT,
            actions=[
                WorkflowAction(
                    action_name="Retry LLM request",
                    handler=WorkflowHandlers.retry_llm_request,
                    retry_on_failure=True,
                    max_retries=2
                )
            ],
            success_state=PipelineState.RUNNING,
            failure_state=PipelineState.DEGRADED
        )

    @staticmethod
    def build_llm_rate_limit_workflow() -> Workflow:
        """Workflow for LLM rate limit issues"""
        return Workflow(
            name="LLM Rate Limit Handling",
            issue_type=IssueType.LLM_RATE_LIMIT,
            actions=[
                WorkflowAction(
                    action_name="Handle rate limit",
                    handler=WorkflowHandlers.handle_rate_limit,
                    retry_on_failure=False
                ),
                WorkflowAction(
                    action_name="Switch LLM provider",
                    handler=WorkflowHandlers.switch_llm_provider
                )
            ],
            success_state=PipelineState.RUNNING,
            failure_state=PipelineState.DEGRADED
        )

    @staticmethod
    def build_invalid_llm_response_workflow() -> Workflow:
        """Workflow for invalid LLM response issues"""
        return Workflow(
            name="LLM Response Validation",
            issue_type=IssueType.INVALID_LLM_RESPONSE,
            actions=[
                WorkflowAction(
                    action_name="Validate LLM response",
                    handler=WorkflowHandlers.validate_llm_response
                ),
                WorkflowAction(
                    action_name="Retry LLM request",
                    handler=WorkflowHandlers.retry_llm_request,
                    retry_on_failure=True,
                    max_retries=2
                )
            ],
            success_state=PipelineState.RUNNING,
            failure_state=PipelineState.FAILED
        )

    # ========================================================================
    # STAGE-SPECIFIC WORKFLOWS
    # ========================================================================

    @staticmethod
    def build_architecture_invalid_workflow() -> Workflow:
        """Workflow for invalid architecture issues"""
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
        """Workflow for code review failure issues"""
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
        """Workflow for integration conflict issues"""
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
        """Workflow for validation failure issues"""
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

    # ========================================================================
    # MULTI-AGENT WORKFLOWS
    # ========================================================================

    @staticmethod
    def build_arbitration_deadlock_workflow() -> Workflow:
        """Workflow for arbitration deadlock issues"""
        return Workflow(
            name="Arbitration Deadlock Resolution",
            issue_type=IssueType.ARBITRATION_DEADLOCK,
            actions=[
                WorkflowAction(
                    action_name="Break arbitration deadlock",
                    handler=WorkflowHandlers.break_arbitration_deadlock
                )
            ],
            success_state=PipelineState.RUNNING,
            failure_state=PipelineState.FAILED
        )

    @staticmethod
    def build_developer_conflict_workflow() -> Workflow:
        """Workflow for developer conflict issues"""
        return Workflow(
            name="Developer Conflict Merge",
            issue_type=IssueType.DEVELOPER_CONFLICT,
            actions=[
                WorkflowAction(
                    action_name="Merge developer solutions",
                    handler=WorkflowHandlers.merge_developer_solutions
                )
            ],
            success_state=PipelineState.RUNNING,
            failure_state=PipelineState.DEGRADED
        )

    @staticmethod
    def build_messenger_error_workflow() -> Workflow:
        """Workflow for messenger error issues"""
        return Workflow(
            name="Messenger Restart",
            issue_type=IssueType.MESSENGER_ERROR,
            actions=[
                WorkflowAction(
                    action_name="Restart messenger",
                    handler=WorkflowHandlers.restart_messenger
                )
            ],
            success_state=PipelineState.RUNNING,
            failure_state=PipelineState.DEGRADED
        )

    # ========================================================================
    # DATA ISSUE WORKFLOWS
    # ========================================================================

    @staticmethod
    def build_invalid_card_workflow() -> Workflow:
        """Workflow for invalid card issues"""
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
        """Workflow for corrupted state issues"""
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
        """Workflow for RAG error issues"""
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

    # ========================================================================
    # SYSTEM ISSUE WORKFLOWS
    # ========================================================================

    @staticmethod
    def build_zombie_process_workflow() -> Workflow:
        """Workflow for zombie process issues"""
        return Workflow(
            name="Zombie Process Cleanup",
            issue_type=IssueType.ZOMBIE_PROCESS,
            actions=[
                WorkflowAction(
                    action_name="Cleanup zombie processes",
                    handler=WorkflowHandlers.cleanup_zombie_processes
                )
            ],
            success_state=PipelineState.RUNNING,
            failure_state=PipelineState.DEGRADED
        )

    @staticmethod
    def build_file_lock_workflow() -> Workflow:
        """Workflow for file lock issues"""
        return Workflow(
            name="File Lock Release",
            issue_type=IssueType.FILE_LOCK,
            actions=[
                WorkflowAction(
                    action_name="Release file locks",
                    handler=WorkflowHandlers.release_file_locks
                )
            ],
            success_state=PipelineState.RUNNING,
            failure_state=PipelineState.FAILED
        )

    @staticmethod
    def build_permission_denied_workflow() -> Workflow:
        """Workflow for permission denied issues"""
        return Workflow(
            name="Permission Fix",
            issue_type=IssueType.PERMISSION_DENIED,
            actions=[
                WorkflowAction(
                    action_name="Fix permissions",
                    handler=WorkflowHandlers.fix_permissions
                )
            ],
            success_state=PipelineState.RUNNING,
            failure_state=PipelineState.FAILED
        )
