#!/usr/bin/env python3
"""
.NET NuGet Package Manager

WHY: Dedicated module for NuGet package operations (add, remove, restore).
RESPONSIBILITY: Handle all NuGet package lifecycle operations.
PATTERNS: Single Responsibility Principle, Command pattern for operations.

Part of: managers.build_managers.dotnet
Dependencies: None (uses external dotnet CLI)
"""

from pathlib import Path
from typing import Optional, Callable, Any

from artemis_exceptions import wrap_exception
from build_system_exceptions import DependencyInstallError, BuildExecutionError


class NuGetManager:
    """
    Manager for NuGet package operations.

    WHY: Isolate NuGet-specific operations from main build manager.
    RESPONSIBILITY: Add, restore, and manage NuGet packages.
    PATTERNS: Single Responsibility, Facade pattern for dotnet CLI.
    """

    def __init__(
        self,
        project_file: Path,
        execute_command: Callable,
        logger: Any
    ):
        """
        Initialize NuGet manager.

        WHY: Dependency injection of command executor and logger.

        Args:
            project_file: Path to .csproj/.fsproj/.vbproj file
            execute_command: Command execution function from BuildManagerBase
            logger: Logger instance

        Guards:
            - project_file must not be None
        """
        if project_file is None:
            raise ValueError("project_file cannot be None")

        self.project_file = project_file
        self._execute_command = execute_command
        self.logger = logger

    @wrap_exception(DependencyInstallError, "Failed to add NuGet package")
    def add_package(
        self,
        package: str,
        version: Optional[str] = None
    ) -> bool:
        """
        Add a NuGet package to the project.

        WHY: Programmatically install dependencies without manual .csproj editing.

        Args:
            package: Package name (e.g., "Newtonsoft.Json")
            version: Package version (optional, uses latest if not specified)

        Returns:
            True if successful

        Raises:
            DependencyInstallError: If package installation fails

        Guards:
            - package must not be empty
        """
        if not package:
            raise DependencyInstallError(
                "Package name cannot be empty",
                {"package": package}
            )

        cmd = ["dotnet", "add", str(self.project_file), "package", package]

        if version:
            cmd.extend(["-v", version])

        self._execute_command(
            cmd,
            timeout=120,
            error_type=DependencyInstallError,
            error_message=f"Failed to add package {package}"
        )

        self.logger.info(f"Added package {package} {version or ''}")
        return True

    @wrap_exception(BuildExecutionError, "Failed to restore NuGet packages")
    def restore_packages(self, target_path: Path):
        """
        Restore NuGet packages for project or solution.

        WHY: Download all declared dependencies before build.

        Args:
            target_path: Path to .csproj, .sln, or directory

        Returns:
            BuildResult with restore details

        Raises:
            BuildExecutionError: If restore fails
        """
        cmd = ["dotnet", "restore", str(target_path)]

        return self._execute_command(
            cmd,
            timeout=300,
            error_type=BuildExecutionError,
            error_message="NuGet restore failed"
        )


__all__ = ["NuGetManager"]
