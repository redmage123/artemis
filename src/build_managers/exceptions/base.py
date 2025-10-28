#!/usr/bin/env python3
"""
Base Build System Exception

WHY: Provides foundation for all build system error handling with rich context
     preservation and integration with Artemis pipeline error handling.

RESPONSIBILITY: Define base exception class that all build system exceptions
                inherit from, providing consistent error handling and context
                management across all build operations.

PATTERNS:
- Template Method Pattern: Provides base __str__ method that subclasses can extend
- Context Preservation Pattern: Stores rich diagnostic information with every error
- Exception Chaining Pattern: Maintains original exception for debugging

Design Philosophy:
- All build system errors inherit from PipelineStageError for pipeline integration
- Rich context preserved with every exception (build system, command, environment)
- Original exceptions wrapped to maintain full error chain for debugging
- Functional approach: immutable context dictionaries, pure error formatting
"""

from typing import Dict, Any, Optional
from artemis_exceptions import PipelineStageError


class BuildSystemError(PipelineStageError):
    """
    Base exception for all build system errors.

    WHY: Single base class enables uniform error handling, context preservation,
         and integration with Artemis pipeline error recovery mechanisms.

    RESPONSIBILITY: Provide base error class with context preservation and
                   enhanced string formatting for all build system operations.

    PATTERNS:
    - Template Method: Defines error formatting that subclasses inherit
    - Context Preservation: Stores diagnostic context for debugging
    - Exception Chaining: Wraps original exceptions without losing information

    Example:
        >>> raise BuildSystemError(
        ...     "Maven build failed",
        ...     context={'build_system': 'maven', 'phase': 'compile'},
        ...     original_exception=CompilationError("Cannot find symbol")
        ... )

    Attributes:
        message: Human-readable error description
        context: Diagnostic context dictionary (build system, command, etc.)
        original_exception: Original wrapped exception if available
    """

    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ) -> None:
        """
        Initialize build system error with context.

        WHY: Rich context enables better debugging, error reporting, and
             automated error recovery in the Artemis pipeline.

        Args:
            message: Human-readable error message describing what went wrong
            context: Additional diagnostic context (build system, command, exit_code, etc.)
            original_exception: Original exception if this error wraps another exception

        Example:
            >>> error = BuildSystemError(
            ...     "Maven not found",
            ...     context={'build_system': 'maven', 'path': '/usr/bin/mvn'},
            ...     original_exception=FileNotFoundError()
            ... )
        """
        # Use immutable context (functional programming)
        super().__init__(message, context or {})
        self.original_exception = original_exception

    def __str__(self) -> str:
        """
        Enhanced string representation with context and exception chain.

        WHY: Provides complete error information for logging and debugging
             without losing original exception details.

        PERFORMANCE: O(1) string formatting, context is pre-stored dictionary.

        Returns:
            Complete error message with context and original exception chain

        Example:
            >>> error = BuildSystemError(
            ...     "Build failed",
            ...     context={'phase': 'compile'},
            ...     original_exception=RuntimeError("Missing dependency")
            ... )
            >>> print(error)
            Build failed
            Context: {'phase': 'compile'}
            Caused by: RuntimeError: Missing dependency
        """
        base_message = super().__str__()

        # Guard clause: Early return if no original exception (avoid nesting)
        if not self.original_exception:
            return base_message

        # Functional approach: Build new string without mutation
        exception_type = type(self.original_exception).__name__
        exception_message = str(self.original_exception)
        return f"{base_message}\nCaused by: {exception_type}: {exception_message}"

    def get_context_value(self, key: str, default: Any = None) -> Any:
        """
        Safely retrieve context value.

        WHY: Provides functional accessor for context without exposing
             mutable dictionary directly.

        Args:
            key: Context key to retrieve
            default: Default value if key not found

        Returns:
            Context value or default

        Example:
            >>> error = BuildSystemError("Failed", context={'system': 'maven'})
            >>> error.get_context_value('system')
            'maven'
            >>> error.get_context_value('missing', 'default')
            'default'
        """
        return self.context.get(key, default)


class UnsupportedBuildSystemError(BuildSystemError):
    """
    Build system not supported or not implemented.

    WHY: Distinguishes "not yet implemented" from other failures, enabling
         better error messages and potential fallback strategies.

    RESPONSIBILITY: Signal that requested build system is not supported
                   on current platform or not yet implemented.

    Example:
        >>> raise UnsupportedBuildSystemError(
        ...     "Bazel build system not yet supported",
        ...     context={
        ...         'requested_system': 'bazel',
        ...         'supported_systems': ['maven', 'gradle', 'npm', 'cargo'],
        ...         'platform': 'linux'
        ...     }
        ... )
    """
    pass


# Module-level constants for error context keys (DRY principle)
CONTEXT_BUILD_SYSTEM = "build_system"
CONTEXT_COMMAND = "command"
CONTEXT_EXIT_CODE = "exit_code"
CONTEXT_WORKING_DIR = "working_dir"
CONTEXT_TIMEOUT = "timeout"
CONTEXT_PHASE = "phase"
