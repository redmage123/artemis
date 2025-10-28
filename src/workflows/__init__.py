"""
Workflows Package - Recovery Workflow Management

WHAT:
Complete workflow management system for pipeline recovery including workflow
definitions, builder, registry, and validation.

WHY:
Centralizes all workflow-related functionality in dedicated package, enabling
easy maintenance, testing, and extension of recovery workflows.

RESPONSIBILITY:
- Export workflow builder for backward compatibility
- Export workflow registry for workflow lookup
- Export workflow validator for validation
- Export workflow definitions for direct access

PATTERNS:
- Package Organization: Logical grouping of workflow components
- Facade Pattern: Simplified API through package __init__
- Backward Compatibility: Re-export WorkflowBuilder for existing code

INTEGRATION:
- Used by: SupervisorAgent, RecoveryEngine
- Exports: WorkflowBuilder, WorkflowRegistry, WorkflowValidator
- Structure: workflows/definitions/, workflows/workflow_*.py

PACKAGE STRUCTURE:
workflows/
├── __init__.py (this file)
├── workflow_builder.py (factory for workflows)
├── workflow_registry.py (central catalog)
├── workflow_validator.py (validation)
├── handlers/ (workflow handlers - existing)
├── strategies/ (pipeline execution strategies - NEW)
│   ├── base_strategy.py
│   ├── execution_context.py
│   ├── standard_strategy.py
│   ├── fast_strategy.py
│   ├── parallel_strategy.py
│   ├── checkpoint_strategy.py
│   └── strategy_factory.py
└── definitions/ (workflow definitions by category)
    ├── infrastructure_workflows.py
    ├── code_workflows.py
    ├── dependency_workflows.py
    ├── llm_workflows.py
    ├── stage_workflows.py
    ├── multiagent_workflows.py
    ├── data_workflows.py
    └── system_workflows.py
"""

# Core workflow components
from workflows.workflow_builder import WorkflowBuilder
from workflows.workflow_registry import (
    WorkflowRegistry,
    get_global_registry,
    reset_global_registry
)
from workflows.workflow_validator import (
    WorkflowValidator,
    ValidationResult
)

# Workflow definitions (for direct access if needed)
from workflows.definitions import (
    get_all_workflow_definitions,
    # Infrastructure
    get_infrastructure_workflows,
    build_timeout_workflow,
    build_hanging_process_workflow,
    build_memory_exhausted_workflow,
    build_disk_full_workflow,
    build_network_error_workflow,
    # Code
    get_code_workflows,
    build_compilation_error_workflow,
    build_test_failure_workflow,
    build_security_vulnerability_workflow,
    build_linting_error_workflow,
    # Dependencies
    get_dependency_workflows,
    build_missing_dependency_workflow,
    build_version_conflict_workflow,
    build_import_error_workflow,
    # LLM
    get_llm_workflows,
    build_llm_api_error_workflow,
    build_llm_timeout_workflow,
    build_llm_rate_limit_workflow,
    build_invalid_llm_response_workflow,
    # Stage
    get_stage_workflows,
    build_architecture_invalid_workflow,
    build_code_review_failed_workflow,
    build_integration_conflict_workflow,
    build_validation_failed_workflow,
    # Multi-agent
    get_multiagent_workflows,
    build_arbitration_deadlock_workflow,
    build_developer_conflict_workflow,
    build_messenger_error_workflow,
    # Data
    get_data_workflows,
    build_invalid_card_workflow,
    build_corrupted_state_workflow,
    build_rag_error_workflow,
    # System
    get_system_workflows,
    build_zombie_process_workflow,
    build_file_lock_workflow,
    build_permission_denied_workflow,
)


__all__ = [
    # Core components
    "WorkflowBuilder",
    "WorkflowRegistry",
    "WorkflowValidator",
    "ValidationResult",
    "get_global_registry",
    "reset_global_registry",

    # Aggregate definitions
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

    # Individual workflow builders (for backward compatibility)
    # Infrastructure
    "build_timeout_workflow",
    "build_hanging_process_workflow",
    "build_memory_exhausted_workflow",
    "build_disk_full_workflow",
    "build_network_error_workflow",
    # Code
    "build_compilation_error_workflow",
    "build_test_failure_workflow",
    "build_security_vulnerability_workflow",
    "build_linting_error_workflow",
    # Dependencies
    "build_missing_dependency_workflow",
    "build_version_conflict_workflow",
    "build_import_error_workflow",
    # LLM
    "build_llm_api_error_workflow",
    "build_llm_timeout_workflow",
    "build_llm_rate_limit_workflow",
    "build_invalid_llm_response_workflow",
    # Stage
    "build_architecture_invalid_workflow",
    "build_code_review_failed_workflow",
    "build_integration_conflict_workflow",
    "build_validation_failed_workflow",
    # Multi-agent
    "build_arbitration_deadlock_workflow",
    "build_developer_conflict_workflow",
    "build_messenger_error_workflow",
    # Data
    "build_invalid_card_workflow",
    "build_corrupted_state_workflow",
    "build_rag_error_workflow",
    # System
    "build_zombie_process_workflow",
    "build_file_lock_workflow",
    "build_permission_denied_workflow",
]
