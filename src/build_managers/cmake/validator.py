#!/usr/bin/env python3
"""
WHY: Validate CMake installation and project structure
RESPONSIBILITY: Verify prerequisites before build operations
PATTERNS: Guard Clauses, Exception Wrapper

Validator ensures CMake is installed and CMakeLists.txt exists before
attempting build operations.
"""

import re
from pathlib import Path
from typing import Optional
from artemis_exceptions import wrap_exception
from build_system_exceptions import (
    BuildSystemNotFoundError,
    ProjectConfigurationError
)


class CMakeValidator:
    """
    Validates CMake installation and project structure.

    WHY: Fail fast if prerequisites aren't met.
    PATTERNS: Guard clauses, Exception wrapping.
    """

    def __init__(self, logger: Optional['logging.Logger'] = None):
        """
        Initialize validator.

        Args:
            logger: Optional logger for diagnostics
        """
        self.logger = logger

    @wrap_exception(BuildSystemNotFoundError, "CMake not found")
    def validate_installation(self, execute_fn) -> Optional[str]:
        """
        Validate CMake is installed.

        WHY: Can't build without CMake - fail fast with clear error.

        Args:
            execute_fn: Function to execute cmake --version command

        Returns:
            CMake version string if found

        Raises:
            BuildSystemNotFoundError: If CMake not in PATH

        Example:
            >>> validator.validate_installation(execute_command_fn)
            '3.22.1'
        """
        result = execute_fn(
            ["cmake", "--version"],
            timeout=10,
            error_type=BuildSystemNotFoundError,
            error_message="CMake not installed or not in PATH"
        )

        # Extract version
        version = self._extract_version(result.output)

        if version and self.logger:
            self.logger.info(f"Using CMake version: {version}")

        return version

    def _extract_version(self, output: str) -> Optional[str]:
        """
        Extract CMake version from output.

        WHY: Version information useful for compatibility checks.

        Args:
            output: cmake --version output

        Returns:
            Version string or None

        Example:
            >>> validator._extract_version("cmake version 3.22.1")
            '3.22.1'
        """
        version_match = re.search(r"cmake version ([\d.]+)", output)
        return version_match.group(1) if version_match else None

    @wrap_exception(ProjectConfigurationError, "Invalid CMake project")
    def validate_project(self, project_dir: Path) -> Path:
        """
        Validate CMakeLists.txt exists.

        WHY: CMake requires CMakeLists.txt - fail fast if missing.

        Args:
            project_dir: Project directory

        Returns:
            Path to CMakeLists.txt

        Raises:
            ProjectConfigurationError: If CMakeLists.txt missing

        Example:
            >>> validator.validate_project(Path("/path/to/project"))
            PosixPath('/path/to/project/CMakeLists.txt')
        """
        cmakelists_path = project_dir / "CMakeLists.txt"

        # Guard clause - fail if CMakeLists.txt doesn't exist
        if not cmakelists_path.exists():
            raise ProjectConfigurationError(
                "CMakeLists.txt not found",
                {"project_dir": str(project_dir)}
            )

        return cmakelists_path
