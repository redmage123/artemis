#!/usr/bin/env python3
"""
WHY: Infer programming language from file extensions for code review context
RESPONSIBILITY: Map file extensions to language identifiers using dispatch table
PATTERNS: Strategy (detection algorithm), Dispatch Table (O(1) lookup)

Language detection enables:
- Syntax-aware code review
- Language-specific linting rules
- Targeted security analysis
- Better formatting in review output
"""

from typing import Dict
from pathlib import Path


class LanguageDetector:
    """
    Detects programming language from file extension

    Uses dispatch table for O(1) lookup performance.
    """

    # Dispatch table: file extension -> language identifier
    # Pattern: Dispatch Table for constant-time lookups
    EXTENSION_TO_LANGUAGE: Dict[str, str] = {
        '.py': 'python',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.html': 'html',
        '.css': 'css',
        '.java': 'java',
        '.go': 'go',
        '.rb': 'ruby',
        '.rs': 'rust',
        '.cpp': 'cpp',
        '.c': 'c',
        '.h': 'c',
        '.sh': 'bash',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.json': 'json',
        '.md': 'markdown',
        '.sql': 'sql',
        '.kt': 'kotlin',
        '.swift': 'swift',
        '.php': 'php',
        '.scala': 'scala',
        '.r': 'r',
        '.pl': 'perl'
    }

    def detect_from_path(self, file_path: str) -> str:
        """
        Detect language from file path

        Args:
            file_path: Path to the file (relative or absolute)

        Returns:
            Language identifier (e.g., 'python', 'javascript') or empty string
        """
        # Guard clause - validate path
        if not file_path:
            return ''

        # Extract extension
        ext = Path(file_path).suffix.lower()

        # Guard clause - check if extension exists
        if not ext:
            return ''

        # Dispatch table lookup - O(1)
        return self.EXTENSION_TO_LANGUAGE.get(ext, '')

    def detect_from_extension(self, extension: str) -> str:
        """
        Detect language from file extension

        Args:
            extension: File extension (with or without leading dot)

        Returns:
            Language identifier or empty string
        """
        # Guard clause - validate extension
        if not extension:
            return ''

        # Normalize extension (ensure leading dot)
        normalized_ext = extension if extension.startswith('.') else f'.{extension}'
        normalized_ext = normalized_ext.lower()

        # Dispatch table lookup - O(1)
        return self.EXTENSION_TO_LANGUAGE.get(normalized_ext, '')

    def get_supported_extensions(self) -> list[str]:
        """
        Get list of supported file extensions

        Returns:
            List of supported extensions
        """
        return list(self.EXTENSION_TO_LANGUAGE.keys())

    def get_supported_languages(self) -> list[str]:
        """
        Get list of supported languages

        Returns:
            List of unique language identifiers
        """
        return list(set(self.EXTENSION_TO_LANGUAGE.values()))
