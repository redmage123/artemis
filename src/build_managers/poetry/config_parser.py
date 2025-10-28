"""
Poetry Build Manager - Configuration Parser

WHY: Isolate pyproject.toml parsing and validation logic
RESPONSIBILITY: Parse and validate Poetry configuration files
PATTERNS: Single Responsibility, Guard Clauses, Exception Wrapping

This module handles all pyproject.toml file parsing, validation, and project
information extraction for Poetry projects.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import toml

from artemis_exceptions import wrap_exception
from build_system_exceptions import ProjectConfigurationError
from .models import PoetryProjectInfo


class PoetryConfigParser:
    """
    Parser for Poetry pyproject.toml files.

    WHY: Dedicated parser for Poetry configuration
    RESPONSIBILITY: Read, validate, and extract Poetry project information
    PATTERNS: Single Responsibility Principle, Guard Clauses
    """

    def __init__(self, logger: Optional['logging.Logger'] = None):
        """
        Initialize parser.

        Args:
            logger: Logger instance for diagnostic output
        """
        self.logger = logger

    @wrap_exception(ProjectConfigurationError, "Invalid Poetry project")
    def validate_project(self, project_dir: Path) -> Path:
        """
        Validate pyproject.toml exists and contains [tool.poetry] section.

        WHY: Early validation prevents cryptic errors downstream
        PATTERNS: Guard clauses - fail fast on invalid configuration

        Args:
            project_dir: Project directory path

        Returns:
            Path to valid pyproject.toml

        Raises:
            ProjectConfigurationError: If pyproject.toml missing or invalid
        """
        pyproject_path = project_dir / "pyproject.toml"

        if not pyproject_path.exists():
            raise ProjectConfigurationError(
                "pyproject.toml not found",
                {"project_dir": str(project_dir)}
            )

        # Load and validate structure
        with open(pyproject_path, 'r') as f:
            data = toml.load(f)

        if "tool" not in data:
            raise ProjectConfigurationError(
                "pyproject.toml is not a Poetry project (missing [tool.poetry])",
                {"project_dir": str(project_dir)}
            )

        if "poetry" not in data.get("tool", {}):
            raise ProjectConfigurationError(
                "pyproject.toml is not a Poetry project (missing [tool.poetry])",
                {"project_dir": str(project_dir)}
            )

        return pyproject_path

    @wrap_exception(ProjectConfigurationError, "Failed to parse pyproject.toml")
    def parse_project_info(
        self,
        pyproject_path: Path,
        poetry_lock_path: Path
    ) -> Dict[str, Any]:
        """
        Parse pyproject.toml for project information.

        WHY: Extract structured project metadata for analysis and reporting
        PATTERNS: Guard clauses, explicit error handling

        Args:
            pyproject_path: Path to pyproject.toml
            poetry_lock_path: Path to poetry.lock (for lock file detection)

        Returns:
            Dictionary with project information

        Raises:
            ProjectConfigurationError: If pyproject.toml malformed
        """
        if not pyproject_path.exists():
            raise ProjectConfigurationError(
                "pyproject.toml not found",
                {"path": str(pyproject_path)}
            )

        with open(pyproject_path, 'r') as f:
            data = toml.load(f)

        poetry_section = data.get("tool", {}).get("poetry", {})

        info = PoetryProjectInfo(
            name=poetry_section.get("name", ""),
            version=poetry_section.get("version", "0.1.0"),
            description=poetry_section.get("description"),
            authors=poetry_section.get("authors", []),
            license=poetry_section.get("license"),
            readme=poetry_section.get("readme"),
            python_version=poetry_section.get("dependencies", {}).get("python", "^3.8"),
            dependencies=poetry_section.get("dependencies", {}),
            dev_dependencies=poetry_section.get("dev-dependencies", {}),
            scripts=poetry_section.get("scripts", {}),
            has_lock_file=poetry_lock_path.exists()
        )

        return info.to_dict()

    @staticmethod
    def extract_section(
        pyproject_path: Path,
        section_path: str
    ) -> Optional[Dict[str, Any]]:
        """
        Extract specific section from pyproject.toml.

        WHY: Targeted extraction without parsing entire file
        PATTERNS: Static method - no state required

        Args:
            pyproject_path: Path to pyproject.toml
            section_path: Dot-separated path (e.g., "tool.poetry.dependencies")

        Returns:
            Section data or None if not found
        """
        if not pyproject_path.exists():
            return None

        with open(pyproject_path, 'r') as f:
            data = toml.load(f)

        # Navigate to section
        current = data
        for key in section_path.split('.'):
            if not isinstance(current, dict):
                return None
            current = current.get(key)
            if current is None:
                return None

        return current


__all__ = [
    'PoetryConfigParser'
]
