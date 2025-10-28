#!/usr/bin/env python3
"""
Config Validator - Backward Compatibility Wrapper

WHY: Provides backward compatibility for existing imports while using modular implementation

RESPONSIBILITY: Re-export all components from config package

PATTERNS: Facade pattern for backward compatibility

MIGRATION: This is a compatibility layer. New code should import from config package directly:
    from config import ConfigValidator, validate_config_or_exit
    from config.models import ValidationResult, ValidationReport
"""

# Re-export all components from config package
from config import (
    # Models
    ValidationResult,
    ValidationReport,
    # Main validator
    ConfigValidator,
    validate_config_or_exit,
    # Validator strategies (if needed)
    LLMProviderValidator,
    PathValidator,
    DatabaseValidator,
    MessengerValidator,
    RAGDatabaseValidator,
    ResourceLimitValidator,
    OptionalServiceValidator,
    # Report utilities
    generate_report,
    print_report,
    print_result,
    # Constants
    VALID_LLM_PROVIDERS,
    VALID_MESSENGER_TYPES,
    VALID_PERSISTENCE_TYPES,
    DEFAULT_LLM_PROVIDER,
    DEFAULT_MESSENGER_TYPE,
    DEFAULT_PERSISTENCE_TYPE,
    PROVIDER_CONFIGS,
    # Path utilities
    resolve_relative_path,
    ensure_directory_writable,
    get_script_directory,
)

__all__ = [
    # Models
    "ValidationResult",
    "ValidationReport",
    # Main validator
    "ConfigValidator",
    "validate_config_or_exit",
    # Validator strategies
    "LLMProviderValidator",
    "PathValidator",
    "DatabaseValidator",
    "MessengerValidator",
    "RAGDatabaseValidator",
    "ResourceLimitValidator",
    "OptionalServiceValidator",
    # Report utilities
    "generate_report",
    "print_report",
    "print_result",
    # Constants
    "VALID_LLM_PROVIDERS",
    "VALID_MESSENGER_TYPES",
    "VALID_PERSISTENCE_TYPES",
    "DEFAULT_LLM_PROVIDER",
    "DEFAULT_MESSENGER_TYPE",
    "DEFAULT_PERSISTENCE_TYPE",
    "PROVIDER_CONFIGS",
    # Path utilities
    "resolve_relative_path",
    "ensure_directory_writable",
    "get_script_directory",
]


if __name__ == "__main__":
    """
    Run validation from command line

    WHY: Allows standalone validation testing
    """
    import sys

    validator = ConfigValidator(verbose=True)
    report = validator.validate_all()

    # Strategy pattern: Dictionary mapping for exit codes
    # WHY: Avoids if/elif chain, clear mapping of status to exit code
    exit_codes = {
        "pass": 0,
        "warning": 2,
        "fail": 1
    }

    exit_code = exit_codes.get(report.overall_status, 1)
    sys.exit(exit_code)
