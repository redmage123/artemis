#!/usr/bin/env python3
"""
Config Validation Package - Configuration validation subsystem

WHY: Provides modular, maintainable configuration validation with clean public API.
     Validates all configuration at startup to catch errors early (fail-fast).

RESPONSIBILITY: Export public API for configuration validation.

PATTERNS: Facade pattern for simplified interface, Strategy pattern for validators.

Public API:
    - ConfigValidator: Main validator class
    - validate_config_or_exit: Convenience function for startup validation
    - ValidationResult: Individual check result
    - ValidationReport: Aggregated validation report

Example:
    from config.validation import ConfigValidator, validate_config_or_exit

    # Option 1: Use facade
    validator = ConfigValidator(verbose=True)
    report = validator.validate_all()

    # Option 2: Use convenience function
    report = validate_config_or_exit(verbose=True)
"""

from config.validation.models import ValidationResult, ValidationReport
from config.validation.config_validator_facade import ConfigValidator, validate_config_or_exit

# Public API exports
__all__ = [
    "ConfigValidator",
    "validate_config_or_exit",
    "ValidationResult",
    "ValidationReport",
]
