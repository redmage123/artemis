#!/usr/bin/env python3
"""
Module: services.core.html_validator

WHY: Catches malformed HTML early before it causes runtime errors in browsers
     or deployment pipelines. Provides consistent validation across all HTML assets.

RESPONSIBILITY: Validate HTML file syntax and structure using BeautifulSoup parser.

PATTERNS:
- Single Responsibility: Only validates HTML syntax and structure
- Strategy Pattern: Can be extended with different validators (W3C, tidy, etc.)
- Interface Segregation: Implements ValidatorInterface for loose coupling
- Fail-Fast: Returns on first parsing error to avoid cascading failures

DESIGN DECISIONS:
- BeautifulSoup parser (lenient but catches serious syntax issues)
- Returns standardized dict format (consistent with other validators)
- Exception handling wraps parsing errors (detailed error reporting)
- Uses context manager for file I/O (automatic resource cleanup)

Dependencies: core.interfaces
"""

from pathlib import Path
from typing import Dict, Optional

from bs4 import BeautifulSoup

from core.interfaces import ValidatorInterface


class HTMLValidator(ValidatorInterface):
    """
    HTML syntax and structure validation service.

    WHAT: Validates HTML files for syntax errors using BeautifulSoup parser.
    WHY: BeautifulSoup is lenient but will catch serious syntax issues that
         would cause problems in production.

    Attributes:
        parser: HTML parser to use (default: 'html.parser')
        strict: Whether to use strict validation mode

    Example:
        >>> validator = HTMLValidator()
        >>> result = validator.validate(Path("index.html"))
        >>> if result['status'] == 'PASS':
        ...     print("HTML is valid!")
    """

    # Parser options (dispatch table pattern)
    PARSER_OPTIONS: Dict[str, str] = {
        'html': 'html.parser',
        'lxml': 'lxml',
        'xml': 'xml',
        'html5': 'html5lib'
    }

    # Status constants
    STATUS_PASS: str = "PASS"
    STATUS_FAIL: str = "FAIL"

    def __init__(self, parser: str = 'html.parser', strict: bool = False) -> None:
        """
        Initialize HTML validator.

        Args:
            parser: Parser to use ('html.parser', 'lxml', 'xml', 'html5lib')
            strict: Enable strict validation mode (default: False)

        WHY: Different parsers have different trade-offs (speed vs strictness).
             html.parser is built-in and sufficient for most cases.

        Raises:
            ValueError: If parser not supported
        """
        # Guard clause: Validate parser choice
        if parser not in self.PARSER_OPTIONS.values():
            raise ValueError(
                f"Unsupported parser: {parser}. "
                f"Choose from: {list(self.PARSER_OPTIONS.values())}"
            )

        self.parser: str = parser
        self.strict: bool = strict

    def validate(self, file_path: Path) -> Dict:
        """
        Validate HTML file syntax using BeautifulSoup.

        WHAT: Attempts to parse HTML file and reports any parsing errors.
        WHY: BeautifulSoup's parser is forgiving but will fail on severely
             malformed HTML. Returns standardized result format.

        Args:
            file_path: Path to HTML file to validate

        Returns:
            Dict containing:
                - status: "PASS" or "FAIL"
                - errors: Number of errors found (0 or 1)
                - note: Human-readable message
                - file_path: Path to validated file (optional)

        Example:
            >>> result = validator.validate(Path("page.html"))
            >>> print(f"{result['status']}: {result['note']}")
            PASS: HTML is valid and parseable
        """
        # Guard clause: Validate file path
        if not file_path.exists():
            return self._create_result(
                status=self.STATUS_FAIL,
                errors=1,
                note=f"File not found: {file_path}",
                file_path=file_path
            )

        # Guard clause: Validate file is HTML
        if not self._is_html_file(file_path):
            return self._create_result(
                status=self.STATUS_FAIL,
                errors=1,
                note=f"Not an HTML file: {file_path.suffix}",
                file_path=file_path
            )

        # Attempt to parse HTML
        try:
            html_content = self._read_html_file(file_path)
            soup = self._parse_html(html_content)

            # Optional: Strict validation checks
            if self.strict:
                return self._strict_validation(soup, file_path)

            # Basic validation passed
            return self._create_result(
                status=self.STATUS_PASS,
                errors=0,
                note="HTML is valid and parseable",
                file_path=file_path
            )

        except UnicodeDecodeError as e:
            return self._create_result(
                status=self.STATUS_FAIL,
                errors=1,
                note=f"Encoding error: {str(e)}",
                file_path=file_path
            )

        except Exception as e:
            return self._create_result(
                status=self.STATUS_FAIL,
                errors=1,
                note=f"Parsing error: {str(e)}",
                file_path=file_path
            )

    def _is_html_file(self, file_path: Path) -> bool:
        """
        Check if file is HTML based on extension.

        Args:
            file_path: Path to check

        Returns:
            True if file has HTML extension

        WHY: Quick guard clause to prevent processing non-HTML files.
        """
        return file_path.suffix.lower() in {'.html', '.htm'}

    def _read_html_file(self, file_path: Path) -> str:
        """
        Read HTML file content with proper encoding.

        Args:
            file_path: Path to HTML file

        Returns:
            File content as string

        WHY: Centralizes file reading with consistent encoding handling.
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def _parse_html(self, html_content: str) -> BeautifulSoup:
        """
        Parse HTML content using configured parser.

        Args:
            html_content: HTML string to parse

        Returns:
            BeautifulSoup object

        WHY: Separates parsing logic for easier testing and mocking.
        """
        return BeautifulSoup(html_content, self.parser)

    def _strict_validation(self, soup: BeautifulSoup, file_path: Path) -> Dict:
        """
        Perform strict validation checks on parsed HTML.

        Args:
            soup: Parsed HTML document
            file_path: Original file path

        Returns:
            Validation result dict

        WHY: Additional checks for production-ready HTML (doctype, lang, etc).
        """
        errors = []

        # Check for doctype
        if not soup.contents or str(soup.contents[0]).strip().lower() != '<!doctype html>':
            errors.append("Missing or invalid DOCTYPE")

        # Check for html tag
        if not soup.html:
            errors.append("Missing <html> tag")

        # Check for lang attribute
        if soup.html and not soup.html.get('lang'):
            errors.append("Missing lang attribute on <html> tag")

        # Check for head and body
        if not soup.head:
            errors.append("Missing <head> tag")

        if not soup.body:
            errors.append("Missing <body> tag")

        # Return result based on errors found
        if errors:
            return self._create_result(
                status=self.STATUS_FAIL,
                errors=len(errors),
                note=f"Strict validation failed: {'; '.join(errors)}",
                file_path=file_path
            )

        return self._create_result(
            status=self.STATUS_PASS,
            errors=0,
            note="HTML passed strict validation",
            file_path=file_path
        )

    def _create_result(
        self,
        status: str,
        errors: int,
        note: str,
        file_path: Optional[Path] = None
    ) -> Dict:
        """
        Create standardized validation result dictionary.

        Args:
            status: "PASS" or "FAIL"
            errors: Number of errors found
            note: Human-readable description
            file_path: Optional path to validated file

        Returns:
            Standardized result dict

        WHY: Ensures all validators return consistent result format.
        PATTERN: Factory method for result objects
        """
        result = {
            "status": status,
            "errors": errors,
            "note": note
        }

        if file_path:
            result["file_path"] = str(file_path)

        return result


# Service factory function for dependency injection
def create_html_validator(
    parser: str = 'html.parser',
    strict: bool = False
) -> HTMLValidator:
    """
    Factory function to create HTMLValidator instance.

    WHY: Enables dependency injection and easier testing/mocking.
    PATTERN: Factory Method pattern

    Args:
        parser: HTML parser to use
        strict: Enable strict validation mode

    Returns:
        Configured HTMLValidator instance

    Example:
        >>> validator = create_html_validator(strict=True)
    """
    return HTMLValidator(parser=parser, strict=strict)


__all__ = ["HTMLValidator", "create_html_validator"]
