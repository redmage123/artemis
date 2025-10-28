#!/usr/bin/env python3
"""
WHY: Handle GDPR compliance evaluation logic
RESPONSIBILITY: Evaluate implementations for GDPR compliance
PATTERNS: Facade pattern for GDPR evaluation, Guard clauses

This module handles GDPR compliance evaluation by delegating to the GDPREvaluator.
"""

from typing import Dict, Any
from gdpr_evaluator import GDPREvaluator
from artemis_exceptions import GDPREvaluationError, wrap_exception


class GDPRComplianceEvaluator:
    """
    WHY: Encapsulate GDPR compliance evaluation logic
    RESPONSIBILITY: Perform GDPR compliance checks
    PATTERNS: Facade pattern, Dependency injection

    Benefits:
    - Isolates GDPR evaluation logic
    - Clean error handling
    - Testable
    """

    def __init__(self, logger: Any):
        """
        WHY: Initialize with dependencies
        RESPONSIBILITY: Set up logger

        Args:
            logger: Logger interface
        """
        self.logger = logger

    def evaluate_gdpr_compliance(
        self,
        developer_name: str,
        implementation_dir: str
    ) -> Dict:
        """
        WHY: Run GDPR compliance evaluation
        RESPONSIBILITY: Execute GDPR checks and handle errors
        PATTERNS: Guard clauses for error handling

        Args:
            developer_name: Name of the developer
            implementation_dir: Directory containing implementation

        Returns:
            Dict with GDPR evaluation results

        Raises:
            GDPREvaluationError: If evaluation fails
        """
        self.logger.log("Running GDPR compliance checks...", "INFO")

        try:
            gdpr_evaluator = GDPREvaluator()
            gdpr_results = gdpr_evaluator.evaluate_directory(implementation_dir)
            return gdpr_results

        except Exception as e:
            raise wrap_exception(
                e,
                GDPREvaluationError,
                f"GDPR evaluation failed for {developer_name}",
                {"developer": developer_name, "implementation_dir": implementation_dir}
            )
