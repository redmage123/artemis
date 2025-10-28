#!/usr/bin/env python3
"""
WHY: Define the base validator interface for Chain of Responsibility pattern.

RESPONSIBILITY: Provide abstract base class and helper methods for all validators,
ensuring consistent validation interface and enabling extensibility.

PATTERNS:
- Abstract Base Class (ABC) for interface definition
- Template Method pattern for common validation flow
- Guard clauses for early validation
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional
from .models import ValidationContext


class BaseValidator(ABC):
    """
    WHY: Abstract base class for all validation stages.

    RESPONSIBILITY: Define common interface and shared helper methods
    for validators in the validation pipeline.

    Each validator implements validate() to return (checks, feedback, severity).
    """

    def __init__(self):
        """Initialize base validator."""
        self.name = self.__class__.__name__

    @abstractmethod
    def validate(self, code: str, context: Optional[ValidationContext]) -> Tuple[Dict[str, bool], List[str], str]:
        """
        WHY: Abstract validation method that all validators must implement.

        Args:
            code: Code to validate
            context: Optional validation context

        Returns:
            Tuple of (checks_dict, feedback_list, severity_string)
        """
        pass

    def _check_required_imports(self, code: str, required: List[str]) -> Tuple[Dict[str, bool], List[str]]:
        """
        WHY: Reusable helper to verify required imports are present.

        Args:
            code: Code to check
            required: List of required import strings

        Returns:
            Tuple of (checks_dict, feedback_list)
        """
        checks = {}
        feedback = []

        for req in required:
            has_req = req in code
            checks[f'has_{req}'] = has_req

            if not has_req:
                feedback.append(f"Missing required import: {req}")

        return checks, feedback

    def _check_has_imports(self, code: str, code_lines: List[str]) -> Tuple[Dict[str, bool], List[str]]:
        """
        WHY: Check if non-trivial code has import statements.

        Args:
            code: Full code string
            code_lines: Non-comment code lines

        Returns:
            Tuple of (checks_dict, feedback_list)
        """
        checks = {}
        feedback = []

        # Guard: Skip check for trivial code
        if len(code_lines) <= 5:
            return checks, feedback

        has_imports = any('import ' in line for line in code)
        checks['has_imports'] = has_imports

        if not has_imports:
            feedback.append("Code has no import statements - likely missing dependencies")

        return checks, feedback

    def _check_expected_methods(self, code: str, expected_methods: List[str]) -> Tuple[Dict[str, bool], List[str]]:
        """
        WHY: Verify expected framework methods are used.

        Args:
            code: Code to check
            expected_methods: List of expected method names

        Returns:
            Tuple of (checks_dict, feedback_list)
        """
        checks = {}
        feedback = []

        for method in expected_methods:
            has_method = method in code
            checks[f'uses_{method}'] = has_method

            if not has_method:
                feedback.append(f"Expected to use method: {method}")

        return checks, feedback

    def _is_dangerous_import(self, import_statement: str) -> bool:
        """
        WHY: Identify dangerous imports that pose security risks.

        Args:
            import_statement: Import statement to check

        Returns:
            True if import is dangerous
        """
        dangerous_patterns = [
            'from os import system',
            'import pickle',
            '__import__',
            'eval',
            'exec'
        ]

        return any(pattern in import_statement for pattern in dangerous_patterns)

    def _merge_results(self, *results: Tuple[Dict, List]) -> Tuple[Dict[str, bool], List[str]]:
        """
        WHY: Combine multiple validation check results.

        Args:
            *results: Variable number of (checks_dict, feedback_list) tuples

        Returns:
            Merged (checks_dict, feedback_list)
        """
        merged_checks = {}
        merged_feedback = []

        for checks, feedback in results:
            merged_checks.update(checks)
            merged_feedback.extend(feedback)

        return merged_checks, merged_feedback


class ValidatorHelper:
    """
    WHY: Static utility methods for validation tasks.

    RESPONSIBILITY: Provide common validation utilities that don't
    require instance state.
    """

    @staticmethod
    def parse_code_lines(code: str) -> Tuple[List[str], List[str]]:
        """
        WHY: Split code into all lines and non-comment lines.

        Args:
            code: Code to parse

        Returns:
            Tuple of (all_lines, code_lines_without_comments)
        """
        lines = [line.strip() for line in code.split('\n') if line.strip()]
        code_lines = [line for line in lines if not line.startswith('#')]

        return lines, code_lines

    @staticmethod
    def determine_severity(checks: Dict[str, bool], critical_keys: Optional[List[str]] = None) -> str:
        """
        WHY: Calculate overall severity based on failed checks.

        Args:
            checks: Dictionary of check results
            critical_keys: List of check keys that indicate critical failures

        Returns:
            Severity string: 'critical', 'high', 'medium', or 'low'
        """
        # Guard: No critical keys specified
        if not critical_keys:
            critical_keys = ['parseable', 'compiles', 'syntax_valid']

        # Check for critical failures
        for key in critical_keys:
            if key in checks and not checks[key]:
                return "critical"

        # Check for any failures
        has_failures = any(not passed for passed in checks.values())

        if has_failures:
            return "high"

        return "medium"

    @staticmethod
    def count_code_lines(code: str) -> int:
        """
        WHY: Count non-empty, non-comment lines of code.

        Args:
            code: Code to count

        Returns:
            Number of code lines
        """
        lines = code.split('\n')
        code_lines = [line.strip() for line in lines if line.strip() and not line.strip().startswith('#')]

        return len(code_lines)
