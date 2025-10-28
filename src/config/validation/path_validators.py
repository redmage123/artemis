#!/usr/bin/env python3
"""
Path Validators - File system path validation

WHY: Validates file system access before pipeline runs to prevent runtime errors
     when trying to write outputs, logs, or intermediate results.

RESPONSIBILITY: Validate file paths exist and are writable.

PATTERNS: Strategy pattern for path validation with pure functions.
"""

import os
from pathlib import Path
from typing import List, Tuple
from config.validation.models import ValidationResult


class PathValidator:
    """
    Validates important file paths exist and are writable.

    WHY: Validates file system access before pipeline runs to fail fast.
    RESPONSIBILITY: Validate path existence and write permissions only.
    PATTERNS: Pure functions for path validation, list comprehension for iteration.
    """

    @staticmethod
    def _get_absolute_path(path: str, script_dir: str) -> str:
        """
        Convert relative path to absolute.

        WHY: Pure function to ensure consistent path handling.
        PERFORMANCE: O(1) path conversion.

        Args:
            path: Path to convert
            script_dir: Script directory for relative paths

        Returns:
            Absolute path
        """
        if os.path.isabs(path):
            return path
        return os.path.join(script_dir, path)

    @staticmethod
    def _validate_single_path(path_str: str, description: str) -> ValidationResult:
        """
        Validate a single path is writable.

        WHY: Pure function extracted to avoid nested logic and enable testing.
        PERFORMANCE: O(1) file system operation with write test.

        Args:
            path_str: Path to validate
            description: Human-readable description

        Returns:
            ValidationResult for this path
        """
        path = Path(path_str)

        try:
            # Try to create directory and test write
            path.mkdir(parents=True, exist_ok=True)

            # Test writable
            test_file = path / ".test_write"
            test_file.write_text("test")
            test_file.unlink()

            return ValidationResult(
                check_name=f"Path: {description}",
                passed=True,
                message=f"{path} exists and writable",
                severity="info"
            )
        except Exception as e:
            return ValidationResult(
                check_name=f"Path: {description}",
                passed=False,
                message=f"{path} not writable: {e}",
                fix_suggestion=f"Ensure {path} exists and has write permissions"
            )

    @staticmethod
    def validate() -> List[ValidationResult]:
        """
        Validate all important file paths.

        WHY: Ensures all required paths are accessible before pipeline runs.
        PERFORMANCE: O(n) where n is number of paths to check.

        Returns:
            List of ValidationResults, one per path
        """
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Get paths from environment
        temp_dir = os.getenv("ARTEMIS_TEMP_DIR", "../../.artemis_data/temp")
        adr_dir = os.getenv("ARTEMIS_ADR_DIR", "../../.artemis_data/adrs")
        developer_dir = os.getenv("ARTEMIS_DEVELOPER_DIR", "../../.artemis_data/developer_output")

        # Convert to absolute paths using pure function
        temp_dir = PathValidator._get_absolute_path(temp_dir, script_dir)
        adr_dir = PathValidator._get_absolute_path(adr_dir, script_dir)
        developer_dir = PathValidator._get_absolute_path(developer_dir, script_dir)

        # Strategy pattern: Dictionary mapping of paths to descriptions
        paths_to_check = [
            (temp_dir, "Temp directory"),
            (adr_dir, "ADR directory"),
            (f"{developer_dir}/developer-a", "Developer A output"),
            (f"{developer_dir}/developer-b", "Developer B output"),
        ]

        # Functional approach: Use list comprehension instead of explicit loop
        return [
            PathValidator._validate_single_path(path_str, description)
            for path_str, description in paths_to_check
        ]
