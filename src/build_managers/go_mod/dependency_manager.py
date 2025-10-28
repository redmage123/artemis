"""
Go Dependency Manager

WHY: Dedicated module for dependency operations
RESPONSIBILITY: Handle all dependency-related operations (get, download, tidy, verify)
PATTERNS: Single Responsibility, command builder, guard clauses
"""

import logging
from typing import Optional, Callable

from artemis_exceptions import wrap_exception
from build_system_exceptions import (
    DependencyInstallError,
    BuildExecutionError
)
from build_manager_base import BuildResult


class GoDependencyManager:
    """
    WHY: Centralize all dependency management operations
    RESPONSIBILITY: Manage Go module dependencies
    PATTERNS: Single Responsibility, dependency injection
    """

    def __init__(
        self,
        execute_command: Callable[..., BuildResult],
        logger: Optional[logging.Logger] = None
    ):
        """
        WHY: Inject command executor for testability
        RESPONSIBILITY: Initialize with required dependencies
        PATTERNS: Dependency injection

        Args:
            execute_command: Command execution function
            logger: Logger instance
        """
        self.execute_command = execute_command
        self.logger = logger or logging.getLogger(__name__)

    @wrap_exception(DependencyInstallError, "Failed to add dependency")
    def install_dependency(
        self,
        module: str,
        version: Optional[str] = None
    ) -> bool:
        """
        WHY: Add a dependency to go.mod
        RESPONSIBILITY: Execute 'go get' with proper module specification
        PATTERNS: Guard clause, command builder

        Args:
            module: Module path
            version: Module version (optional)

        Returns:
            True if successful

        Raises:
            DependencyInstallError: If installation fails
        """
        if not module:
            raise DependencyInstallError(
                "Module path required",
                {"module": module}
            )

        module_spec = f"{module}@{version}" if version else module
        cmd = ["go", "get", module_spec]

        self.execute_command(
            cmd,
            timeout=120,
            error_type=DependencyInstallError,
            error_message=f"Failed to add module {module}"
        )

        self.logger.info(f"Added module {module}")
        return True

    @wrap_exception(BuildExecutionError, "Failed to download dependencies")
    def download_dependencies(self) -> BuildResult:
        """
        WHY: Download all dependencies to local cache
        RESPONSIBILITY: Execute 'go mod download'
        PATTERNS: Command execution wrapper

        Returns:
            BuildResult

        Raises:
            BuildExecutionError: If download fails
        """
        cmd = ["go", "mod", "download"]

        return self.execute_command(
            cmd,
            timeout=300,
            error_type=BuildExecutionError,
            error_message="Dependency download failed"
        )

    @wrap_exception(BuildExecutionError, "Failed to tidy dependencies")
    def tidy(self) -> BuildResult:
        """
        WHY: Clean up go.mod and go.sum
        RESPONSIBILITY: Execute 'go mod tidy' to remove unused dependencies
        PATTERNS: Command execution wrapper

        Returns:
            BuildResult

        Raises:
            BuildExecutionError: If tidy fails
        """
        cmd = ["go", "mod", "tidy"]

        return self.execute_command(
            cmd,
            timeout=120,
            error_type=BuildExecutionError,
            error_message="go mod tidy failed"
        )

    @wrap_exception(BuildExecutionError, "Failed to verify dependencies")
    def verify(self) -> BuildResult:
        """
        WHY: Verify dependencies have expected content
        RESPONSIBILITY: Execute 'go mod verify' for security
        PATTERNS: Command execution wrapper

        Returns:
            BuildResult

        Raises:
            BuildExecutionError: If verification fails
        """
        cmd = ["go", "mod", "verify"]

        return self.execute_command(
            cmd,
            timeout=60,
            error_type=BuildExecutionError,
            error_message="go mod verify failed"
        )
