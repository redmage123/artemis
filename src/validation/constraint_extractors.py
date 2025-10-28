#!/usr/bin/env python3
"""
WHY: Extract actionable constraints from validation failures for prompt refinement
RESPONSIBILITY: Provide category-specific constraint extraction strategies
PATTERNS: Strategy (extractor per category), Dispatch Table (category→extractor mapping)

Constraint extractors convert error messages into specific refinement guidance:
- MISSING_IMPORTS → "Include 'import django'"
- INCOMPLETE_IMPLEMENTATION → "No TODO/FIXME/pass statements"
- INCORRECT_SIGNATURE → "Include parameter 'user_id'"
"""

import re
from typing import List, Optional, Callable, Dict
from validation.models import FailureCategory


class ConstraintExtractors:
    """
    Extracts constraints from validation failures using Strategy pattern

    Each failure category has a specialized extraction strategy.
    """

    def __init__(self):
        """Initialize constraint extractors"""
        # Strategy pattern: Category → extractor function mapping
        self._extractors: Dict[FailureCategory, Callable] = {
            FailureCategory.MISSING_IMPORTS: self._extract_import_constraints,
            FailureCategory.INCOMPLETE_IMPLEMENTATION: self._extract_implementation_constraints,
            FailureCategory.INCORRECT_SIGNATURE: self._extract_signature_constraints,
            FailureCategory.MISSING_DOCSTRINGS: self._extract_docstring_constraints,
            FailureCategory.FORBIDDEN_PATTERNS: self._extract_forbidden_pattern_constraints,
        }

    def extract(
        self,
        category: FailureCategory,
        error_messages: List[str],
        code: Optional[str] = None
    ) -> List[str]:
        """
        Extract constraints for given category

        Args:
            category: Failure category
            error_messages: Error messages from validation
            code: Optional code that was validated

        Returns:
            List of actionable constraints for prompt refinement
        """
        # Get extractor for category (with default)
        extractor = self._extractors.get(
            category,
            lambda msgs, c: ["Fix validation errors"]  # Default extractor
        )

        return extractor(error_messages, code)

    def _extract_import_constraints(
        self,
        error_messages: List[str],
        code: Optional[str]
    ) -> List[str]:
        """
        Extract import-related constraints

        WHY: Missing imports are common hallucination - extract which imports to add.
        """
        constraints = []

        # Extract import names from error messages
        import_pattern = re.compile(r'import\s+(\w+)', re.IGNORECASE)

        for message in error_messages:
            matches = import_pattern.findall(message)
            for module in matches:
                constraints.append(f"Include 'import {module}' at the top of the file")

        # Default constraint if no specific imports found
        if not constraints:
            constraints.append("Add all necessary imports at the top of the file")

        return constraints

    def _extract_implementation_constraints(
        self,
        error_messages: List[str],
        code: Optional[str]
    ) -> List[str]:
        """Extract constraints for incomplete implementations"""
        return [
            "Implement all functions completely - no TODO, FIXME, or pass statements",
            "Provide full working implementation, not placeholders",
            "All methods must have complete logic, not just skeleton code"
        ]

    def _extract_signature_constraints(
        self,
        error_messages: List[str],
        code: Optional[str]
    ) -> List[str]:
        """Extract constraints for signature mismatches"""
        constraints = [
            "Ensure all function signatures match the requirements exactly",
            "Include all required parameters with correct names and types"
        ]

        # Extract specific parameter names if available
        param_pattern = re.compile(r'parameter[s]?\s+["\']?(\w+)["\']?', re.IGNORECASE)
        for message in error_messages:
            matches = param_pattern.findall(message)
            for param in matches:
                constraints.append(f"Include parameter '{param}' in function signature")

        return constraints

    def _extract_docstring_constraints(
        self,
        error_messages: List[str],
        code: Optional[str]
    ) -> List[str]:
        """Extract constraints for missing docstrings"""
        return [
            "Add docstrings to all classes and functions",
            "Include description, Args, Returns, and Example sections in docstrings"
        ]

    def _extract_forbidden_pattern_constraints(
        self,
        error_messages: List[str],
        code: Optional[str]
    ) -> List[str]:
        """Extract constraints for forbidden patterns"""
        return [
            "Do NOT use eval(), exec(), or os.system()",
            "Use safe alternatives instead of dangerous patterns",
            "Avoid dynamic code execution"
        ]


class CodeIssueExtractor:
    """
    Extracts specific code locations/patterns that caused failures

    WHY: Enables detailed analysis for supervisor learning.
    """

    def extract_issues(
        self,
        error_messages: List[str],
        code: Optional[str] = None
    ) -> List[Dict]:
        """
        Extract code issues from error messages

        Returns:
            List of issue dictionaries with location, pattern, message
        """
        issues = []

        for message in error_messages:
            issue = {
                'message': message,
                'pattern': self._extract_pattern_from_message(message),
                'location': None  # Could parse line numbers if available
            }
            issues.append(issue)

        return issues

    def _extract_pattern_from_message(self, message: str) -> Optional[str]:
        """
        Extract code pattern from error message

        WHY: Identifies specific problematic patterns for learning.
        """
        # Common patterns in error messages
        patterns = {
            'import': re.compile(r'import\s+\w+'),
            'function': re.compile(r'def\s+\w+'),
            'class': re.compile(r'class\s+\w+'),
        }

        for pattern_type, pattern in patterns.items():
            match = pattern.search(message)
            if match:
                return match.group(0)

        return None
