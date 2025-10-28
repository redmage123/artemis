#!/usr/bin/env python3
"""
Build System Exception Utilities

WHY: Provides convenience functions for creating build system exceptions,
     reducing boilerplate and ensuring consistent exception instantiation.

RESPONSIBILITY: Offer helper functions and utilities for exception creation,
                error formatting, and context building.

PATTERNS:
- Factory Pattern: build_error() factory function for exception creation
- Builder Pattern: Context builders for common error scenarios
- DRY Principle: Eliminates repeated exception instantiation code

Design Philosophy:
- Convenience functions reduce verbosity in exception creation
- Type hints ensure correct exception types
- Context builders enforce consistent context structure
- Functional approach: Pure functions for exception creation
"""

from typing import Dict, Any, Type, Optional
from build_managers.exceptions.base import BuildSystemError


def build_error(
    message: str,
    error_type: Type[BuildSystemError] = BuildSystemError,
    **context: Any
) -> BuildSystemError:
    """
    Convenience factory function to create build system errors.

    WHY: Reduces boilerplate when creating exceptions with context,
         enables cleaner error raising with keyword arguments.

    PATTERNS:
    - Factory Pattern: Creates exceptions of specified type
    - Builder Pattern: Constructs context from keyword arguments
    - Fluent Interface: Can be used inline with raise statement

    PERFORMANCE: O(1) - simple object instantiation

    Args:
        message: Human-readable error message
        error_type: Exception class to instantiate (default: BuildSystemError)
        **context: Context as keyword arguments (converted to dict)

    Returns:
        Initialized exception instance of specified type

    Raises:
        TypeError: If error_type is not a BuildSystemError subclass

    Example:
        >>> raise build_error(
        ...     "Maven not found",
        ...     error_type=BuildSystemNotFoundError,
        ...     build_system="maven",
        ...     expected_path="/usr/bin/mvn"
        ... )

    Example (with default type):
        >>> raise build_error(
        ...     "Build failed",
        ...     build_system="gradle",
        ...     exit_code=1
        ... )
    """
    # Guard clause: Validate error_type is BuildSystemError subclass
    if not issubclass(error_type, BuildSystemError):
        raise TypeError(
            f"error_type must be BuildSystemError subclass, got {error_type}"
        )

    # Functional approach: Create immutable context dict from kwargs
    context_dict = dict(context) if context else {}

    return error_type(message, context_dict)


def create_not_found_error(
    build_system: str,
    expected_path: str,
    searched_paths: Optional[list] = None,
    install_command: Optional[str] = None
) -> "BuildSystemNotFoundError":
    """
    Create BuildSystemNotFoundError with standardized context.

    WHY: Ensures consistent context structure for "not found" errors,
         reduces boilerplate in build system detection code.

    PATTERNS: Builder Pattern for consistent error context

    Args:
        build_system: Name of the build system (maven, gradle, npm, etc.)
        expected_path: Path where tool was expected
        searched_paths: List of paths that were searched (optional)
        install_command: Command to install the tool (optional)

    Returns:
        BuildSystemNotFoundError with standardized context

    Example:
        >>> raise create_not_found_error(
        ...     build_system="maven",
        ...     expected_path="/usr/bin/mvn",
        ...     searched_paths=["/usr/bin", "/usr/local/bin"],
        ...     install_command="apt-get install maven"
        ... )
    """
    # Import here to avoid circular dependency
    from build_managers.exceptions.validation import BuildSystemNotFoundError

    context = {
        'build_system': build_system,
        'expected_path': expected_path
    }

    # Add optional context fields (functional approach: build new dict)
    if searched_paths:
        context['searched_paths'] = searched_paths
    if install_command:
        context['install_command'] = install_command

    message = f"{build_system} executable not found at {expected_path}"
    return BuildSystemNotFoundError(message, context)


