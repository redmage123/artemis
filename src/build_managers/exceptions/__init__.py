#!/usr/bin/env python3
"""
Build System Exception Package

WHY: Centralizes all build system exception handling with modular organization,
     enabling targeted error handling and recovery strategies per error category.

RESPONSIBILITY: Export all build system exception classes and utilities,
                providing a unified interface for importing exceptions.

PATTERNS:
- Facade Pattern: Provides unified interface to exception subsystem
- Module Organization: Groups related exceptions by category
- Backward Compatibility: Maintains same public API as original module

Design Philosophy:
- Modular organization: Exceptions grouped by category (validation, execution, dependencies)
- Single import point: All exceptions accessible from this package
- Rich context: Every exception carries diagnostic information
- Functional design: Immutable contexts, pure utility functions

Module Structure:
- base.py: Base exception classes and core functionality
- validation.py: Validation and configuration exceptions
- execution.py: Build and test execution exceptions
- dependencies.py: Dependency management exceptions
- utilities.py: Exception creation helpers and formatters

Exception Hierarchy:
    BuildSystemError (base)
    ├── BuildSystemNotFoundError (validation)
    ├── ProjectConfigurationError (validation)
    ├── UnsupportedBuildSystemError (base)
    ├── BuildExecutionError (execution)
    ├── TestExecutionError (execution)
    ├── BuildTimeoutError (execution)
    ├── DependencyInstallError (dependencies)
    └── DependencyResolutionError (dependencies)

Example Usage:
    >>> from build_managers.exceptions import (
    ...     BuildSystemError,
    ...     BuildSystemNotFoundError,
    ...     build_error
    ... )
    >>> raise BuildSystemNotFoundError(
    ...     "Maven not found",
    ...     context={'build_system': 'maven'}
    ... )
"""

# Base exceptions
from build_managers.exceptions.base import (
    BuildSystemError,
    UnsupportedBuildSystemError,
    CONTEXT_BUILD_SYSTEM,
    CONTEXT_COMMAND,
    CONTEXT_EXIT_CODE,
    CONTEXT_WORKING_DIR,
    CONTEXT_TIMEOUT,
    CONTEXT_PHASE,
)

# Validation exceptions
from build_managers.exceptions.validation import (
    BuildSystemNotFoundError,
    ProjectConfigurationError,
    CONTEXT_EXPECTED_PATH,
    CONTEXT_SEARCHED_PATHS,
    CONTEXT_INSTALL_COMMAND,
    CONTEXT_CONFIG_FILE,
    CONTEXT_PROJECT_DIR,
    CONTEXT_MISSING_FIELDS,
    CONTEXT_INVALID_FIELDS,
    CONTEXT_PARSE_ERROR,
)

# Execution exceptions
from build_managers.exceptions.execution import (
    BuildExecutionError,
    TestExecutionError,
    BuildTimeoutError,
    CONTEXT_ERRORS,
    CONTEXT_WARNINGS,
    CONTEXT_STDOUT,
    CONTEXT_STDERR,
    CONTEXT_TESTS_RUN,
    CONTEXT_TESTS_PASSED,
    CONTEXT_TESTS_FAILED,
    CONTEXT_TESTS_SKIPPED,
    CONTEXT_FAILED_TESTS,
    CONTEXT_OPERATION,
    CONTEXT_ELAPSED,
    CONTEXT_SUGGESTION,
)

# Dependency exceptions
from build_managers.exceptions.dependencies import (
    DependencyInstallError,
    DependencyResolutionError,
    CONTEXT_PACKAGE,
    CONTEXT_VERSION,
    CONTEXT_REASON,
    CONTEXT_REGISTRY,
    CONTEXT_SUGGESTED_VERSIONS,
    CONTEXT_RETRYABLE,
    CONTEXT_NETWORK_ERROR,
    CONTEXT_CONFLICTING_VERSIONS,
    CONTEXT_REQUIRED_BY,
    CONTEXT_RESOLUTION_STRATEGY,
    CONTEXT_SUGGESTED_RESOLUTION,
    CONTEXT_DEPENDENCY_TREE,
    REASON_NOT_FOUND,
    REASON_NETWORK,
    REASON_PERMISSION,
    REASON_VERSION_CONFLICT,
    REASON_CHECKSUM_FAILED,
    REASON_REGISTRY_UNAVAILABLE,
)

# Utilities
from build_managers.exceptions.utilities import (
    build_error,
    create_not_found_error,
    create_config_error,
    create_build_execution_error,
    format_error_summary,
)

# Public API - defines what's exported with "from build_managers.exceptions import *"
__all__ = [
    # Base exceptions
    'BuildSystemError',
    'UnsupportedBuildSystemError',

    # Validation exceptions
    'BuildSystemNotFoundError',
    'ProjectConfigurationError',

    # Execution exceptions
    'BuildExecutionError',
    'TestExecutionError',
    'BuildTimeoutError',

    # Dependency exceptions
    'DependencyInstallError',
    'DependencyResolutionError',

    # Utility functions
    'build_error',
    'create_not_found_error',
    'create_config_error',
    'create_build_execution_error',
    'format_error_summary',

    # Context key constants (base)
    'CONTEXT_BUILD_SYSTEM',
    'CONTEXT_COMMAND',
    'CONTEXT_EXIT_CODE',
    'CONTEXT_WORKING_DIR',
    'CONTEXT_TIMEOUT',
    'CONTEXT_PHASE',

    # Context key constants (validation)
    'CONTEXT_EXPECTED_PATH',
    'CONTEXT_SEARCHED_PATHS',
    'CONTEXT_INSTALL_COMMAND',
    'CONTEXT_CONFIG_FILE',
    'CONTEXT_PROJECT_DIR',
    'CONTEXT_MISSING_FIELDS',
    'CONTEXT_INVALID_FIELDS',
    'CONTEXT_PARSE_ERROR',

    # Context key constants (execution)
    'CONTEXT_ERRORS',
    'CONTEXT_WARNINGS',
    'CONTEXT_STDOUT',
    'CONTEXT_STDERR',
    'CONTEXT_TESTS_RUN',
    'CONTEXT_TESTS_PASSED',
    'CONTEXT_TESTS_FAILED',
    'CONTEXT_TESTS_SKIPPED',
    'CONTEXT_FAILED_TESTS',
    'CONTEXT_OPERATION',
    'CONTEXT_ELAPSED',
    'CONTEXT_SUGGESTION',

    # Context key constants (dependencies)
    'CONTEXT_PACKAGE',
    'CONTEXT_VERSION',
    'CONTEXT_REASON',
    'CONTEXT_REGISTRY',
    'CONTEXT_SUGGESTED_VERSIONS',
    'CONTEXT_RETRYABLE',
    'CONTEXT_NETWORK_ERROR',
    'CONTEXT_CONFLICTING_VERSIONS',
    'CONTEXT_REQUIRED_BY',
    'CONTEXT_RESOLUTION_STRATEGY',
    'CONTEXT_SUGGESTED_RESOLUTION',
    'CONTEXT_DEPENDENCY_TREE',

    # Reason constants
    'REASON_NOT_FOUND',
    'REASON_NETWORK',
    'REASON_PERMISSION',
    'REASON_VERSION_CONFLICT',
    'REASON_CHECKSUM_FAILED',
    'REASON_REGISTRY_UNAVAILABLE',
]

# Version info
__version__ = '1.0.0'
__author__ = 'Artemis Development Team'
