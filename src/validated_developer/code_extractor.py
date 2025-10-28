#!/usr/bin/env python3
"""
Code Extractor Utility

WHY: LLM responses often contain markdown fences, explanations, and other
     non-code content. We need clean code extraction for validation.

RESPONSIBILITY:
- Extract code blocks from LLM responses
- Handle various markdown formats (```python, ```javascript, etc.)
- Clean and normalize code for validation

PATTERNS:
- Strategy Pattern: Different extraction strategies for different formats
- Guard Clauses: Early returns to avoid nested conditionals
"""

import re
from typing import Any, Dict


class CodeExtractor:
    """
    Extracts clean code from LLM responses.

    WHY: LLM responses contain markdown fences and explanations that must
         be removed before validation or execution.
    """

    # Supported language identifiers in markdown fences
    SUPPORTED_LANGUAGES = [
        'python', 'javascript', 'typescript', 'java', 'go',
        'rust', 'cpp', 'c', 'ruby', 'php', 'swift', 'kotlin'
    ]

    @staticmethod
    def extract_code_from_response(response: Any) -> str:
        """
        Extract code from LLM response (remove markdown fences).

        WHY: LLM responses need cleaning before validation/execution.

        WHAT: Tries multiple extraction strategies:
              1. Extract 'content' field if response is dict/object
              2. Find markdown code blocks with language identifiers
              3. Fall back to returning response as-is

        Args:
            response: LLM response (str, dict, or object with .content)

        Returns:
            Extracted code as string
        """
        # Guard: Extract content field if response is object/dict
        if hasattr(response, 'content'):
            response = response.content
        elif isinstance(response, dict) and 'content' in response:
            response = response['content']

        # Convert to string
        response = str(response)

        # Try to extract markdown code blocks
        code = CodeExtractor._extract_markdown_blocks(response)
        if code:
            return code

        # No code blocks found - return as-is
        return response.strip()

    @staticmethod
    def _extract_markdown_blocks(text: str) -> str:
        """
        Extract code from markdown code blocks.

        Args:
            text: Text that may contain markdown code blocks

        Returns:
            Extracted code or empty string if no blocks found
        """
        # Build pattern for all supported languages
        languages = '|'.join(CodeExtractor.SUPPORTED_LANGUAGES)
        pattern = rf'```(?:{languages})?\n(.*?)\n```'

        matches = re.findall(pattern, text, re.DOTALL)

        # Guard: No matches found
        if not matches:
            return ""

        # Return first code block (strip whitespace)
        return matches[0].strip()

    @staticmethod
    def extract_test_methods(test_code: str) -> list:
        """
        Extract method names from test code.

        WHY: Validation needs to check if implementation contains all methods
             referenced in tests.

        Args:
            test_code: Test code to analyze

        Returns:
            List of unique method names found in test code
        """
        # Find all function calls in test code
        method_calls = re.findall(r'(\w+)\s*\(', test_code)

        # Return unique method names
        return list(set(method_calls))
