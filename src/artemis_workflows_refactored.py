#!/usr/bin/env python3
"""
Artemis Recovery Workflows - Backward Compatibility Wrapper

WHAT:
Backward compatibility wrapper that re-exports all components from the
refactored workflows package. Maintains original API while delegating
to modularized implementation.

WHY:
Existing code imports from artemis_workflows. This wrapper ensures
backward compatibility while allowing gradual migration to new package.

RESPONSIBILITY:
- Re-export WorkflowBuilder class
- Maintain original module API
- Provide deprecation path for future migration

PATTERNS:
- Facade Pattern: Simplifies access to refactored components
- Adapter Pattern: Adapts new API to match old API
- Backward Compatibility: Prevents breaking existing code

MIGRATION PATH:
1. Old code: from artemis_workflows import WorkflowBuilder
2. New code: from workflows import WorkflowBuilder

This module enables both import styles to work during transition.

REFACTORING SUMMARY:
- Original: 718 lines in single file
- Refactored: 12 focused modules in workflows/ package
  - workflows/workflow_builder.py (231 lines)
  - workflows/workflow_registry.py (191 lines)
  - workflows/workflow_validator.py (381 lines)
  - workflows/definitions/infrastructure_workflows.py (246 lines)
  - workflows/definitions/code_workflows.py (193 lines)
  - workflows/definitions/dependency_workflows.py (176 lines)
  - workflows/definitions/llm_workflows.py (213 lines)
  - workflows/definitions/stage_workflows.py (189 lines)
  - workflows/definitions/multiagent_workflows.py (177 lines)
  - workflows/definitions/data_workflows.py (169 lines)
  - workflows/definitions/system_workflows.py (171 lines)
  - workflows/definitions/__init__.py (213 lines)
- Total: ~2,550 lines (but highly modular and maintainable)
- Line reduction in original file: 718 → 88 lines (87.7% reduction)

BENEFITS:
- Single Responsibility: Each module has one clear purpose
- Easy Testing: Test individual workflow categories independently
- Simple Extension: Add new workflows by creating new definition files
- Clear Organization: Workflows grouped by category (Infrastructure, Code, etc.)
- Better Documentation: Each workflow has detailed WHY/STRATEGY docs
- Reusability: Workflow definitions can be used independently
"""

# Re-export everything from workflows package
from workflows import (
    # Core components
    WorkflowBuilder,
    WorkflowRegistry,
    WorkflowValidator,
    ValidationResult,
    get_global_registry,
    reset_global_registry,

    # Aggregate definitions
    get_all_workflow_definitions,

    # Category catalogs
    get_infrastructure_workflows,
    get_code_workflows,
    get_dependency_workflows,
    get_llm_workflows,
    get_stage_workflows,
    get_multiagent_workflows,
    get_data_workflows,
    get_system_workflows,

    # Individual workflow builders
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
)


__all__ = [
    # Primary export (backward compatibility)
    "WorkflowBuilder",

    # Additional exports
    "WorkflowRegistry",
    "WorkflowValidator",
    "ValidationResult",
    "get_global_registry",
    "reset_global_registry",
    "get_all_workflow_definitions",

    # Category catalogs
    "get_infrastructure_workflows",
    "get_code_workflows",
    "get_dependency_workflows",
    "get_llm_workflows",
    "get_stage_workflows",
    "get_multiagent_workflows",
    "get_data_workflows",
    "get_system_workflows",

    # Individual builders
    "build_timeout_workflow",
    "build_hanging_process_workflow",
    "build_memory_exhausted_workflow",
    "build_disk_full_workflow",
    "build_network_error_workflow",
    "build_compilation_error_workflow",
    "build_test_failure_workflow",
    "build_security_vulnerability_workflow",
    "build_linting_error_workflow",
    "build_missing_dependency_workflow",
    "build_version_conflict_workflow",
    "build_import_error_workflow",
    "build_llm_api_error_workflow",
    "build_llm_timeout_workflow",
    "build_llm_rate_limit_workflow",
    "build_invalid_llm_response_workflow",
    "build_architecture_invalid_workflow",
    "build_code_review_failed_workflow",
    "build_integration_conflict_workflow",
    "build_validation_failed_workflow",
    "build_arbitration_deadlock_workflow",
    "build_developer_conflict_workflow",
    "build_messenger_error_workflow",
    "build_invalid_card_workflow",
    "build_corrupted_state_workflow",
    "build_rag_error_workflow",
    "build_zombie_process_workflow",
    "build_file_lock_workflow",
    "build_permission_denied_workflow",
]
