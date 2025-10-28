#!/usr/bin/env python3
"""
Path Validation Module

WHY: Validates file system paths exist and are writable before pipeline execution

RESPONSIBILITY: Validate file paths and directory access permissions

PATTERNS: Guard clauses for early returns, pure functions for path operations
"""

import os
from pathlib import Path
from typing import List
from ..models import ValidationResult
from ..constants import (
    DEFAULT_TEMP_DIR,
    DEFAULT_ADR_DIR,
    DEFAULT_DEVELOPER_DIR
)
from ..path_utils import resolve_relative_path, ensure_directory_writable, get_script_directory


class PathValidator:
    """
    Validates file paths exist and are writable

    WHY: Single Responsibility - handles only path validation

    PATTERNS: Guard clauses for early returns
    """

    def validate_paths(self) -> List[ValidationResult]:
        """
        Check important file paths exist and are writable

        WHY: Validates file system access before pipeline runs
        PERFORMANCE: O(n) where n is number of paths to check

        Returns:
            List of ValidationResult for each path check
        """
        script_dir = get_script_directory()

        temp_dir = os.getenv("ARTEMIS_TEMP_DIR", DEFAULT_TEMP_DIR)
        adr_dir = os.getenv("ARTEMIS_ADR_DIR", DEFAULT_ADR_DIR)
        developer_dir = os.getenv("ARTEMIS_DEVELOPER_DIR", DEFAULT_DEVELOPER_DIR)

        # Convert relative paths to absolute
        temp_dir = resolve_relative_path(temp_dir, script_dir)
        adr_dir = resolve_relative_path(adr_dir, script_dir)
        developer_dir = resolve_relative_path(developer_dir, script_dir)

        paths_to_check = [
            (temp_dir, "Temp directory"),
            (adr_dir, "ADR directory"),
            (f"{developer_dir}/developer-a", "Developer A output"),
            (f"{developer_dir}/developer-b", "Developer B output"),
        ]

        results = []
        for path_str, description in paths_to_check:
            path = Path(path_str)
            success, error_msg = ensure_directory_writable(path)

            if success:
                results.append(ValidationResult(
                    check_name=f"Path: {description}",
                    passed=True,
                    message=f"{path} exists and writable",
                    severity="info"
                ))
            else:
                results.append(ValidationResult(
                    check_name=f"Path: {description}",
                    passed=False,
                    message=f"{path} not writable: {error_msg}",
                    fix_suggestion=f"Ensure {path} exists and has write permissions"
                ))

        return results
