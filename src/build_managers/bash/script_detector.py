#!/usr/bin/env python3
"""
Bash Manager - Script Detector

WHY: Separate script discovery logic for Single Responsibility Principle
RESPONSIBILITY: Find and catalog all shell scripts in a project
PATTERNS: Strategy Pattern, Iterator Pattern, Guard Clauses

This module handles the discovery and cataloging of shell scripts,
providing a clean separation from build orchestration logic.
"""

from pathlib import Path
from typing import List, Set, Optional, Callable
import logging

from .models import ShellScript


class ScriptDetector:
    """
    Detects and catalogs shell scripts in a project.

    WHY: Single Responsibility - only concerned with finding scripts
    RESPONSIBILITY: Recursive script discovery with configurable filters
    PATTERNS: Strategy Pattern (configurable filters), Guard Clauses
    """

    # Default shell script extensions
    DEFAULT_EXTENSIONS: Set[str] = {'.sh', '.bash'}

    # Default directories to skip (common patterns)
    DEFAULT_SKIP_DIRS: Set[str] = {
        'node_modules',
        '.git',
        '__pycache__',
        '.venv',
        'venv',
        'env',
        '.tox',
        'dist',
        'build',
        '.mypy_cache',
        '.pytest_cache'
    }

    def __init__(
        self,
        project_dir: Path,
        extensions: Optional[Set[str]] = None,
        skip_dirs: Optional[Set[str]] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize script detector.

        WHY: Dependency Injection for configurability
        PATTERNS: Dependency Injection, Builder Pattern

        Args:
            project_dir: Root directory to search
            extensions: Shell script extensions (default: .sh, .bash)
            skip_dirs: Directories to skip during traversal
            logger: Logger instance
        """
        self.project_dir = Path(project_dir)
        self.extensions = extensions or self.DEFAULT_EXTENSIONS
        self.skip_dirs = skip_dirs or self.DEFAULT_SKIP_DIRS
        self.logger = logger or logging.getLogger(__name__)

    def detect_scripts(self) -> List[ShellScript]:
        """
        Recursively find all shell scripts.

        WHY: Single method with clear purpose
        RESPONSIBILITY: Orchestrate script discovery
        PATTERNS: Guard Clauses (early returns), Iterator Pattern

        Returns:
            List of ShellScript objects

        Raises:
            OSError: If directory access fails
        """
        # Guard: Ensure directory exists
        if not self.project_dir.exists():
            self.logger.warning(f"Project directory not found: {self.project_dir}")
            return []

        # Guard: Ensure it's a directory
        if not self.project_dir.is_dir():
            self.logger.warning(f"Not a directory: {self.project_dir}")
            return []

        scripts: List[ShellScript] = []

        # Traverse directory tree
        for file_path in self._walk_directory(self.project_dir):
            # Guard: Skip if not matching extension
            if file_path.suffix not in self.extensions:
                continue

            # Guard: Skip if file is not readable
            if not self._is_readable(file_path):
                self.logger.debug(f"Skipping unreadable file: {file_path}")
                continue

            # Create ShellScript value object
            try:
                script = self._create_shell_script(file_path)
                scripts.append(script)
                self.logger.debug(f"Found script: {script.relative_path}")
            except OSError as e:
                self.logger.warning(f"Failed to process {file_path}: {e}")
                continue

        self.logger.info(f"Detected {len(scripts)} shell script(s)")
        return scripts

    def has_scripts(self) -> bool:
        """
        Quick check if any shell scripts exist.

        WHY: Fast detection without full catalog
        RESPONSIBILITY: Boolean existence check
        PATTERNS: Guard Clauses

        Returns:
            True if any scripts found
        """
        # Guard: Ensure directory exists
        if not self.project_dir.exists() or not self.project_dir.is_dir():
            return False

        # Short-circuit on first match
        for file_path in self._walk_directory(self.project_dir):
            if file_path.suffix in self.extensions:
                return True

        return False

    def _walk_directory(self, directory: Path) -> List[Path]:
        """
        Walk directory tree with skip_dirs filtering.

        WHY: Centralize directory traversal logic
        RESPONSIBILITY: Recursive traversal with filtering
        PATTERNS: Iterator Pattern, Guard Clauses

        Args:
            directory: Starting directory

        Returns:
            List of file paths
        """
        files: List[Path] = []

        try:
            for item in directory.iterdir():
                # Guard: Skip hidden files/dirs (start with .)
                if item.name.startswith('.') and item.is_dir():
                    continue

                # Guard: Skip configured directories
                if item.is_dir() and item.name in self.skip_dirs:
                    self.logger.debug(f"Skipping directory: {item}")
                    continue

                # Recurse into subdirectories
                if item.is_dir():
                    files.extend(self._walk_directory(item))
                elif item.is_file():
                    files.append(item)

        except PermissionError as e:
            self.logger.warning(f"Permission denied: {directory}: {e}")

        return files

    def _is_readable(self, file_path: Path) -> bool:
        """
        Check if file is readable.

        WHY: Guard against permission errors
        RESPONSIBILITY: Validate file access
        PATTERNS: Guard Clause

        Args:
            file_path: File to check

        Returns:
            True if readable
        """
        try:
            # Attempt to get file stats (fast check)
            file_path.stat()
            return True
        except (OSError, PermissionError):
            return False

    def _create_shell_script(self, file_path: Path) -> ShellScript:
        """
        Create ShellScript value object.

        WHY: Centralize object creation
        RESPONSIBILITY: Build immutable ShellScript
        PATTERNS: Factory Method

        Args:
            file_path: Absolute path to script

        Returns:
            ShellScript instance

        Raises:
            OSError: If file stats cannot be retrieved
        """
        relative = file_path.relative_to(self.project_dir)
        size = file_path.stat().st_size

        return ShellScript(
            path=file_path,
            relative_path=relative,
            size_bytes=size
        )

    def filter_scripts(
        self,
        scripts: List[ShellScript],
        predicate: Callable[[ShellScript], bool]
    ) -> List[ShellScript]:
        """
        Filter scripts using custom predicate.

        WHY: Functional programming approach for flexibility
        RESPONSIBILITY: Apply custom filters
        PATTERNS: Strategy Pattern, Higher-Order Functions

        Args:
            scripts: Scripts to filter
            predicate: Filter function

        Returns:
            Filtered list

        Example:
            # Filter scripts larger than 1KB
            large_scripts = detector.filter_scripts(
                scripts,
                lambda s: s.size_bytes > 1024
            )
        """
        return [s for s in scripts if predicate(s)]

    def get_scripts_by_directory(
        self,
        scripts: List[ShellScript]
    ) -> dict[Path, List[ShellScript]]:
        """
        Group scripts by parent directory.

        WHY: Useful for directory-level operations
        RESPONSIBILITY: Organize scripts by location
        PATTERNS: Grouping Pattern

        Args:
            scripts: Scripts to group

        Returns:
            Dictionary mapping directories to scripts
        """
        grouped: dict[Path, List[ShellScript]] = {}

        for script in scripts:
            parent = script.path.parent
            if parent not in grouped:
                grouped[parent] = []
            grouped[parent].append(script)

        return grouped


__all__ = [
    'ScriptDetector'
]
