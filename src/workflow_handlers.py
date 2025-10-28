#!/usr/bin/env python3
"""
Workflow Action Handlers - Backward Compatibility Wrapper

WHAT:
Backward compatibility wrapper that maintains the original static method API
while delegating to the new modular handler architecture.

WHY:
Enables gradual migration without breaking existing code. External code can
continue using WorkflowHandlers static methods while internally leveraging
the new modular, testable, and maintainable handler structure.

RESPONSIBILITY:
- Maintain original API surface (static methods)
- Delegate to modular handler implementations
- Re-export all handler classes and factory
- Ensure zero breaking changes

PATTERNS:
- Facade Pattern: Simple interface over complex modular system
- Adapter Pattern: Adapts old API to new implementation
- Delegation Pattern: Forwards calls to appropriate handlers
- Lazy Loading: Imports delayed to avoid circular dependencies

MIGRATION PATH:
Old usage (still works):
    WorkflowHandlers.kill_hanging_process({'pid': 12345})

New usage (preferred):
    handler = WorkflowHandlerFactory.create("kill_hanging_process")
    handler.handle({'pid': 12345})

INTEGRATION:
- Imports from: workflows.handlers.handler_factory (lazy)
- Used by: Legacy code and workflow execution engine
- Re-exports: All handler classes for backward compatibility

MODULARIZATION:
Original file: 944 lines
New structure:
- base_handler.py: 83 lines (base interface)
- infrastructure_handlers.py: 206 lines (6 handlers)
- code_handlers.py: 146 lines (4 handlers)
- dependency_handlers.py: 117 lines (3 handlers)
- llm_handlers.py: 118 lines (4 handlers)
- stage_handlers.py: 86 lines (4 handlers)
- multi_agent_handlers.py: 84 lines (3 handlers)
- data_handlers.py: 86 lines (3 handlers)
- system_handlers.py: 103 lines (3 handlers)
- handler_factory.py: 224 lines (factory + registry)
- workflow_handlers.py: 304 lines (this wrapper)
Total: 1,695 lines (distributed across 11 focused modules)
Line count increase: +751 lines (+80%) for documentation and separation
Per-module average: 154 lines (84% reduction in module size)
"""

from typing import Dict, Any


def _get_factory():
    """Lazy import to avoid circular dependency"""
    from workflows.handlers.handler_factory import WorkflowHandlerFactory
    return WorkflowHandlerFactory


class WorkflowHandlers:
    """
    Backward compatibility adapter for old WorkflowHandlers class

    WHAT:
    Maintains the static method API while delegating to new handler classes.
    Allows gradual migration without breaking existing code.

    WHY:
    Enables refactoring without disrupting consumers. Code using the old API
    continues to work while internally leveraging the improved architecture.

    PATTERNS:
    - Facade Pattern: Simplified interface over modular system
    - Adapter Pattern: Old API to new implementation
    - Lazy Loading: Factory imported on-demand to avoid circular imports
    """

    @staticmethod
    def kill_hanging_process(context: Dict[str, Any]) -> bool:
        return _get_factory().create("kill_hanging_process").handle(context)

    @staticmethod
    def increase_timeout(context: Dict[str, Any]) -> bool:
        return _get_factory().create("increase_timeout").handle(context)

    @staticmethod
    def free_memory(context: Dict[str, Any]) -> bool:
        return _get_factory().create("free_memory").handle(context)

    @staticmethod
    def cleanup_temp_files(context: Dict[str, Any]) -> bool:
        return _get_factory().create("cleanup_temp_files").handle(context)

    @staticmethod
    def check_disk_space(context: Dict[str, Any]) -> bool:
        return _get_factory().create("check_disk_space").handle(context)

    @staticmethod
    def retry_network_request(context: Dict[str, Any]) -> bool:
        return _get_factory().create("retry_network_request").handle(context)

    @staticmethod
    def run_linter_fix(context: Dict[str, Any]) -> bool:
        return _get_factory().create("run_linter_fix").handle(context)

    @staticmethod
    def rerun_tests(context: Dict[str, Any]) -> bool:
        return _get_factory().create("rerun_tests").handle(context)

    @staticmethod
    def fix_security_vulnerability(context: Dict[str, Any]) -> bool:
        return _get_factory().create("fix_security_vulnerability").handle(context)

    @staticmethod
    def retry_compilation(context: Dict[str, Any]) -> bool:
        return _get_factory().create("retry_compilation").handle(context)

    @staticmethod
    def install_missing_dependency(context: Dict[str, Any]) -> bool:
        return _get_factory().create("install_missing_dependency").handle(context)

    @staticmethod
    def resolve_version_conflict(context: Dict[str, Any]) -> bool:
        return _get_factory().create("resolve_version_conflict").handle(context)

    @staticmethod
    def fix_import_error(context: Dict[str, Any]) -> bool:
        return _get_factory().create("fix_import_error").handle(context)

    @staticmethod
    def switch_llm_provider(context: Dict[str, Any]) -> bool:
        return _get_factory().create("switch_llm_provider").handle(context)

    @staticmethod
    def retry_llm_request(context: Dict[str, Any]) -> bool:
        return _get_factory().create("retry_llm_request").handle(context)

    @staticmethod
    def handle_rate_limit(context: Dict[str, Any]) -> bool:
        return _get_factory().create("handle_rate_limit").handle(context)

    @staticmethod
    def validate_llm_response(context: Dict[str, Any]) -> bool:
        return _get_factory().create("validate_llm_response").handle(context)

    @staticmethod
    def regenerate_architecture(context: Dict[str, Any]) -> bool:
        return _get_factory().create("regenerate_architecture").handle(context)

    @staticmethod
    def request_code_review_revision(context: Dict[str, Any]) -> bool:
        return _get_factory().create("request_code_review_revision").handle(context)

    @staticmethod
    def resolve_integration_conflict(context: Dict[str, Any]) -> bool:
        return _get_factory().create("resolve_integration_conflict").handle(context)

    @staticmethod
    def rerun_validation(context: Dict[str, Any]) -> bool:
        return _get_factory().create("rerun_validation").handle(context)

    @staticmethod
    def break_arbitration_deadlock(context: Dict[str, Any]) -> bool:
        return _get_factory().create("break_arbitration_deadlock").handle(context)

    @staticmethod
    def merge_developer_solutions(context: Dict[str, Any]) -> bool:
        return _get_factory().create("merge_developer_solutions").handle(context)

    @staticmethod
    def restart_messenger(context: Dict[str, Any]) -> bool:
        return _get_factory().create("restart_messenger").handle(context)

    @staticmethod
    def validate_card_data(context: Dict[str, Any]) -> bool:
        return _get_factory().create("validate_card_data").handle(context)

    @staticmethod
    def restore_state_from_backup(context: Dict[str, Any]) -> bool:
        return _get_factory().create("restore_state_from_backup").handle(context)

    @staticmethod
    def rebuild_rag_index(context: Dict[str, Any]) -> bool:
        return _get_factory().create("rebuild_rag_index").handle(context)

    @staticmethod
    def cleanup_zombie_processes(context: Dict[str, Any]) -> bool:
        return _get_factory().create("cleanup_zombie_processes").handle(context)

    @staticmethod
    def release_file_locks(context: Dict[str, Any]) -> bool:
        return _get_factory().create("release_file_locks").handle(context)

    @staticmethod
    def fix_permissions(context: Dict[str, Any]) -> bool:
        return _get_factory().create("fix_permissions").handle(context)


