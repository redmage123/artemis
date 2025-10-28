#!/usr/bin/env python3
"""
Workflow Handler Factory

WHY:
Provides centralized handler creation with registry pattern, enabling
dynamic registration and discovery of workflow action handlers.

RESPONSIBILITY:
- Create handler instances by action name
- Register new handlers dynamically
- Maintain handler registry mapping
- Validate handler types

PATTERNS:
- Factory Pattern: Creates objects based on identifier (action_name)
- Registry Pattern: Maintains map of name to handler class
- Open/Closed Principle: Add handlers via registration without modification
- Type Safety: Validates handlers extend WorkflowHandler base class

INTEGRATION:
- Used by: Workflow execution engine for handler instantiation
- Used by: Backward compatibility wrapper (WorkflowHandlers class)
- Imports: All handler modules (infrastructure, code, dependency, etc.)
- Validates: Handler class inheritance from WorkflowHandler
"""

from typing import Dict, Type, List

from workflows.handlers.base_handler import WorkflowHandler

# Import all handler classes
from workflows.handlers.infrastructure_handlers import (
    KillHangingProcessHandler,
    IncreaseTimeoutHandler,
    FreeMemoryHandler,
    CleanupTempFilesHandler,
    CheckDiskSpaceHandler,
    RetryNetworkRequestHandler,
)
from workflows.handlers.code_handlers import (
    RunLinterFixHandler,
    RerunTestsHandler,
    FixSecurityVulnerabilityHandler,
    RetryCompilationHandler,
)
from workflows.handlers.dependency_handlers import (
    InstallMissingDependencyHandler,
    ResolveVersionConflictHandler,
    FixImportErrorHandler,
)
from workflows.handlers.llm_handlers import (
    SwitchLLMProviderHandler,
    RetryLLMRequestHandler,
    HandleRateLimitHandler,
    ValidateLLMResponseHandler,
)
from workflows.handlers.stage_handlers import (
    RegenerateArchitectureHandler,
    RequestCodeReviewRevisionHandler,
    ResolveIntegrationConflictHandler,
    RerunValidationHandler,
)
from workflows.handlers.multi_agent_handlers import (
    BreakArbitrationDeadlockHandler,
    MergeDeveloperSolutionsHandler,
    RestartMessengerHandler,
)
from workflows.handlers.data_handlers import (
    ValidateCardDataHandler,
    RestoreStateFromBackupHandler,
    RebuildRAGIndexHandler,
)
from workflows.handlers.system_handlers import (
    CleanupZombieProcessesHandler,
    ReleaseFileLocksHandler,
    FixPermissionsHandler,
)


class WorkflowHandlerFactory:
    """
    Factory for creating workflow handlers

    WHAT:
    Creates handler instances by name using registry pattern. Supports dynamic
    registration of new handlers without modifying factory code.

    WHY:
    Open/Closed Principle: Can add new handlers by registering them, without
    modifying this class. Factory provides:
    - Centralized handler creation
    - Type safety (validates handler extends WorkflowHandler)
    - Discovery (get_all_actions lists available handlers)
    - Extensibility (register custom handlers)

    PATTERNS:
    - Factory Pattern: Creates objects based on identifier (action_name)
    - Registry Pattern: Maintains map of name to handler class
    - Singleton Pattern: Factory is stateless, can be used as singleton

    INTEGRATION:
    - Used by: artemis_workflows.py WorkflowBuilder
    - Used by: WorkflowHandlers backward compatibility adapter
    - Registered handlers: 30+ action handlers

    USAGE:
        # Create handler
        handler = WorkflowHandlerFactory.create("kill_hanging_process")
        success = handler.handle({'pid': 12345})

        # Register custom handler
        class CustomHandler(WorkflowHandler):
            def handle(self, context): ...

        WorkflowHandlerFactory.register("custom_action", CustomHandler)

        # List all actions
        actions = WorkflowHandlerFactory.get_all_actions()
        # ['kill_hanging_process', 'increase_timeout', ...]
    """

    # Handler registry - maps action names to handler classes
    _handlers: Dict[str, Type[WorkflowHandler]] = {
        # Infrastructure
        "kill_hanging_process": KillHangingProcessHandler,
        "increase_timeout": IncreaseTimeoutHandler,
        "free_memory": FreeMemoryHandler,
        "cleanup_temp_files": CleanupTempFilesHandler,
        "check_disk_space": CheckDiskSpaceHandler,
        "retry_network_request": RetryNetworkRequestHandler,

        # Code
        "run_linter_fix": RunLinterFixHandler,
        "rerun_tests": RerunTestsHandler,
        "fix_security_vulnerability": FixSecurityVulnerabilityHandler,
        "retry_compilation": RetryCompilationHandler,

        # Dependencies
        "install_missing_dependency": InstallMissingDependencyHandler,
        "resolve_version_conflict": ResolveVersionConflictHandler,
        "fix_import_error": FixImportErrorHandler,

        # LLM
        "switch_llm_provider": SwitchLLMProviderHandler,
        "retry_llm_request": RetryLLMRequestHandler,
        "handle_rate_limit": HandleRateLimitHandler,
        "validate_llm_response": ValidateLLMResponseHandler,

        # Stages
        "regenerate_architecture": RegenerateArchitectureHandler,
        "request_code_review_revision": RequestCodeReviewRevisionHandler,
        "resolve_integration_conflict": ResolveIntegrationConflictHandler,
        "rerun_validation": RerunValidationHandler,

        # Multi-agent
        "break_arbitration_deadlock": BreakArbitrationDeadlockHandler,
        "merge_developer_solutions": MergeDeveloperSolutionsHandler,
        "restart_messenger": RestartMessengerHandler,

        # Data
        "validate_card_data": ValidateCardDataHandler,
        "restore_state_from_backup": RestoreStateFromBackupHandler,
        "rebuild_rag_index": RebuildRAGIndexHandler,

        # System
        "cleanup_zombie_processes": CleanupZombieProcessesHandler,
        "release_file_locks": ReleaseFileLocksHandler,
        "fix_permissions": FixPermissionsHandler,
    }

    @classmethod
    def create(cls, action_name: str) -> WorkflowHandler:
        """
        Create a workflow handler by action name

        Args:
            action_name: Name of the workflow action

        Returns:
            WorkflowHandler instance

        Raises:
            ValueError: If action name is unknown
        """
        handler_class = cls._handlers.get(action_name)

        if not handler_class:
            raise ValueError(
                f"Unknown workflow action: {action_name}. "
                f"Available: {', '.join(cls._handlers.keys())}"
            )

        return handler_class()

    @classmethod
    def register(cls, action_name: str, handler_class: Type[WorkflowHandler]) -> None:
        """
        Register a new handler class

        Allows extending handlers without modifying this file
        (Open/Closed Principle)

        Args:
            action_name: Name of the action
            handler_class: Handler class (must extend WorkflowHandler)

        Raises:
            ValueError: If handler_class does not extend WorkflowHandler
        """
        if not issubclass(handler_class, WorkflowHandler):
            raise ValueError(f"{handler_class} must extend WorkflowHandler")

        cls._handlers[action_name] = handler_class

    @classmethod
    def get_all_actions(cls) -> List[str]:
        """
        Get list of all registered action names

        Returns:
            List of registered action name strings
        """
        return list(cls._handlers.keys())