def create_config_error(
    config_file: str,
    project_dir: str,
    missing_fields: Optional[list] = None,
    invalid_fields: Optional[list] = None,
    parse_error: Optional[str] = None
) -> "ProjectConfigurationError":
    """
    Create ProjectConfigurationError with standardized context.

    WHY: Ensures consistent context structure for configuration errors,
         reduces boilerplate in config validation code.

    PATTERNS: Builder Pattern for consistent error context

    Args:
        config_file: Name of the configuration file
        project_dir: Project directory path
        missing_fields: List of missing required fields (optional)
        invalid_fields: List of invalid fields (optional)
        parse_error: Parse error details (optional)

    Returns:
        ProjectConfigurationError with standardized context

    Example:
        >>> raise create_config_error(
        ...     config_file="pom.xml",
        ...     project_dir="/path/to/project",
        ...     missing_fields=["groupId", "artifactId"]
        ... )
    """
    # Import here to avoid circular dependency
    from build_managers.exceptions.validation import ProjectConfigurationError

    context = {
        'config_file': config_file,
        'project_dir': project_dir
    }

    # Build error message based on what's provided
    error_parts = []

    if missing_fields:
        context['missing_fields'] = missing_fields
        error_parts.append(f"missing fields: {', '.join(missing_fields)}")

    if invalid_fields:
        context['invalid_fields'] = invalid_fields
        error_parts.append(f"invalid fields: {', '.join(invalid_fields)}")

    if parse_error:
        context['parse_error'] = parse_error
        error_parts.append(f"parse error: {parse_error}")

    # Functional approach: Use join to build message
    message_suffix = "; ".join(error_parts) if error_parts else "invalid configuration"
    message = f"{config_file} configuration error: {message_suffix}"

    return ProjectConfigurationError(message, context)


def create_build_execution_error(
    build_system: str,
    phase: str,
    exit_code: int,
    errors: Optional[list] = None,
    command: Optional[str] = None,
    working_dir: Optional[str] = None
) -> "BuildExecutionError":
    """
    Create BuildExecutionError with standardized context.

    WHY: Ensures consistent context structure for build execution errors,
         reduces boilerplate in build execution code.

    PATTERNS: Builder Pattern for consistent error context

    Args:
        build_system: Name of the build system
        phase: Build phase that failed (compile, test, package)
        exit_code: Process exit code
        errors: List of error messages (optional)
        command: Command that was executed (optional)
        working_dir: Working directory (optional)

    Returns:
        BuildExecutionError with standardized context

    Example:
        >>> raise create_build_execution_error(
        ...     build_system="maven",
        ...     phase="compile",
        ...     exit_code=1,
        ...     errors=["Error: Cannot find symbol"],
        ...     command="mvn clean compile"
        ... )
    """
    # Import here to avoid circular dependency
    from build_managers.exceptions.execution import BuildExecutionError

    context = {
        'build_system': build_system,
        'phase': phase,
        'exit_code': exit_code
    }

    # Add optional context fields
    if errors:
        context['errors'] = errors
    if command:
        context['command'] = command
    if working_dir:
        context['working_dir'] = working_dir

    # Build error message
    error_count = len(errors) if errors else 0
    error_suffix = f" with {error_count} errors" if error_count > 0 else ""
    message = f"{build_system} {phase} failed{error_suffix} (exit code: {exit_code})"

    return BuildExecutionError(message, context)


def format_error_summary(error: BuildSystemError) -> str:
    """
    Format exception as human-readable summary.

    WHY: Provides consistent error formatting for logging and user display.

    PATTERNS: Visitor Pattern for error formatting

    Args:
        error: BuildSystemError instance

    Returns:
        Formatted error summary string

    Example:
        >>> summary = format_error_summary(error)
        >>> print(summary)
        BuildSystemError: Maven build failed
        Build System: maven
        Phase: compile
        Exit Code: 1
    """
    # Start with error type and message
    lines = [
        f"{type(error).__name__}: {str(error.args[0]) if error.args else 'Unknown error'}"
    ]

    # Add key context fields if present (functional approach: list comprehension)
    context_mappings = [
        ('build_system', 'Build System'),
        ('phase', 'Phase'),
        ('exit_code', 'Exit Code'),
        ('package', 'Package'),
        ('version', 'Version'),
        ('config_file', 'Config File'),
        ('timeout', 'Timeout'),
    ]

    # Functional approach: Use list comprehension with guard clause
    context_lines = [
        f"{display_name}: {error.get_context_value(key)}"
        for key, display_name in context_mappings
        if error.get_context_value(key) is not None
    ]

    lines.extend(context_lines)

    # Functional approach: Join lines without mutation
    return "\n".join(lines)


# Export commonly used context key constants (DRY principle)
__all__ = [
    'build_error',
    'create_not_found_error',
    'create_config_error',
    'create_build_execution_error',
    'format_error_summary',
]