# Lazy exports to avoid circular imports
def __getattr__(name):
    """
    Lazy attribute access for re-exported classes

    Allows:
        from workflow_handlers import WorkflowHandlerFactory
        from workflow_handlers import KillHangingProcessHandler

    Without circular import issues.
    """
    if name == 'WorkflowHandlerFactory':
        from workflows.handlers.handler_factory import WorkflowHandlerFactory
        return WorkflowHandlerFactory

    if name == 'WorkflowHandler':
        from workflows.handlers.base_handler import WorkflowHandler
        return WorkflowHandler

    # Infrastructure handlers
    if name == 'KillHangingProcessHandler':
        from workflows.handlers.infrastructure_handlers import KillHangingProcessHandler
        return KillHangingProcessHandler
    if name == 'IncreaseTimeoutHandler':
        from workflows.handlers.infrastructure_handlers import IncreaseTimeoutHandler
        return IncreaseTimeoutHandler
    if name == 'FreeMemoryHandler':
        from workflows.handlers.infrastructure_handlers import FreeMemoryHandler
        return FreeMemoryHandler
    if name == 'CleanupTempFilesHandler':
        from workflows.handlers.infrastructure_handlers import CleanupTempFilesHandler
        return CleanupTempFilesHandler
    if name == 'CheckDiskSpaceHandler':
        from workflows.handlers.infrastructure_handlers import CheckDiskSpaceHandler
        return CheckDiskSpaceHandler
    if name == 'RetryNetworkRequestHandler':
        from workflows.handlers.infrastructure_handlers import RetryNetworkRequestHandler
        return RetryNetworkRequestHandler

    # Code handlers
    if name == 'RunLinterFixHandler':
        from workflows.handlers.code_handlers import RunLinterFixHandler
        return RunLinterFixHandler
    if name == 'RerunTestsHandler':
        from workflows.handlers.code_handlers import RerunTestsHandler
        return RerunTestsHandler
    if name == 'FixSecurityVulnerabilityHandler':
        from workflows.handlers.code_handlers import FixSecurityVulnerabilityHandler
        return FixSecurityVulnerabilityHandler
    if name == 'RetryCompilationHandler':
        from workflows.handlers.code_handlers import RetryCompilationHandler
        return RetryCompilationHandler

    # Dependency handlers
    if name == 'InstallMissingDependencyHandler':
        from workflows.handlers.dependency_handlers import InstallMissingDependencyHandler
        return InstallMissingDependencyHandler
    if name == 'ResolveVersionConflictHandler':
        from workflows.handlers.dependency_handlers import ResolveVersionConflictHandler
        return ResolveVersionConflictHandler
    if name == 'FixImportErrorHandler':
        from workflows.handlers.dependency_handlers import FixImportErrorHandler
        return FixImportErrorHandler

    # LLM handlers
    if name == 'SwitchLLMProviderHandler':
        from workflows.handlers.llm_handlers import SwitchLLMProviderHandler
        return SwitchLLMProviderHandler
    if name == 'RetryLLMRequestHandler':
        from workflows.handlers.llm_handlers import RetryLLMRequestHandler
        return RetryLLMRequestHandler
    if name == 'HandleRateLimitHandler':
        from workflows.handlers.llm_handlers import HandleRateLimitHandler
        return HandleRateLimitHandler
    if name == 'ValidateLLMResponseHandler':
        from workflows.handlers.llm_handlers import ValidateLLMResponseHandler
        return ValidateLLMResponseHandler

    # Stage handlers
    if name == 'RegenerateArchitectureHandler':
        from workflows.handlers.stage_handlers import RegenerateArchitectureHandler
        return RegenerateArchitectureHandler
    if name == 'RequestCodeReviewRevisionHandler':
        from workflows.handlers.stage_handlers import RequestCodeReviewRevisionHandler
        return RequestCodeReviewRevisionHandler
    if name == 'ResolveIntegrationConflictHandler':
        from workflows.handlers.stage_handlers import ResolveIntegrationConflictHandler
        return ResolveIntegrationConflictHandler
    if name == 'RerunValidationHandler':
        from workflows.handlers.stage_handlers import RerunValidationHandler
        return RerunValidationHandler

    # Multi-agent handlers
    if name == 'BreakArbitrationDeadlockHandler':
        from workflows.handlers.multi_agent_handlers import BreakArbitrationDeadlockHandler
        return BreakArbitrationDeadlockHandler
    if name == 'MergeDeveloperSolutionsHandler':
        from workflows.handlers.multi_agent_handlers import MergeDeveloperSolutionsHandler
        return MergeDeveloperSolutionsHandler
    if name == 'RestartMessengerHandler':
        from workflows.handlers.multi_agent_handlers import RestartMessengerHandler
        return RestartMessengerHandler

    # Data handlers
    if name == 'ValidateCardDataHandler':
        from workflows.handlers.data_handlers import ValidateCardDataHandler
        return ValidateCardDataHandler
    if name == 'RestoreStateFromBackupHandler':
        from workflows.handlers.data_handlers import RestoreStateFromBackupHandler
        return RestoreStateFromBackupHandler
    if name == 'RebuildRAGIndexHandler':
        from workflows.handlers.data_handlers import RebuildRAGIndexHandler
        return RebuildRAGIndexHandler

    # System handlers
    if name == 'CleanupZombieProcessesHandler':
        from workflows.handlers.system_handlers import CleanupZombieProcessesHandler
        return CleanupZombieProcessesHandler
    if name == 'ReleaseFileLocksHandler':
        from workflows.handlers.system_handlers import ReleaseFileLocksHandler
        return ReleaseFileLocksHandler
    if name == 'FixPermissionsHandler':
        from workflows.handlers.system_handlers import FixPermissionsHandler
        return FixPermissionsHandler

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = [
    # Backward compatibility adapter
    'WorkflowHandlers',
    # Factory (lazy)
    'WorkflowHandlerFactory',
    # Base handler (lazy)
    'WorkflowHandler',
    # Infrastructure handlers (lazy)
    'KillHangingProcessHandler',
    'IncreaseTimeoutHandler',
    'FreeMemoryHandler',
    'CleanupTempFilesHandler',
    'CheckDiskSpaceHandler',
    'RetryNetworkRequestHandler',
    # Code handlers (lazy)
    'RunLinterFixHandler',
    'RerunTestsHandler',
    'FixSecurityVulnerabilityHandler',
    'RetryCompilationHandler',
    # Dependency handlers (lazy)
    'InstallMissingDependencyHandler',
    'ResolveVersionConflictHandler',
    'FixImportErrorHandler',
    # LLM handlers (lazy)
    'SwitchLLMProviderHandler',
    'RetryLLMRequestHandler',
    'HandleRateLimitHandler',
    'ValidateLLMResponseHandler',
    # Stage handlers (lazy)
    'RegenerateArchitectureHandler',
    'RequestCodeReviewRevisionHandler',
    'ResolveIntegrationConflictHandler',
    'RerunValidationHandler',
    # Multi-agent handlers (lazy)
    'BreakArbitrationDeadlockHandler',
    'MergeDeveloperSolutionsHandler',
    'RestartMessengerHandler',
    # Data handlers (lazy)
    'ValidateCardDataHandler',
    'RestoreStateFromBackupHandler',
    'RebuildRAGIndexHandler',
    # System handlers (lazy)
    'CleanupZombieProcessesHandler',
    'ReleaseFileLocksHandler',
    'FixPermissionsHandler',
]
