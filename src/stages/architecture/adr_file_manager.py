#!/usr/bin/env python3
"""
ADR File Manager

WHY: Manages ADR file naming, numbering, and path operations
RESPONSIBILITY: Handle all file-system operations related to ADRs
PATTERNS: Single Responsibility, Guard Clauses
"""

import re
from pathlib import Path
from typing import List, Optional


class ADRFileManager:
    """
    Manages ADR file naming, numbering, and directory operations.

    WHY: Separate file operations from business logic
    RESPONSIBILITY: ADR file system management only
    PATTERNS: Single Responsibility, Guard Clauses
    """

    def __init__(self, adr_dir: Path):
        """
        Initialize ADR file manager.

        Args:
            adr_dir: Directory where ADRs are stored
        """
        self.adr_dir = adr_dir
        self.adr_dir.mkdir(exist_ok=True, parents=True)

    def get_next_adr_number(self) -> str:
        """
        Get next available ADR number.

        Returns:
            Zero-padded ADR number (e.g., "001")

        WHY: Ensures sequential ADR numbering
        PATTERN: Guard clause for empty directory
        """
        existing_adrs = list(self.adr_dir.glob("ADR-*.md"))
        if not existing_adrs:
            return "001"

        numbers = self._extract_adr_numbers(existing_adrs)
        next_num = max(numbers) + 1 if numbers else 1
        return f"{next_num:03d}"

    def create_adr_filename(self, title: str, adr_number: str) -> str:
        """
        Create ADR filename from title.

        Args:
            title: Task title
            adr_number: ADR number (e.g., "001")

        Returns:
            Sanitized filename (e.g., "ADR-001-implement-auth.md")

        WHY: Consistent, safe filenames across platforms
        PATTERN: Guard clause pattern for sanitization
        """
        if not title:
            return f"ADR-{adr_number}-untitled.md"

        # Sanitize title to remove file paths and invalid characters
        slug = re.sub(r'[^a-zA-Z0-9\s-]', '', title)  # Remove invalid chars
        slug = slug.lower().replace(' ', '-')[:50]  # Convert to kebab-case
        slug = re.sub(r'-+', '-', slug).strip('-')  # Normalize multiple dashes

        if not slug:
            return f"ADR-{adr_number}-untitled.md"

        return f"ADR-{adr_number}-{slug}.md"

    def get_adr_path(self, filename: str) -> Path:
        """
        Get full path for ADR file.

        Args:
            filename: ADR filename

        Returns:
            Full path to ADR file
        """
        return self.adr_dir / filename

    def _extract_adr_numbers(self, adr_files: List[Path]) -> List[int]:
        """
        Extract ADR numbers from file list.

        Args:
            adr_files: List of ADR file paths

        Returns:
            List of extracted ADR numbers

        WHY: Helper for finding next ADR number
        PATTERN: List comprehension with guard clause
        """
        return [
            num for num in
            (self._extract_single_adr_number(f) for f in adr_files)
            if num is not None
        ]

    def _extract_single_adr_number(self, adr_file: Path) -> Optional[int]:
        """
        Extract ADR number from single file.

        Args:
            adr_file: Path to ADR file

        Returns:
            ADR number if found, None otherwise

        WHY: Parse ADR number from filename
        PATTERN: Guard clause for regex match
        """
        match = re.search(r'ADR-(\d+)', adr_file.name)
        if not match:
            return None

        return int(match.group(1))
