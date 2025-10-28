"""
Artemis Orchestrator Package - Modularized pipeline orchestration

WHY: Separate orchestration concerns into focused, testable modules.
RESPONSIBILITY: Provide clean API for pipeline orchestration.
PATTERNS: Facade Pattern (package interface), Dependency Injection.

This package contains:
- orchestrator_core.py: ArtemisOrchestrator class initialization
- stage_creation.py: Stage factory and configuration
- pipeline_execution.py: Main pipeline execution logic
- batch_processing.py: Batch task processing
- stage_filtering.py: Stage filtering and metrics
- review_feedback.py: Code review feedback handling
- cli_display.py: CLI status display utilities
- config_validation.py: Configuration validation
- entry_points.py: CLI entry points (main_hydra, main_legacy)
- workflow_planner.py: Task analysis and workflow plan generation
- supervisor_integration.py: Supervisor registration and recovery strategies
- helpers.py: Platform, notification, retrospective, code review helpers

REFACTORING: Extracted from artemis_orchestrator.py (1,738 lines → modular package)
"""

# Core orchestrator class
from orchestrator.orchestrator_core import ArtemisOrchestrator

# Stage creation
from orchestrator.stage_creation import create_default_stages

# Pipeline execution
from orchestrator.pipeline_execution import run_full_pipeline
from orchestrator.batch_processing import run_all_pending_tasks

# Stage filtering and metrics
from orchestrator.stage_filtering import (
    filter_stages_by_plan,
    filter_stages_by_router,
    get_pipeline_metrics,
    get_pipeline_state
)

# Review feedback
from orchestrator.review_feedback import (
    load_review_report,
    extract_code_review_feedback,
    format_issue_list,
    store_retry_feedback_in_rag
)

# CLI display
from orchestrator.cli_display import (
    display_workflow_status,
    list_active_workflows
)

# Config validation
from orchestrator.config_validation import (
    validate_config_or_exit,
    display_validation_errors,
    get_config_path
)

# Entry points
from orchestrator.entry_points import (
    main_hydra,
    main_legacy
)

# Workflow planning (existing)
from orchestrator.workflow_planner import WorkflowPlanner

# Supervisor integration (existing)
from orchestrator.supervisor_integration import register_stages_with_supervisor

# Helper utilities (existing)
from orchestrator.helpers import (
    store_and_validate_platform_info,
    notify_pipeline_start,
    notify_pipeline_completion,
    notify_pipeline_failure,
    collect_sprint_metrics,
    run_retrospective,
    load_review_report as helpers_load_review_report,
    extract_code_review_feedback as helpers_extract_code_review_feedback
)

__all__ = [
    # Core class
    "ArtemisOrchestrator",

    # Stage creation
    "create_default_stages",

    # Pipeline execution
    "run_full_pipeline",
    "run_all_pending_tasks",

    # Stage filtering and metrics
    "filter_stages_by_plan",
    "filter_stages_by_router",
    "get_pipeline_metrics",
    "get_pipeline_state",

    # Review feedback
    "load_review_report",
    "extract_code_review_feedback",
    "format_issue_list",
    "store_retry_feedback_in_rag",

    # CLI display
    "display_workflow_status",
    "list_active_workflows",

    # Config validation
    "validate_config_or_exit",
    "display_validation_errors",
    "get_config_path",

    # Entry points
    "main_hydra",
    "main_legacy",

    # Workflow planning
    "WorkflowPlanner",

    # Supervisor integration
    "register_stages_with_supervisor",

    # Helper utilities
    "store_and_validate_platform_info",
    "notify_pipeline_start",
    "notify_pipeline_completion",
    "notify_pipeline_failure",
    "collect_sprint_metrics",
    "run_retrospective",
]
