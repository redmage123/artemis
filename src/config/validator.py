from artemis_logger import get_logger
logger = get_logger('validator')
'\nConfiguration Validator - Main Orchestrator\n\nWHY: Orchestrates all validation checks using validator strategies\n\nRESPONSIBILITY: Coordinate validation checks and generate comprehensive report\n\nPATTERNS: Strategy pattern for validation checks, Single Responsibility Principle\n'
import sys
from typing import List, Callable
from .models import ValidationResult, ValidationReport
from .validators import LLMProviderValidator, PathValidator, DatabaseValidator, MessengerValidator, RAGDatabaseValidator, ResourceLimitValidator, OptionalServiceValidator
from .report_generator import generate_report, print_report, print_result

class ConfigValidator:
    """
    Validates Artemis configuration at startup

    Single Responsibility: Validate all prerequisites before pipeline runs
    """

    def __init__(self, verbose: bool=True):
        """
        Initialize validator

        Args:
            verbose: Print validation progress
        """
        self.verbose = verbose
        self.results: List[ValidationResult] = []

    def validate_all(self) -> ValidationReport:
        """
        Run all validation checks

        WHY: Centralized validation orchestration ensures all checks run in order
        PERFORMANCE: O(n) where n is number of checks, runs sequentially

        Returns:
            ValidationReport with all results
        """
        if self.verbose:
            
            logger.log('\n' + '=' * 70, 'INFO')
            
            logger.log('ARTEMIS CONFIGURATION VALIDATION', 'INFO')
            
            logger.log('=' * 70 + '\n', 'INFO')
        validation_checks: List[Callable[[], None]] = [self._check_llm_provider, self._check_llm_api_keys, self._check_file_paths, self._check_database_access, self._check_messenger_backend, self._check_rag_database, self._check_resource_limits, self._check_optional_services]
        for check in validation_checks:
            check()
        report = generate_report(self.results)
        if self.verbose:
            print_report(report)
        return report

    def _add_result(self, result: ValidationResult) -> None:
        """
        Add validation result

        WHY: Centralizes result collection and optional printing

        Args:
            result: ValidationResult to add
        """
        self.results.append(result)
        if not self.verbose:
            return
        print_result(result)

    def _check_llm_provider(self) -> None:
        """Check LLM provider configuration"""
        validator = LLMProviderValidator()
        result = validator.validate_provider()
        self._add_result(result)

    def _check_llm_api_keys(self) -> None:
        """Check LLM API keys are present"""
        validator = LLMProviderValidator()
        result = validator.validate_api_keys()
        self._add_result(result)

    def _check_file_paths(self) -> None:
        """Check important file paths exist and are writable"""
        validator = PathValidator()
        results = validator.validate_paths()
        for result in results:
            self._add_result(result)

    def _check_database_access(self) -> None:
        """Check database/persistence access"""
        validator = DatabaseValidator()
        result = validator.validate_database()
        self._add_result(result)

    def _check_messenger_backend(self) -> None:
        """Check messenger backend availability"""
        validator = MessengerValidator()
        result = validator.validate_messenger()
        self._add_result(result)

    def _check_rag_database(self) -> None:
        """Check RAG database (ChromaDB) access"""
        validator = RAGDatabaseValidator()
        result = validator.validate_rag_database()
        self._add_result(result)

    def _check_resource_limits(self) -> None:
        """Check resource limits are reasonable"""
        validator = ResourceLimitValidator()
        results = validator.validate_resource_limits()
        for result in results:
            self._add_result(result)

    def _check_optional_services(self) -> None:
        """Check optional services"""
        validator = OptionalServiceValidator()
        results = validator.validate_optional_services()
        for result in results:
            self._add_result(result)

def validate_config_or_exit(verbose: bool=True) -> ValidationReport:
    """
    Validate configuration or exit

    WHY: Convenience function for fail-fast validation at startup
    PERFORMANCE: O(n) where n is number of validation checks

    Args:
        verbose: Print validation progress

    Returns:
        ValidationReport if passed, exits otherwise

    Raises:
        SystemExit: If validation fails with status code 1
    """
    validator = ConfigValidator(verbose=verbose)
    report = validator.validate_all()
    if report.overall_status == 'fail':
        
        logger.log('\nSTARTUP ABORTED: Fix configuration errors above', 'INFO')
        sys.exit(1)
    return report