#!/usr/bin/env python3
"""
WHY: Analyze validation failures to extract actionable refinement constraints
RESPONSIBILITY: Orchestrate categorization, constraint extraction, and retry decision
PATTERNS: Facade (simplified API), Composition (categorizer, extractors)

ValidationFailureAnalyzer converts validation errors into refinement guidance:
- Categorizes failures (missing imports, incomplete code, etc.)
- Extracts specific constraints
- Determines retry feasibility
- Calculates severity scores
"""

from typing import Dict, Optional
from artemis_stage_interface import LoggerInterface
from validation.models import FailureCategory, FailureAnalysis
from validation.categorizer import FailureCategorizer
from validation.constraint_extractors import ConstraintExtractors, CodeIssueExtractor
from validation.message_extractor import ValidationMessageExtractor


class ValidationFailureAnalyzer:
    """
    Analyzes validation failures and extracts constraints

    WHY: Validation failures contain patterns that can guide prompt refinement.
         Example: "import django missing" → constraint: "Include 'import django'"

    RESPONSIBILITY: ONLY analyze failures - no validation or retry logic.
    PATTERNS: Facade (simplified API), Composition (specialized components).
    """

    def __init__(self, logger: Optional[LoggerInterface] = None):
        """
        Initialize failure analyzer

        Args:
            logger: Optional logger for debugging
        """
        self.logger = logger

        # Initialize components (Composition pattern)
        self.message_extractor = ValidationMessageExtractor()
        self.categorizer = FailureCategorizer()
        self.constraint_extractors = ConstraintExtractors()
        self.code_issue_extractor = CodeIssueExtractor()

        if self.logger:
            self.logger.log("🔍 Failure analyzer initialized", "DEBUG")

    def analyze_failures(
        self,
        validation_results: Dict,
        code: Optional[str] = None
    ) -> FailureAnalysis:
        """
        Analyze validation failures and extract constraints

        WHY: Converts validation errors into actionable refinement constraints.
             Enables intelligent retry with specific guidance.

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
        # Guard clause - early return if validation passed
        if validation_results.get('passed', False):
            return FailureAnalysis(
                category=FailureCategory.UNKNOWN,
                retry_recommended=False,
                severity=0.0
            )

        # Extract error messages
        error_messages = self.message_extractor.extract(validation_results)

        # Guard clause - early return if no errors found
        if not error_messages:
            return FailureAnalysis(
                category=FailureCategory.UNKNOWN,
                retry_recommended=False,
                severity=0.5
            )

        # Categorize failure
        category = self.categorizer.categorize(error_messages)

        # Extract constraints
        constraints = self.constraint_extractors.extract(category, error_messages, code)

        # Extract code issues
        code_issues = self.code_issue_extractor.extract_issues(error_messages, code)

        # Get severity score
        severity = self.categorizer.get_severity(category)

        # Determine if retry is recommended
        retry_recommended = self.categorizer.should_retry(category, severity)

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
