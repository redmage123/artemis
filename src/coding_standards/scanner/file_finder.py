#!/usr/bin/env python3
"""
WHY: Find Python files for scanning
RESPONSIBILITY: Discover Python files while respecting exclusions
PATTERNS: Iterator (yield files as found)

File finder enables scalable codebase scanning.
"""

from pathlib import Path
from typing import Iterator, Set


class PythonFileFinder:
    """
    Finds Python files in codebase.

    WHY: Centralized file discovery with exclusion logic.
    RESPONSIBILITY: Find .py files while excluding specified directories.
    PATTERNS: Iterator (lazy file discovery).
    """

    def __init__(self, root_path: Path, exclude_dirs: Set[str]):
        """
        Initialize file finder.

        Args:
            root_path: Root directory to search
            exclude_dirs: Directory names to exclude
        """
        self.root_path = root_path
        self.exclude_dirs = exclude_dirs

    def find_files(self) -> Iterator[Path]:
        """
        Find all Python files in codebase.

        WHY: Generator pattern enables memory-efficient scanning.

        Yields:
            Path objects for Python files

        Example:
            >>> finder = PythonFileFinder(Path('src'), {'.venv', '__pycache__'})
            >>> for file in finder.find_files():
            ...     process(file)
        """
        for path in self.root_path.rglob('*.py'):
            # Guard clause - skip excluded directories
            if any(excluded in path.parts for excluded in self.exclude_dirs):
                continue

            yield path
