#!/usr/bin/env python3
"""
WHY: Configure CMake projects with build types and options
RESPONSIBILITY: Generate build configuration
PATTERNS: Builder (command construction), Guard Clauses

Configurator prepares CMake build system by running cmake configuration.
"""

from pathlib import Path
from typing import Dict, Optional
from artemis_exceptions import wrap_exception
from build_system_exceptions import BuildExecutionError
from build_manager_base import BuildResult


class CMakeConfigurator:
    """
    Configures CMake projects.

    WHY: Configuration must happen before build - generates build system.
    PATTERNS: Builder (command construction).
    """

    @wrap_exception(BuildExecutionError, "CMake configuration failed")
    def configure(
        self,
        project_dir: Path,
        build_dir: Path,
        execute_fn,
        build_type: str = "Release",
        generator: Optional[str] = None,
        options: Optional[Dict[str, str]] = None
    ) -> BuildResult:
        """
        Configure CMake project.

        WHY: Generates build system files (Makefiles, Ninja files, etc.).

        Args:
            project_dir: Source directory
            build_dir: Build directory
            execute_fn: Function to execute cmake command
            build_type: Build type (Debug, Release, etc.)
            generator: CMake generator
            options: Additional CMake options

        Returns:
            BuildResult

        Raises:
            BuildExecutionError: If configuration fails

        Example:
            >>> configurator.configure(
            ...     Path("."), Path("build"), execute_fn,
            ...     build_type="Release",
            ...     options={"BUILD_TESTING": "ON"}
            ... )
        """
        # Create build directory
        build_dir.mkdir(parents=True, exist_ok=True)

        # Build command
        cmd = self._build_configure_command(
            project_dir,
            build_dir,
            build_type,
            generator,
            options
        )

        return execute_fn(
            cmd,
            timeout=120,
            error_type=BuildExecutionError,
            error_message="CMake configuration failed"
        )

    def _build_configure_command(
        self,
        project_dir: Path,
        build_dir: Path,
        build_type: str,
        generator: Optional[str],
        options: Optional[Dict[str, str]]
    ) -> list:
        """
        Build cmake configure command.

        WHY: Centralizes command construction logic.

        Args:
            project_dir: Source directory
            build_dir: Build directory
            build_type: Build type
            generator: CMake generator
            options: CMake options

        Returns:
            Command list
        """
        cmd = ["cmake", "-B", str(build_dir), "-S", str(project_dir)]

        # Build type
        cmd.append(f"-DCMAKE_BUILD_TYPE={build_type}")

        # Generator
        if generator:
            cmd.extend(["-G", generator])

        # Additional options
        if options:
            for key, value in options.items():
                cmd.append(f"-D{key}={value}")

        return cmd
