"""
NPM Build Manager - Configuration Parser

WHY: Parse and validate package.json configuration files
RESPONSIBILITY: Read package.json and convert to NpmProjectInfo
PATTERNS: Parser pattern, Guard clauses, Exception wrapping

This module handles all package.json parsing, validation, and conversion
to type-safe data structures.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import json
import logging

from artemis_exceptions import wrap_exception
from build_system_exceptions import ProjectConfigurationError

from .models import NpmProjectInfo, PackageManager


class NpmConfigParser:
    """
    Parser for package.json configuration files.

    WHY: Centralize package.json parsing and validation logic
    RESPONSIBILITY: Parse package.json into NpmProjectInfo objects
    PATTERNS: Parser pattern, Guard clauses for validation

    This class handles reading and parsing package.json files, converting
    them into strongly-typed NpmProjectInfo objects with proper validation.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize config parser.

        WHY: Setup logger for diagnostics
        PATTERNS: Dependency injection for logger

        Args:
            logger: Logger instance
        """
        self.logger = logger or logging.getLogger(__name__)

    def validate_project(self, project_dir: Path) -> Path:
        """
        Validate package.json exists.

        WHY: Early validation to fail fast
        PATTERNS: Guard clause, Path validation

        Args:
            project_dir: Project directory

        Returns:
            Path to package.json

        Raises:
            ProjectConfigurationError: If package.json missing
        """
        package_json_path = project_dir / "package.json"

        if not package_json_path.exists():
            raise ProjectConfigurationError(
                "package.json not found",
                {"project_dir": str(project_dir)}
            )

        return package_json_path

    @wrap_exception(ProjectConfigurationError, "Failed to parse package.json")
    def parse_project_info(
        self,
        package_json_path: Path,
        package_manager: PackageManager
    ) -> Dict[str, Any]:
        """
        Parse package.json into project information.

        WHY: Convert raw JSON to typed data structure
        PATTERNS: Parser pattern, Exception wrapping

        Args:
            package_json_path: Path to package.json
            package_manager: Detected package manager

        Returns:
            Dictionary with project information

        Raises:
            ProjectConfigurationError: If package.json malformed
        """
        with open(package_json_path, 'r') as f:
            data = json.load(f)

        info = NpmProjectInfo(
            name=data.get("name", ""),
            version=data.get("version", "0.0.0"),
            description=data.get("description"),
            dependencies=data.get("dependencies", {}),
            dev_dependencies=data.get("devDependencies", {}),
            scripts=data.get("scripts", {}),
            package_manager=package_manager,
            engines=data.get("engines", {}),
            license=data.get("license"),
            repository=data.get("repository")
        )

        return info.to_dict()

    def get_scripts(self, package_json_path: Path) -> Dict[str, str]:
        """
        Extract scripts from package.json.

        WHY: Quick access to available scripts without full parse
        PATTERNS: Partial parsing for efficiency

        Args:
            package_json_path: Path to package.json

        Returns:
            Dictionary of script name -> command

        Raises:
            ProjectConfigurationError: If package.json malformed
        """
        if not package_json_path.exists():
            return {}

        with open(package_json_path, 'r') as f:
            data = json.load(f)

        return data.get("scripts", {})

    def has_script(self, package_json_path: Path, script_name: str) -> bool:
        """
        Check if a script exists in package.json.

        WHY: Validate script before execution
        PATTERNS: Guard clause for script validation

        Args:
            package_json_path: Path to package.json
            script_name: Script name to check

        Returns:
            True if script exists
        """
        scripts = self.get_scripts(package_json_path)
        return script_name in scripts


__all__ = [
    'NpmConfigParser'
]
