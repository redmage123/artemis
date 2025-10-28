#!/usr/bin/env python3
"""
Repository for accessing and querying coding standards.

WHY: Provides a clean API for retrieving coding standards by language or category.

RESPONSIBILITY:
    - Query and filter coding standards by language
    - Validate language support
    - Provide access to complete standards text

PATTERNS:
    - Repository pattern for data access abstraction
    - Guard clauses for input validation (max 1 level nesting)
    - Pure functions for filtering logic
"""

from typing import Optional

from .constants import CODING_STANDARDS_ALL_LANGUAGES, SUPPORTED_LANGUAGES


class RulesRepository:
    """
    Repository for accessing coding standards and rules.

    WHY: Centralizes all access to coding standards, provides clean query API.
    RESPONSIBILITY: Query, filter, and retrieve coding standards by language.
    PATTERNS: Repository pattern, guard clauses, immutable data access.

    Example:
        repo = RulesRepository()
        all_standards = repo.get_all_standards()
        python_standards = repo.get_standards_for_language('python')
    """

    def __init__(self) -> None:
        """
        Initialize the rules repository.

        WHY: Sets up access to immutable standards text.
        PERFORMANCE: No computation on init, just reference storage.
        """
        self._standards_text = CODING_STANDARDS_ALL_LANGUAGES

    def get_all_standards(self) -> str:
        """
        Retrieve the complete coding standards text.

        WHY: Provides access to the full standards document.
        PERFORMANCE: O(1) - returns reference to constant string.

        Returns:
            Complete standards as a formatted string

        Example:
            standards = repo.get_all_standards()
            print(standards)
        """
        return self._standards_text

    def get_standards_for_language(self, language: str) -> str:
        """
        Extract standards relevant to a specific language.

        WHY: Filters standards to show only language-specific content.
        PERFORMANCE: O(n) where n is number of lines in standards text.
        Uses guard clauses to avoid nested ifs.

        Args:
            language: Programming language name (case-insensitive)

        Returns:
            Language-specific standards as string. If language not found,
            returns message indicating no standards found.

        Example:
            python_standards = repo.get_standards_for_language('python')
            java_standards = repo.get_standards_for_language('Java')

        Note:
            Language matching is case-insensitive.
        """
        # Guard clause: empty language
        if not language:
            return ""

        # Guard clause: unsupported language
        if not self._is_language_supported(language.lower()):
            return f"# No specific standards found for {language}"

        # Extract language-specific section
        return self._extract_language_section(language)

    def _extract_language_section(self, language: str) -> str:
        """
        Extract the section for a specific language from standards text.

        WHY: Separates extraction logic for testability and clarity.
        PERFORMANCE: O(n) single pass through lines.
        Uses guard clauses to avoid nested ifs.

        Args:
            language: Programming language name

        Returns:
            Extracted language section or "not found" message
        """
        lines = self._standards_text.split('\n')
        result_lines = []
        in_language_section = False
        lang_lower = language.lower()

        for line in lines:
            # Check if this is the start of the language-specific section
            if line.upper().startswith(lang_lower.upper() + ':'):
                in_language_section = True
                result_lines.append(line)
                continue

            # Guard clause: not in target section yet
            if not in_language_section:
                continue

            # Check if we've moved to a different language section
            # Guard clause: exit if we hit another major section
            if self._is_new_section(line):
                break

            result_lines.append(line)

        # Guard clause: no content found
        if not result_lines:
            return f"# No specific standards found for {language}"

        return '\n'.join(result_lines)

    def _is_new_section(self, line: str) -> bool:
        """
        Determine if a line marks the start of a new language section.

        WHY: Extracts section detection logic for clarity and testability.
        PERFORMANCE: O(1) - simple string checks.

        Args:
            line: Line of text to check

        Returns:
            True if line starts a new major section
        """
        # Guard clause: empty line
        if not line:
            return False

        # Guard clause: indented lines are not new sections
        if line.startswith('  ') or line.startswith('-'):
            return False

        # Check for uppercase start and colon (language section pattern)
        return line and line[0].isupper() and ':' in line

    def _is_language_supported(self, language: str) -> bool:
        """
        Check if a language is in the supported list.

        WHY: Validates language before attempting to extract standards.
        PERFORMANCE: O(1) average case (set lookup internally).

        Args:
            language: Language name to check (should be lowercase)

        Returns:
            True if language is supported

        Example:
            if repo._is_language_supported('python'):
                # Extract python standards
        """
        return language.lower() in SUPPORTED_LANGUAGES

    def is_language_supported(self, language: str) -> bool:
        """
        Public API to check if a language is supported.

        WHY: Allows clients to check support before querying.
        PERFORMANCE: O(1) average case.

        Args:
            language: Language name to check (case-insensitive)

        Returns:
            True if language is supported

        Example:
            if repo.is_language_supported('Python'):
                standards = repo.get_standards_for_language('Python')
        """
        # Guard clause: empty language
        if not language:
            return False

        return self._is_language_supported(language.lower())

    def get_supported_languages(self) -> list[str]:
        """
        Get list of all supported languages.

        WHY: Provides discovery of available languages.
        PERFORMANCE: O(1) - returns reference to constant list.

        Returns:
            List of supported language names

        Example:
            languages = repo.get_supported_languages()
            print(f"Supported languages: {', '.join(languages)}")
        """
        return list(SUPPORTED_LANGUAGES)


# Singleton instance for convenient access
rules_repository = RulesRepository()
