#!/usr/bin/env python3
"""
Validator Executor - Orchestrates validation checks

WHY: Coordinates execution of all validation checks in a controlled manner,
     ensuring all checks run and results are collected.

RESPONSIBILITY: Execute all validation checks and collect results.

PATTERNS: Strategy pattern for validation check orchestration, functional composition.
"""

from typing import List, Callable
from config.validation.models import ValidationResult, ValidationReport
from config.validation.llm_validators import LLMProviderValidator, LLMAPIKeyValidator
from config.validation.path_validators import PathValidator
from config.validation.database_validators import DatabaseValidator
from config.validation.messenger_validators import MessengerValidator
from config.validation.resource_validators import (
    ResourceLimitValidator,
    RAGDatabaseValidator,
    OptionalServiceValidator
)
from config.validation.report_generator import ReportGenerator, ReportPrinter


class ValidatorExecutor:
    """
    Executes all validation checks and collects results.

    WHY: Centralized validation orchestration ensures all checks run in order
         and results are properly collected and reported.

    RESPONSIBILITY: Execute validation checks and collect results only.

    PATTERNS: Strategy pattern for validation check orchestration, functional approach.
    """

    def __init__(self, verbose: bool = True):
        """
        Initialize validator executor.

        WHY: Configure verbosity for validation output.
        PERFORMANCE: O(1) initialization.

        Args:
            verbose: Print validation progress
        """
        self.verbose = verbose
        self.results: List[ValidationResult] = []

    def _add_result(self, result: ValidationResult) -> None:
        """
        Add validation result and optionally print.

        WHY: Centralized result collection with optional output.
        PERFORMANCE: O(1) list append and optional print.

        Args:
            result: ValidationResult to add
        """
        self.results.append(result)

        # Guard clause: Early return if not verbose
        if not self.verbose:
            return

        # Print result
        ReportPrinter.print_result(result)

    def _add_results(self, results: List[ValidationResult]) -> None:
        """
        Add multiple validation results.

        WHY: Efficient handling of validators that return multiple results.
        PERFORMANCE: O(n) where n is number of results.

        Args:
            results: List of ValidationResults to add
        """
        for result in results:
            self._add_result(result)

    def _execute_single_result_validator(self, validator_func: Callable[[], ValidationResult]) -> None:
        """
        Execute validator that returns single result.

        WHY: Pure function to execute validator and collect result.
        PERFORMANCE: O(1) function call and result collection.

        Args:
            validator_func: Validator function to execute
        """
        result = validator_func()
        self._add_result(result)

    def _execute_multi_result_validator(self, validator_func: Callable[[], List[ValidationResult]]) -> None:
        """
        Execute validator that returns multiple results.

        WHY: Pure function to execute validator and collect results.
        PERFORMANCE: O(n) where n is number of results from validator.

        Args:
            validator_func: Validator function to execute
        """
        results = validator_func()
        self._add_results(results)

    def execute_all_validations(self) -> ValidationReport:
        """
        Execute all validation checks.

        WHY: Centralized validation orchestration ensures all checks run in order.
        PERFORMANCE: O(n) where n is number of checks, runs sequentially.

        Returns:
            ValidationReport with all results
        """
        if self.verbose:
            ReportPrinter.print_header()

        # Strategy pattern: Define all validation checks
        # WHY: Makes it easy to add/remove checks without modifying orchestration logic
        # Each entry is (validator_function, returns_multiple_results)

        # Single result validators
        single_result_validators = [
            LLMProviderValidator.validate,
            LLMAPIKeyValidator.validate,
            DatabaseValidator.validate,
            MessengerValidator.validate,
            RAGDatabaseValidator.validate,
        ]

        # Multiple result validators
        multi_result_validators = [
            PathValidator.validate,
            ResourceLimitValidator.validate,
            OptionalServiceValidator.validate,
        ]

        # Execute single result validators using list comprehension
        for validator_func in single_result_validators:
            self._execute_single_result_validator(validator_func)

        # Execute multiple result validators using list comprehension
        for validator_func in multi_result_validators:
            self._execute_multi_result_validator(validator_func)

        # Generate report
        report = ReportGenerator.generate(self.results)

        if self.verbose:
            ReportPrinter.print_report(report)

        return report
