"""
Workflow Handlers Subpackage

WHY:
Provides modular, testable, and maintainable workflow action handlers
organized by responsibility (infrastructure, code, dependencies, etc.).

RESPONSIBILITY:
- Export all handler classes for external use
- Export factory for handler creation
- Maintain clean module organization
- Support both new and legacy import patterns

PATTERNS:
- Factory Pattern: WorkflowHandlerFactory for handler creation
- Strategy Pattern: Each handler implements different recovery strategy
- Single Responsibility: Each module focuses on one domain

INTEGRATION:
Part of: workflows package
Exports: All handler classes and factory
Used by: Workflow execution engine, backward compatibility wrapper

MODULES:
- base_handler: Abstract WorkflowHandler base class
- infrastructure_handlers: System resource management (6 handlers)
- code_handlers: Code quality operations (4 handlers)
- dependency_handlers: Package management (3 handlers)
- llm_handlers: LLM API operations (4 handlers)
- stage_handlers: Pipeline stage operations (4 handlers)
- multi_agent_handlers: Agent coordination (3 handlers)
- data_handlers: Data validation and storage (3 handlers)
- system_handlers: System-level operations (3 handlers)
- handler_factory: Handler creation and registration
"""

from workflows.handlers.base_handler import WorkflowHandler

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

from workflows.handlers.handler_factory import WorkflowHandlerFactory

__all__ = [
    # Factory
    'WorkflowHandlerFactory',
    # Base handler
    'WorkflowHandler',
    # Infrastructure handlers
    'KillHangingProcessHandler',
    'IncreaseTimeoutHandler',
    'FreeMemoryHandler',
    'CleanupTempFilesHandler',
    'CheckDiskSpaceHandler',
    'RetryNetworkRequestHandler',
    # Code handlers
    'RunLinterFixHandler',
    'RerunTestsHandler',
    'FixSecurityVulnerabilityHandler',
    'RetryCompilationHandler',
    # Dependency handlers
    'InstallMissingDependencyHandler',
    'ResolveVersionConflictHandler',
    'FixImportErrorHandler',
    # LLM handlers
    'SwitchLLMProviderHandler',
    'RetryLLMRequestHandler',
    'HandleRateLimitHandler',
    'ValidateLLMResponseHandler',
    # Stage handlers
    'RegenerateArchitectureHandler',
    'RequestCodeReviewRevisionHandler',
    'ResolveIntegrationConflictHandler',
    'RerunValidationHandler',
    # Multi-agent handlers
    'BreakArbitrationDeadlockHandler',
    'MergeDeveloperSolutionsHandler',
    'RestartMessengerHandler',
    # Data handlers
    'ValidateCardDataHandler',
    'RestoreStateFromBackupHandler',
    'RebuildRAGIndexHandler',
    # System handlers
    'CleanupZombieProcessesHandler',
    'ReleaseFileLocksHandler',
    'FixPermissionsHandler',
]
