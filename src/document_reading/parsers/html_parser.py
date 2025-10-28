#!/usr/bin/env python3
"""
WHY: HTML document parsing with BeautifulSoup.
RESPONSIBILITY: Extract clean text from HTML files, removing scripts and styles.
PATTERNS: Strategy pattern for fallback handling, Guard clauses for library detection.
"""

from typing import Optional
from artemis_exceptions import DocumentReadError


class HTMLParser:
    """
    WHY: Parse HTML files and extract clean text content.
    RESPONSIBILITY: Remove HTML tags, scripts, and styles to get readable text.
    """

    def __init__(self, verbose: bool = False):
        """
        WHY: Initialize parser with library detection.
        RESPONSIBILITY: Check if BeautifulSoup is available.

        Args:
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        self.has_bs4 = self._detect_beautifulsoup()

    def _detect_beautifulsoup(self) -> bool:
        """
        WHY: Check if BeautifulSoup library is available.
        RESPONSIBILITY: Return True if bs4 can be imported.

        Returns:
            True if BeautifulSoup is available
        """
        try:
            from bs4 import BeautifulSoup
            return True
        except ImportError:
            if self.verbose:
                print("[HTMLParser] BeautifulSoup not available. Reading raw HTML. Install: pip install beautifulsoup4")
            return False

    def is_available(self) -> bool:
        """
        WHY: Check if HTML parsing is available.
        RESPONSIBILITY: Return availability status (always True, fallback to raw read).

        Returns:
            True (HTML parsing always works, with or without BeautifulSoup)
        """
        return True

    def parse(self, file_path: str) -> str:
        """
        WHY: Parse HTML file and extract text.
        RESPONSIBILITY: Use BeautifulSoup if available, otherwise read raw HTML.

        Args:
            file_path: Path to HTML file

        Returns:
            Extracted text content

        Raises:
            DocumentReadError: If file cannot be read
        """
        # Guard: Use BeautifulSoup if available
        if self.has_bs4:
            return self._parse_with_beautifulsoup(file_path)

        # Fallback: Read raw HTML
        return self._parse_raw(file_path)

    def _parse_with_beautifulsoup(self, file_path: str) -> str:
        """
        WHY: Parse HTML using BeautifulSoup for clean text extraction.
        RESPONSIBILITY: Remove scripts/styles and extract readable text.

        Args:
            file_path: Path to HTML file

        Returns:
            Clean text without HTML tags
        """
        from bs4 import BeautifulSoup

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()

            soup = BeautifulSoup(html_content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Get text
            text = soup.get_text()

            # Break into lines and remove leading/trailing space
            lines = (line.strip() for line in text.splitlines())

            # Drop blank lines and collapse multiple spaces
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)

            return text

        except Exception as e:
            raise DocumentReadError(
                f"Error parsing HTML with BeautifulSoup: {str(e)}",
                context={"file_path": file_path},
                original_exception=e
            )

    def _parse_raw(self, file_path: str) -> str:
        """
        WHY: Fallback to reading raw HTML without parsing.
        RESPONSIBILITY: Read HTML file as plain text.

        Args:
            file_path: Path to HTML file

        Returns:
            Raw HTML content
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise DocumentReadError(
                f"Error reading HTML file: {str(e)}",
                context={"file_path": file_path},
                original_exception=e
            )
