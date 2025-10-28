#!/usr/bin/env python3
"""
Validator Facade Module

WHY: Provides a unified interface to orchestrate all validator modules

RESPONSIBILITY: Coordinate all validation checks and aggregate results

PATTERNS: Facade pattern for simplified interface, pure functional composition
"""

from typing import List
from ..models import ValidationResult
from .llm_validator import LLMProviderValidator
from .path_validator import PathValidator
from .database_validator import DatabaseValidator
from .messenger_validator import MessengerValidator
from .rag_validator import RAGDatabaseValidator
from .resource_validator import ResourceLimitValidator
from .optional_service_validator import OptionalServiceValidator


class ValidatorFacade:
    """
    Facade for all validator modules

    WHY: Provides simplified interface to run all validations
    RESPONSIBILITY: Orchestrate all validators and collect results
    PATTERNS: Facade pattern to hide complexity of individual validators
    """

    def __init__(self):
        """
        Initialize all validators

        WHY: Instantiate all validator modules for execution
        """
        self.llm_validator = LLMProviderValidator()
        self.path_validator = PathValidator()
        self.database_validator = DatabaseValidator()
        self.messenger_validator = MessengerValidator()
        self.rag_validator = RAGDatabaseValidator()
        self.resource_validator = ResourceLimitValidator()
        self.optional_service_validator = OptionalServiceValidator()

    def run_all_validations(self) -> List[ValidationResult]:
        """
        Run all validation checks

        WHY: Aggregates all validation results in single call
        PERFORMANCE: O(n) where n is total number of checks across all validators

        Returns:
            List of all ValidationResult objects
        """
        results = []

        # LLM validations
        results.append(self.llm_validator.validate_provider())
        results.append(self.llm_validator.validate_api_keys())

        # Path validations
        results.extend(self.path_validator.validate_paths())

        # Database validation
        results.append(self.database_validator.validate_database())

        # Messenger validation
        results.append(self.messenger_validator.validate_messenger())

        # RAG database validation
        results.append(self.rag_validator.validate_rag_database())

        # Resource limit validations
        results.extend(self.resource_validator.validate_resource_limits())

        # Optional service validations
        results.extend(self.optional_service_validator.validate_optional_services())

        return results
