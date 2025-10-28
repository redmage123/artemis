#!/usr/bin/env python3
"""
Module: output_formatter.py

WHY: Formats and sanitizes output paths for notebook files.
     Handles filename generation and path validation.

RESPONSIBILITY:
- Generate safe filenames from card titles
- Sanitize filenames (remove special characters)
- Ensure unique filenames to prevent overwrites
- Construct valid output paths
- Format stage results for pipeline

PATTERNS:
- Guard Clauses: Early returns for invalid inputs
- Single Responsibility: Only handles path/filename formatting
- Pure Functions: Stateless transformations
"""

from typing import Dict, Any, Optional
from pathlib import Path
import re


class OutputFormatter:
    """
    Format notebook output paths and filenames

    WHY: Centralizes path/filename formatting logic
    RESPONSIBILITY: Generate safe, valid notebook file paths
    """

    # Characters allowed in filenames
    SAFE_CHARS_PATTERN = re.compile(r'[^a-zA-Z0-9_\-\s]')

    # Maximum filename length (excluding extension)
    MAX_FILENAME_LENGTH: int = 200

    def format_filename(
        self,
        title: str,
        extension: str = '.ipynb',
        suffix: Optional[str] = None
    ) -> str:
        """
        Format safe filename from title

        Time Complexity: O(n) where n = title length
        Space Complexity: O(n) for string operations

        Args:
            title: Original title text
            extension: File extension (default: .ipynb)
            suffix: Optional suffix to add before extension

        Returns:
            Safe filename string
        """
        # Guard clause: empty title
        if not title:
            title = 'notebook'

        # Guard clause: not a string
        if not isinstance(title, str):
            title = str(title)

        # Remove special characters
        safe_title = self._sanitize_filename(title)

        # Replace spaces with underscores
        safe_title = safe_title.replace(' ', '_')

        # Remove duplicate underscores
        safe_title = re.sub(r'_+', '_', safe_title)

        # Remove leading/trailing underscores
        safe_title = safe_title.strip('_')

        # Convert to lowercase
        safe_title = safe_title.lower()

        # Guard clause: empty after sanitization
        if not safe_title:
            safe_title = 'notebook'

        # Truncate if too long
        safe_title = self._truncate_filename(safe_title)

        # Add suffix if provided
        if suffix:
            safe_title = f"{safe_title}_{suffix}"

        # Add extension
        return f"{safe_title}{extension}"

    def _sanitize_filename(self, filename: str) -> str:
        """
        Remove unsafe characters from filename

        Time Complexity: O(n) where n = filename length
        Space Complexity: O(n) for new string

        Args:
            filename: Original filename

        Returns:
            Sanitized filename with only safe characters
        """
        # Replace unsafe characters with underscores
        return self.SAFE_CHARS_PATTERN.sub('_', filename)

    def _truncate_filename(self, filename: str) -> str:
        """
        Truncate filename to maximum length

        Time Complexity: O(1) slicing operation
        Space Complexity: O(n) for new string

        Args:
            filename: Filename to truncate

        Returns:
            Truncated filename
        """
        # Guard clause: within limit
        if len(filename) <= self.MAX_FILENAME_LENGTH:
            return filename

        return filename[:self.MAX_FILENAME_LENGTH]

    def format_output_path(
        self,
        output_dir: Path,
        filename: str
    ) -> Path:
        """
        Format complete output path for notebook

        Time Complexity: O(1) path operations
        Space Complexity: O(1) path object

        Args:
            output_dir: Output directory path
            filename: Notebook filename

        Returns:
            Complete output path
        """
        # Guard clause: ensure directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        return output_dir / filename

    def ensure_unique_path(
        self,
        path: Path,
        max_attempts: int = 1000
    ) -> Path:
        """
        Ensure path is unique by adding numeric suffix if needed

        Time Complexity: O(n) where n = number of existing files
        Space Complexity: O(1) constant space

        Args:
            path: Desired output path
            max_attempts: Maximum number of attempts to find unique name

        Returns:
            Unique path (may have numeric suffix)
        """
        # Guard clause: path doesn't exist
        if not path.exists():
            return path

        # Try adding numeric suffixes
        stem = path.stem
        suffix = path.suffix
        parent = path.parent

        for i in range(1, max_attempts):
            new_path = parent / f"{stem}_{i}{suffix}"
            if not new_path.exists():
                return new_path

        # If all attempts exhausted, append timestamp
        import time
        timestamp = int(time.time())
        return parent / f"{stem}_{timestamp}{suffix}"

    def format_stage_result(
        self,
        notebook_path: Path,
        notebook_type: str,
        status: str = 'success',
        additional_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Format stage execution result

        Time Complexity: O(1) dict operations
        Space Complexity: O(1) constant space

        Args:
            notebook_path: Path to generated notebook
            notebook_type: Type of notebook generated
            status: Execution status (success/failure)
            additional_data: Optional additional result data

        Returns:
            Formatted result dictionary
        """
        result = {
            'stage': 'notebook_generation',
            'status': status,
            'notebook_path': str(notebook_path),
            'notebook_type': notebook_type,
            'message': f'Generated {notebook_type} notebook'
        }

        # Merge additional data if provided
        if additional_data:
            result.update(additional_data)

        return result

    def format_error_result(
        self,
        error: Exception,
        card_id: str = 'unknown',
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Format error result for stage failure

        Time Complexity: O(1) dict operations
        Space Complexity: O(1) constant space

        Args:
            error: Exception that occurred
            card_id: Card ID being processed
            additional_context: Optional additional error context

        Returns:
            Formatted error result dictionary
        """
        result = {
            'stage': 'notebook_generation',
            'status': 'failed',
            'error': str(error),
            'error_type': type(error).__name__,
            'card_id': card_id
        }

        # Merge additional context if provided
        if additional_context:
            result.update(additional_context)

        return result

    def format_messenger_data(
        self,
        notebook_path: Path,
        notebook_type: str,
        card_id: str
    ) -> Dict[str, Any]:
        """
        Format data for agent messenger communication

        Time Complexity: O(1) dict operations
        Space Complexity: O(1) constant space

        Args:
            notebook_path: Path to notebook
            notebook_type: Type of notebook
            card_id: Card ID

        Returns:
            Formatted messenger data
        """
        return {
            'notebook_path': str(notebook_path),
            'notebook_type': notebook_type,
            'card_id': card_id,
            'stage': 'notebook_generation'
        }

    def validate_filename(self, filename: str) -> bool:
        """
        Validate filename is safe and valid

        Time Complexity: O(n) where n = filename length
        Space Complexity: O(1) constant space

        Args:
            filename: Filename to validate

        Returns:
            True if valid, False otherwise
        """
        # Guard clause: empty filename
        if not filename:
            return False

        # Guard clause: too long
        if len(filename) > self.MAX_FILENAME_LENGTH + 10:  # +10 for extension
            return False

        # Check for path separators (security check)
        if '/' in filename or '\\' in filename:
            return False

        # Check for null bytes (security check)
        if '\0' in filename:
            return False

        return True
