#!/usr/bin/env python3
"""
WHY: UI file analysis and detection logic
RESPONSIBILITY: Find and categorize UI-related files
PATTERNS: Strategy pattern for file type detection, List comprehensions

This module handles finding UI files and detecting their types.
"""

from pathlib import Path
from typing import List


class UIFileAnalyzer:
    """
    WHY: Centralized UI file analysis logic
    RESPONSIBILITY: Find and categorize UI files
    PATTERNS: Strategy pattern, Functional programming

    Benefits:
    - Clean file detection logic
    - Reusable file type detection
    - List comprehensions for efficiency
    """

    # UI file extensions to search for
    UI_EXTENSIONS = ['*.html', '*.css', '*.js', '*.jsx', '*.tsx', '*.vue', '*.svelte']

    @staticmethod
    def find_ui_files(impl_path: Path) -> List[Path]:
        """
        WHY: Find UI-related files using list comprehension (avoid nested for loops)
        RESPONSIBILITY: Locate all UI files in implementation directory
        PATTERNS: Functional programming - declarative over imperative

        PERFORMANCE: Single pass through extensions with generator expression.

        Args:
            impl_path: Path to implementation directory

        Returns:
            List of UI file paths
        """
        # Guard clause: path doesn't exist
        if not impl_path.exists():
            return []

        # Use list comprehension to flatten nested loop (avoid nested for loops)
        # This replaces: for ext in extensions: for file in path.rglob(ext)
        return [
            file_path
            for ext in UIFileAnalyzer.UI_EXTENSIONS
            for file_path in impl_path.rglob(ext)
        ]

    @staticmethod
    def detect_ui_file_type(file_path: str) -> str:
        """
        WHY: Detect UI file type from path using extension mapping
        RESPONSIBILITY: Map file extension to file type
        PATTERNS: Strategy pattern - use dictionary mapping instead of if/elif chain

        Args:
            file_path: Path to file

        Returns:
            File type string
        """
        # Map file extensions to types
        extension_map = [
            (('.html',), 'html'),
            (('.css',), 'css'),
            (('.js', '.jsx'), 'javascript'),
            (('.ts', '.tsx'), 'typescript'),
            (('.vue',), 'vue'),
            (('.svelte',), 'svelte'),
        ]

        # Return first matching type or 'unknown'
        return next(
            (file_type for extensions, file_type in extension_map if file_path.endswith(extensions)),
            'unknown'
        )
