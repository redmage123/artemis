#!/usr/bin/env python3
"""
Composer JSON Parser

WHY: Isolated composer.json parsing logic
RESPONSIBILITY: Parse and validate composer.json files
PATTERNS:
- Single Responsibility: Only handles JSON parsing
- Guard clauses: Early returns for validation
- Exception wrapping: Consistent error handling
"""

from pathlib import Path
from typing import Dict, Any
import json

from artemis_exceptions import wrap_exception
from build_system_exceptions import ProjectConfigurationError
from .models import ComposerProjectInfo


class ComposerParser:
    """
    Parser for composer.json files.

    WHY: Separate parsing logic from manager operations
    RESPONSIBILITY: Read, parse, and extract information from composer.json
    """

    def __init__(self, project_dir: Path):
        """
        Initialize parser.

        Args:
            project_dir: Directory containing composer.json

        Raises:
            ProjectConfigurationError: If composer.json not found
        """
        if not isinstance(project_dir, Path):
            project_dir = Path(project_dir)

        self.project_dir = project_dir
        self.composer_json_path = project_dir / "composer.json"
        self.composer_lock_path = project_dir / "composer.lock"

        if not self.composer_json_path.exists():
            raise ProjectConfigurationError(
                "composer.json not found",
                {"project_dir": str(self.project_dir)}
            )

    @wrap_exception(ProjectConfigurationError, "Failed to parse composer.json")
    def parse_composer_json(self) -> Dict[str, Any]:
        """
        Parse composer.json file.

        WHY: Centralized JSON parsing with error handling
        RESPONSIBILITY: Read and parse JSON, handle file errors

        Returns:
            Parsed JSON as dictionary

        Raises:
            ProjectConfigurationError: If file cannot be read or parsed
        """
        with open(self.composer_json_path, 'r') as f:
            return json.load(f)

    @wrap_exception(ProjectConfigurationError, "Failed to extract project info")
    def get_project_info(self) -> Dict[str, Any]:
        """
        Extract structured project information from composer.json.

        WHY: Transform raw JSON into typed data structure
        RESPONSIBILITY: Map JSON fields to ComposerProjectInfo dataclass

        Returns:
            Dictionary representation of project info

        Raises:
            ProjectConfigurationError: If composer.json malformed
        """
        data = self.parse_composer_json()

        # Extract PHP version from require section
        php_version = data.get("require", {}).get("php", ">=7.0")

        info = ComposerProjectInfo(
            name=data.get("name", ""),
            description=data.get("description"),
            type=data.get("type", "library"),
            license=data.get("license"),
            php_version=php_version,
            require=data.get("require", {}),
            require_dev=data.get("require-dev", {}),
            autoload=data.get("autoload", {}),
            scripts=data.get("scripts", {}),
            has_lock_file=self.composer_lock_path.exists()
        )

        return info.to_dict()

    def has_script(self, script_name: str) -> bool:
        """
        Check if a script is defined in composer.json.

        WHY: Avoid parsing exceptions when checking script existence
        RESPONSIBILITY: Validate script availability before execution

        Args:
            script_name: Name of script to check

        Returns:
            True if script exists in scripts section
        """
        try:
            data = self.parse_composer_json()
            return script_name in data.get("scripts", {})
        except ProjectConfigurationError:
            return False

    def get_scripts(self) -> Dict[str, Any]:
        """
        Get all scripts defined in composer.json.

        WHY: Enable script enumeration and validation
        RESPONSIBILITY: Extract scripts section

        Returns:
            Dictionary of script names to commands
        """
        data = self.parse_composer_json()
        return data.get("scripts", {})

    def get_php_version(self) -> str:
        """
        Extract PHP version requirement.

        WHY: Enable version compatibility checks
        RESPONSIBILITY: Parse PHP version from require section

        Returns:
            PHP version constraint (e.g., ">=7.4")
        """
        data = self.parse_composer_json()
        return data.get("require", {}).get("php", ">=7.0")
