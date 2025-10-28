#!/usr/bin/env python3
"""
WHY: Markdown file parsing (currently delegates to text parser).
RESPONSIBILITY: Parse markdown files, with potential for future enhancement.
PATTERNS: Delegation pattern - currently delegates to TextParser but provides extension point.
"""

from document_reading.parsers.text_parser import TextParser
from artemis_exceptions import DocumentReadError


class MarkdownParser:
    """
    WHY: Dedicated markdown parser for future extensibility.
    RESPONSIBILITY: Parse markdown files (currently as plain text, extensible for future features).

    FUTURE: Could add markdown-specific features:
    - Parse headings into structured sections
    - Extract code blocks separately
    - Build table of contents
    - Convert to HTML or other formats
    """

    @staticmethod
    def parse(file_path: str) -> str:
        """
        WHY: Parse markdown file as text.
        RESPONSIBILITY: Extract markdown content (currently as plain text).

        Args:
            file_path: Path to markdown file

        Returns:
            Markdown content as text

        Raises:
            DocumentReadError: If file cannot be read
        """
        # Currently delegates to text parser
        # Future: Add markdown-specific parsing here
        return TextParser.parse(file_path)

    @staticmethod
    def is_available() -> bool:
        """
        WHY: Check if markdown parsing is available.
        RESPONSIBILITY: Return availability status.

        Returns:
            True (markdown parsing is always available)
        """
        return True
