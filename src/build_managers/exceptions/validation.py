#!/usr/bin/env python3
"""
Build System Validation Exceptions

WHY: Separates validation-related errors (missing tools, invalid configs) from
     execution errors, enabling more precise error handling and recovery strategies.

RESPONSIBILITY: Define exceptions for build system discovery and configuration
                validation failures (missing executables, invalid config files).

PATTERNS:
- Exception Hierarchy: Specialized exceptions for different validation failures
- Semantic Naming: Exception names clearly indicate the problem type
- Context Enrichment: Each exception carries relevant diagnostic information

Design Philosophy:
- Validation errors are recoverable (install tool, fix config)
- Clear distinction between "not found" vs "found but invalid"
- Rich context enables automated recovery or helpful error messages
"""

from typing import Dict, Any, Optional, List
from build_managers.exceptions.base import BuildSystemError, CONTEXT_BUILD_SYSTEM


class BuildSystemNotFoundError(BuildSystemError):
    """
    Build system executable not found in PATH.

    WHY: Distinguishes "tool not installed" from other failures, enabling
         automated installation or clear user guidance to install required tools.

    RESPONSIBILITY: Signal that required build tool executable (maven, gradle,
                   npm, cargo, etc.) is not installed or not in PATH.

    PATTERNS:
    - Semantic Exception: Name clearly indicates the specific problem
    - Context Preservation: Stores expected paths and search locations

    Example:
        >>> raise BuildSystemNotFoundError(
        ...     "Maven executable not found",
        ...     context={
        ...         'build_system': 'maven',
        ...         'expected_path': '/usr/bin/mvn',
        ...         'searched_paths': ['/usr/bin', '/usr/local/bin'],
        ...         'install_command': 'apt-get install maven'
        ...     }
        ... )

    Common Context Keys:
        - build_system: Name of the build system (maven, gradle, npm, etc.)
        - expected_path: Where the tool was expected to be found
        - searched_paths: List of paths that were checked
        - install_command: Suggested command to install the tool
    """

    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ) -> None:
        """
        Initialize build system not found error.

        WHY: Provides specialized initialization for tool discovery failures
             with enhanced context for user guidance.

        Args:
            message: Human-readable error message
            context: Diagnostic context (build_system, expected_path, etc.)
            original_exception: Original exception if wrapping
        """
        super().__init__(message, context, original_exception)

    def get_install_suggestion(self) -> Optional[str]:
        """
        Get installation suggestion if available.

        WHY: Functional accessor for install command without exposing
             internal context structure.

        PERFORMANCE: O(1) dictionary lookup

        Returns:
            Installation command suggestion or None

        Example:
            >>> error.get_install_suggestion()
            'apt-get install maven'
        """
        return self.get_context_value('install_command')


class ProjectConfigurationError(BuildSystemError):
    """
    Project configuration file missing or invalid.

    WHY: Distinguishes configuration problems from execution failures,
         enabling targeted error messages about what to fix in config files.

    RESPONSIBILITY: Signal that build configuration file (pom.xml, package.json,
                   build.gradle, Cargo.toml, etc.) is missing, malformed, or
                   contains invalid settings.

    PATTERNS:
    - Validation Pattern: Checks configuration before execution
    - Error Context: Provides specific details about what's wrong with config

    Example:
        >>> raise ProjectConfigurationError(
        ...     "pom.xml is missing required groupId",
        ...     context={
        ...         'config_file': 'pom.xml',
        ...         'project_dir': '/path/to/project',
        ...         'missing_fields': ['groupId', 'artifactId'],
        ...         'xml_line': 15
        ...     }
        ... )

    Common Context Keys:
        - config_file: Name of the configuration file
        - project_dir: Project directory path
        - missing_fields: List of missing required fields
        - invalid_fields: List of fields with invalid values
        - parse_error: Parsing error details if applicable
        - xml_line/json_line: Line number where error occurred
    """

    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ) -> None:
        """
        Initialize project configuration error.

        WHY: Provides specialized initialization for configuration validation
             failures with enhanced context for developers.

        Args:
            message: Human-readable error message
            context: Diagnostic context (config_file, missing_fields, etc.)
            original_exception: Original exception if wrapping parse errors
        """
        super().__init__(message, context, original_exception)

    def get_missing_fields(self) -> List[str]:
        """
        Get list of missing required fields.

        WHY: Functional accessor for missing fields without exposing
             internal context structure.

        Returns:
            List of missing field names (empty if not applicable)

        Example:
            >>> error.get_missing_fields()
            ['groupId', 'artifactId']
        """
        return self.get_context_value('missing_fields', [])

    def get_config_file(self) -> Optional[str]:
        """
        Get configuration file name.

        WHY: Functional accessor for config file path.

        Returns:
            Configuration file name or None

        Example:
            >>> error.get_config_file()
            'pom.xml'
        """
        return self.get_context_value('config_file')


# Module-level constants for validation error context (DRY principle)
CONTEXT_EXPECTED_PATH = "expected_path"
CONTEXT_SEARCHED_PATHS = "searched_paths"
CONTEXT_INSTALL_COMMAND = "install_command"
CONTEXT_CONFIG_FILE = "config_file"
CONTEXT_PROJECT_DIR = "project_dir"
CONTEXT_MISSING_FIELDS = "missing_fields"
CONTEXT_INVALID_FIELDS = "invalid_fields"
CONTEXT_PARSE_ERROR = "parse_error"
