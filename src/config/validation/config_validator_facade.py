from artemis_logger import get_logger
logger = get_logger('config_validator_facade')
'\nConfig Validator Facade - Main interface for configuration validation\n\nWHY: Provides a simple, unified interface to the validation subsystem,\n     hiding internal complexity from clients.\n\nRESPONSIBILITY: Provide clean public API for configuration validation.\n\nPATTERNS: Facade pattern for simplified interface, Strategy pattern for validation.\n'
import sys
from config.validation.models import ValidationReport
from config.validation.validator_executor import ValidatorExecutor

class ConfigValidator:
    """
    Main configuration validator facade.

    WHY: Provides simple interface for validating all configuration at startup.
    RESPONSIBILITY: Orchestrate validation through ValidatorExecutor.
    PATTERNS: Facade pattern to hide validation complexity.

    Example:
        validator = ConfigValidator(verbose=True)
        report = validator.validate_all()
        if report.overall_status == "fail":
            sys.exit(1)
    """

    def __init__(self, verbose: bool=True):
        """
        Initialize config validator.

        WHY: Configure validation verbosity.
        PERFORMANCE: O(1) initialization.

        Args:
            verbose: Print validation progress
        """
        self.verbose = verbose
        self.executor = ValidatorExecutor(verbose=verbose)

    def validate_all(self) -> ValidationReport:
        """
        Run all validation checks.

        WHY: Single entry point for all configuration validation.
        PERFORMANCE: O(n) where n is number of checks, runs sequentially.

        Returns:
            ValidationReport with all results
        """
        return self.executor.execute_all_validations()

def validate_config_or_exit(verbose: bool=True) -> ValidationReport:
    """
    Validate configuration or exit with error.

    WHY: Convenience function for fail-fast validation at startup.
    PERFORMANCE: O(n) where n is number of validation checks.

    Args:
        verbose: Print validation progress

    Returns:
        ValidationReport if passed, exits otherwise

    Raises:
        SystemExit: If validation fails with status code 1

    Example:
        report = validate_config_or_exit(verbose=True)
        # If we get here, validation passed
    """
    validator = ConfigValidator(verbose=verbose)
    report = validator.validate_all()
    if report.overall_status == 'fail':
        
        logger.log('\nSTARTUP ABORTED: Fix configuration errors above', 'INFO')
        sys.exit(1)
    return report