#!/usr/bin/env python3
"""
ARTEMIS Orchestrator (Backward Compatibility Wrapper)

This file provides backward compatibility with existing code that imports
from artemis_orchestrator. All functionality has been extracted to the
orchestrator/ package for better modularity and maintainability.

REFACTORING SUMMARY:
- 1,738 lines → ~50 lines wrapper + 9 focused modules
- Monolithic file → modular package structure
- God class → focused single-responsibility classes
- Hard-coded logic → configurable, testable modules

NEW STRUCTURE:
orchestrator/
├── __init__.py                 - Package exports
├── orchestrator_core.py        - ArtemisOrchestrator class (120-404)
├── stage_creation.py           - Stage factory (405-618)
├── pipeline_execution.py       - Pipeline execution (620-839)
├── batch_processing.py         - Batch task processing (841-948)
├── stage_filtering.py          - Stage filtering & metrics (950-1010)
├── review_feedback.py          - Code review feedback (1012-1213)
├── cli_display.py              - Workflow status display (1220-1382)
├── config_validation.py        - Config validation (1287-1394)
├── entry_points.py             - CLI entry points (1397-1738)
├── workflow_planner.py         - Workflow planning (existing)
├── supervisor_integration.py   - Supervisor setup (existing)
└── helpers.py                  - Helper utilities (existing)

BACKWARD COMPATIBILITY:
This wrapper ensures existing imports continue to work:
    from artemis_orchestrator import ArtemisOrchestrator
    from artemis_orchestrator import main_hydra, main_legacy

All functionality is delegated to the orchestrator package.
"""

import sys

# Re-export ArtemisOrchestrator class
from orchestrator.orchestrator_core import ArtemisOrchestrator

# Re-export entry point functions
from orchestrator.entry_points import main_hydra, main_legacy

# Re-export CLI display functions (for backward compatibility)
from orchestrator.cli_display import display_workflow_status, list_active_workflows

# Re-export pipeline execution functions (for advanced usage)
from orchestrator.pipeline_execution import run_full_pipeline
from orchestrator.batch_processing import run_all_pending_tasks

# Re-export stage filtering functions (for advanced usage)
from orchestrator.stage_filtering import (
    filter_stages_by_plan,
    filter_stages_by_router,
    get_pipeline_metrics,
    get_pipeline_state
)

# Re-export review feedback functions (for advanced usage)
from orchestrator.review_feedback import (
    load_review_report,
    extract_code_review_feedback,
    format_issue_list,
    store_retry_feedback_in_rag
)

# Re-export config validation functions (for advanced usage)
from orchestrator.config_validation import (
    validate_config_or_exit,
    display_validation_errors,
    get_config_path
)

__all__ = [
    # Core class
    "ArtemisOrchestrator",

    # Entry points
    "main_hydra",
    "main_legacy",

    # CLI display
    "display_workflow_status",
    "list_active_workflows",

    # Pipeline execution
    "run_full_pipeline",
    "run_all_pending_tasks",

    # Stage filtering
    "filter_stages_by_plan",
    "filter_stages_by_router",
    "get_pipeline_metrics",
    "get_pipeline_state",

    # Review feedback
    "load_review_report",
    "extract_code_review_feedback",
    "format_issue_list",
    "store_retry_feedback_in_rag",

    # Config validation
    "validate_config_or_exit",
    "display_validation_errors",
    "get_config_path",
]


if __name__ == "__main__":
    """
    CLI entry point - supports both Hydra and legacy modes

    Hydra mode: python artemis_orchestrator.py card_id=xxx
    Legacy mode: python artemis_orchestrator.py --card-id xxx --full
    """
    # Use Hydra by default (check if Hydra args are present)
    if len(sys.argv) > 1 and ('=' in ' '.join(sys.argv[1:]) or '--config-name' in sys.argv):
        # Hydra mode: card_id=xxx or --config-name
        main_hydra()
    else:
        # Legacy mode: --card-id xxx --full
        main_legacy()
