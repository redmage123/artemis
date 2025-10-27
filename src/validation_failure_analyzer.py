#!/usr/bin/env python3
"""
Validation Failure Analyzer (Layer 4: Retry with Refinement)

WHY: Analyzes validation failures to enable intelligent prompt refinement.
     Categorizes failures by type (missing imports, incomplete code, etc.)
     Extracts actionable insights for retry attempts.

RESPONSIBILITY: ONLY failure analysis - no validation or retry logic.
PATTERNS: Strategy pattern for failure categorization (no if/elif chains).

Example:
    analyzer = ValidationFailureAnalyzer()
    failures = analyzer.analyze_failures(validation_results)
    print(failures.category)  # 'missing_imports'
    print(failures.constraints)  # ['Add import django', 'Add import requests']
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import re

from artemis_stage_interface import LoggerInterface
from artemis_exceptions import ValidationError, create_wrapped_exception


class FailureCategory(Enum):
    """
    Categories of validation failures.

    WHY: Enables targeted prompt refinement strategies.
         Each category requires different refinement approach.
    """
    MISSING_IMPORTS = "missing_imports"
    INCOMPLETE_IMPLEMENTATION = "incomplete_implementation"
    INCORRECT_SIGNATURE = "incorrect_signature"
    MISSING_DOCSTRINGS = "missing_docstrings"
    FORBIDDEN_PATTERNS = "forbidden_patterns"
    TEST_FAILURES = "test_failures"
    RAG_MISMATCH = "rag_mismatch"
    STREAMING_STOPPED = "streaming_stopped"
    UNKNOWN = "unknown"


@dataclass
class FailureAnalysis:
    """
    Result of failure analysis.

    Attributes:
        category: Primary failure category
        constraints: List of specific constraints to add to prompt
        code_issues: Specific code locations/patterns that failed
        severity: How severe the failure is (0.0-1.0)
        retry_recommended: Whether retry with refinement is recommended
    """
    category: FailureCategory
    constraints: List[str] = field(default_factory=list)
    code_issues: List[Dict] = field(default_factory=list)
    severity: float = 0.5
    retry_recommended: bool = True

    def __post_init__(self):
        """Validate severity is in range."""
        if not 0.0 <= self.severity <= 1.0:
            self.severity = max(0.0, min(1.0, self.severity))


class ValidationFailureAnalyzer:
    """
    Analyzes validation failures to extract actionable refinement constraints.

    WHY: Validation failures contain patterns that can guide prompt refinement.
         Example: "import django missing" → constraint: "Include 'import django'"

    RESPONSIBILITY: ONLY analyze failures - no validation or retry logic.
    PATTERNS: Strategy pattern for categorization (dictionary mapping).
    PERFORMANCE: Compiled regex patterns, early returns, O(n) analysis.
    """

    # Strategy pattern: Failure pattern → Category mapping (no if/elif)
    FAILURE_PATTERNS = {
        r'import.*not found': FailureCategory.MISSING_IMPORTS,
        r'missing import': FailureCategory.MISSING_IMPORTS,
        r'TODO|FIXME|pass\s*$': FailureCategory.INCOMPLETE_IMPLEMENTATION,
        r'NotImplementedError': FailureCategory.INCOMPLETE_IMPLEMENTATION,
        r'signature.*mismatch': FailureCategory.INCORRECT_SIGNATURE,
        r'missing.*parameter': FailureCategory.INCORRECT_SIGNATURE,
        r'missing.*docstring': FailureCategory.MISSING_DOCSTRINGS,
        r'eval\(|exec\(': FailureCategory.FORBIDDEN_PATTERNS,
        r'test.*failed': FailureCategory.TEST_FAILURES,
        r'similarity.*low': FailureCategory.RAG_MISMATCH,
        r'streaming.*stopped': FailureCategory.STREAMING_STOPPED,
    }

    # Severity scores for each category (Strategy pattern)
    CATEGORY_SEVERITY = {
        FailureCategory.FORBIDDEN_PATTERNS: 1.0,  # Critical
        FailureCategory.STREAMING_STOPPED: 0.9,   # Very high
        FailureCategory.MISSING_IMPORTS: 0.7,     # High
        FailureCategory.INCORRECT_SIGNATURE: 0.7, # High
        FailureCategory.INCOMPLETE_IMPLEMENTATION: 0.6,  # Medium-high
        FailureCategory.TEST_FAILURES: 0.5,       # Medium
        FailureCategory.MISSING_DOCSTRINGS: 0.3,  # Low
        FailureCategory.RAG_MISMATCH: 0.4,        # Medium-low
        FailureCategory.UNKNOWN: 0.5,             # Medium
    }

    def __init__(self, logger: Optional[LoggerInterface] = None):
        """
        Initialize failure analyzer.

        Args:
            logger: Optional logger for debugging
        """
        self.logger = logger

        # Compile regex patterns once for performance
        self._compiled_patterns = {
            re.compile(pattern, re.IGNORECASE): category
            for pattern, category in self.FAILURE_PATTERNS.items()
        }

        if self.logger:
            self.logger.log("🔍 Failure analyzer initialized", "DEBUG")

    def analyze_failures(
        self,
        validation_results: Dict,
        code: Optional[str] = None
    ) -> FailureAnalysis:
        """
        Analyze validation failures and extract constraints.

        WHY: Converts validation errors into actionable refinement constraints.
             Enables intelligent retry with specific guidance.

        PERFORMANCE: O(n) where n is number of error messages.
                     Early returns when possible.

        Args:
            validation_results: Results from validation pipeline
            code: Optional code that was validated

        Returns:
            FailureAnalysis with category and constraints

        Example:
            results = {'passed': False, 'errors': ['import django not found']}
            analysis = analyzer.analyze_failures(results)
            # analysis.category == FailureCategory.MISSING_IMPORTS
            # analysis.constraints == ['Include import django']
        """
        # Early return if validation passed (performance optimization)
        if validation_results.get('passed', False):
            return FailureAnalysis(
                category=FailureCategory.UNKNOWN,
                retry_recommended=False,
                severity=0.0
            )

        # Extract error messages (avoid nested ifs - extract to helper)
        error_messages = self._extract_error_messages(validation_results)

        # Early return if no errors found
        if not error_messages:
            return FailureAnalysis(
                category=FailureCategory.UNKNOWN,
                retry_recommended=False,
                severity=0.5
            )

        # Categorize failure using Strategy pattern
        category = self._categorize_failure(error_messages)

        # Extract constraints based on category (Strategy pattern)
        constraints = self._extract_constraints(category, error_messages, code)

        # Extract code issues for detailed analysis
        code_issues = self._extract_code_issues(error_messages, code)

        # Get severity score from strategy mapping
        severity = self.CATEGORY_SEVERITY.get(category, 0.5)

        # Determine if retry is recommended
        retry_recommended = self._should_retry(category, severity)

        if self.logger:
            self.logger.log(
                f"📊 Failure analysis: {category.value} (severity: {severity:.2f})",
                "DEBUG"
            )

        return FailureAnalysis(
            category=category,
            constraints=constraints,
            code_issues=code_issues,
            severity=severity,
            retry_recommended=retry_recommended
        )

    def _extract_error_messages(self, validation_results: Dict) -> List[str]:
        """
        Extract error messages from validation results.

        WHY: Validation results can have different structures (errors list, message field, etc.)
             This normalizes them into a consistent list.

        PERFORMANCE: Early returns, list comprehension.
        """
        messages = []

        # Strategy pattern: Different result structures (dictionary mapping)
        extractors = {
            'errors': lambda r: r.get('errors', []),
            'error': lambda r: [r.get('error')] if r.get('error') else [],
            'message': lambda r: [r.get('message')] if r.get('message') else [],
            'validation_errors': lambda r: r.get('validation_errors', []),
        }

        for key, extractor in extractors.items():
            extracted = extractor(validation_results)
            if extracted:
                messages.extend(extracted)

        # Filter out None values (list comprehension for performance)
        return [msg for msg in messages if msg]

    def _categorize_failure(self, error_messages: List[str]) -> FailureCategory:
        """
        Categorize failure based on error messages.

        WHY: Different failure types require different refinement strategies.
        PATTERNS: Strategy pattern with regex mapping (no if/elif chains).
        PERFORMANCE: Compiled regex patterns, early return on first match.

        Args:
            error_messages: List of error messages from validation

        Returns:
            FailureCategory enum value
        """
        # Join messages for pattern matching (performance: single regex search)
        combined_messages = " ".join(error_messages).lower()

        # Strategy pattern: Check each pattern (early return on first match)
        for pattern, category in self._compiled_patterns.items():
            if pattern.search(combined_messages):
                return category

        # Default category if no pattern matches
        return FailureCategory.UNKNOWN

    def _extract_constraints(
        self,
        category: FailureCategory,
        error_messages: List[str],
        code: Optional[str]
    ) -> List[str]:
        """
        Extract specific constraints from error messages.

        WHY: Constraints guide prompt refinement for retries.
        PATTERNS: Strategy pattern for category-specific extraction.
        PERFORMANCE: Dictionary mapping instead of if/elif chains.

        Args:
            category: Failure category
            error_messages: Error messages from validation
            code: Optional code that was validated

        Returns:
            List of actionable constraints for prompt refinement
        """
        # Strategy pattern: Category → extractor function mapping
        constraint_extractors = {
            FailureCategory.MISSING_IMPORTS: self._extract_import_constraints,
            FailureCategory.INCOMPLETE_IMPLEMENTATION: self._extract_implementation_constraints,
            FailureCategory.INCORRECT_SIGNATURE: self._extract_signature_constraints,
            FailureCategory.MISSING_DOCSTRINGS: self._extract_docstring_constraints,
            FailureCategory.FORBIDDEN_PATTERNS: self._extract_forbidden_pattern_constraints,
        }

        # Get extractor for category (with default)
        extractor = constraint_extractors.get(
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
        Extract import-related constraints.

        WHY: Missing imports are common hallucination - extract which imports to add.
        PERFORMANCE: List comprehension, compiled regex.
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
        """Extract constraints for incomplete implementations."""
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
        """Extract constraints for signature mismatches."""
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
        """Extract constraints for missing docstrings."""
        return [
            "Add docstrings to all classes and functions",
            "Include description, Args, Returns, and Example sections in docstrings"
        ]

    def _extract_forbidden_pattern_constraints(
        self,
        error_messages: List[str],
        code: Optional[str]
    ) -> List[str]:
        """Extract constraints for forbidden patterns."""
        return [
            "Do NOT use eval(), exec(), or os.system()",
            "Use safe alternatives instead of dangerous patterns",
            "Avoid dynamic code execution"
        ]

    def _extract_code_issues(
        self,
        error_messages: List[str],
        code: Optional[str]
    ) -> List[Dict]:
        """
        Extract specific code locations/patterns that caused failures.

        WHY: Enables detailed analysis for supervisor learning.

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
        Extract code pattern from error message.

        WHY: Identifies specific problematic patterns for learning.
        PERFORMANCE: Compiled regex patterns.
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

    def _should_retry(self, category: FailureCategory, severity: float) -> bool:
        """
        Determine if retry with refinement is recommended.

        WHY: Some failures are not recoverable through prompt refinement.
        PATTERNS: Strategy pattern with category-based decision.

        Args:
            category: Failure category
            severity: Severity score (0.0-1.0)

        Returns:
            True if retry is recommended, False otherwise
        """
        # Strategy pattern: Categories that should NOT retry (early return)
        no_retry_categories = {
            FailureCategory.UNKNOWN,  # Don't know how to fix
        }

        if category in no_retry_categories:
            return False

        # Retry if severity is below threshold (not catastrophic)
        return severity < 0.95


# Factory for creating analyzers (Strategy pattern)
class FailureAnalyzerFactory:
    """
    Factory for creating failure analyzers.

    WHY: Enables different analyzer configurations without code changes.
    PATTERNS: Factory pattern (Open/Closed principle).
    """

    @staticmethod
    def create_analyzer(logger: Optional[LoggerInterface] = None) -> ValidationFailureAnalyzer:
        """
        Create failure analyzer.

        Args:
            logger: Optional logger

        Returns:
            ValidationFailureAnalyzer instance
        """
        return ValidationFailureAnalyzer(logger=logger)
