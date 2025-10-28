#!/usr/bin/env python3
"""
WHY: Execute CMake build operations
RESPONSIBILITY: Build targets with parallel support
PATTERNS: Builder (command construction), Guard Clauses

Builder executes cmake --build to compile the project.
"""

from pathlib import Path
from typing import Optional
import multiprocessing
from artemis_exceptions import wrap_exception
from build_system_exceptions import BuildExecutionError
from build_manager_base import BuildResult


class CMakeBuilder:
    """
    Builds CMake projects.

    WHY: Executes compilation using configured build system.
    PATTERNS: Builder pattern, Guard clauses.
    """

    @wrap_exception(BuildExecutionError, "Build failed")
    def build(
        self,
        build_dir: Path,
        execute_fn,
        configure_fn,
        clean_fn,
        target: Optional[str] = None,
        parallel: bool = True,
        clean: bool = False
    ) -> BuildResult:
        """
        Build CMake project.

        WHY: Compiles source code into binaries.

        Args:
            build_dir: Build directory
            execute_fn: Function to execute cmake --build
            configure_fn: Function to configure if needed
            clean_fn: Function to clean
            target: Specific target to build (None = all)
            parallel: Enable parallel build
            clean: Clean before building

        Returns:
            BuildResult

        Raises:
            BuildExecutionError: If build fails

        Example:
            >>> builder.build(
            ...     Path("build"), execute_fn, configure_fn, clean_fn,
            ...     target="myapp", parallel=True
            ... )
        """
        # Configure if not already done (guard clause)
        if not (build_dir / "CMakeCache.txt").exists():
            configure_fn()

        # Clean first if requested
        if clean:
            clean_fn()

        # Build command
        cmd = self._build_command(build_dir, target, parallel)

        return execute_fn(
            cmd,
            timeout=600,
            error_type=BuildExecutionError,
            error_message="CMake build failed"
        )

    def _build_command(
        self,
        build_dir: Path,
        target: Optional[str],
        parallel: bool
    ) -> list:
        """
        Build cmake --build command.

        WHY: Centralizes command construction.

        Args:
            build_dir: Build directory
            target: Build target
            parallel: Parallel build flag

        Returns:
            Command list
        """
        cmd = ["cmake", "--build", str(build_dir)]

        # Target
        if target:
            cmd.extend(["--target", target])

        # Parallel build
        if parallel:
            cpu_count = multiprocessing.cpu_count()
            cmd.extend(["--parallel", str(cpu_count)])

        return cmd
