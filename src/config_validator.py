#!/usr/bin/env python3
"""
Config Validator - Backward Compatibility Wrapper

WHY: Maintains backward compatibility with existing imports while delegating
     to the new modular config.validation package.

RESPONSIBILITY: Re-export all public API from config.validation package.

PATTERNS: Facade pattern for backward compatibility, delegation pattern.

DEPRECATED: This module is a compatibility wrapper. New code should import from:
    from config.validation import ConfigValidator, validate_config_or_exit

Example (backward compatible):
    from config_validator import ConfigValidator, validate_config_or_exit
    validator = ConfigValidator(verbose=True)
    report = validator.validate_all()

Example (new recommended way):
    from config.validation import ConfigValidator, validate_config_or_exit
    validator = ConfigValidator(verbose=True)
    report = validator.validate_all()
"""

import sys

# Re-export all public API from config.validation package
# WHY: Maintains 100% backward compatibility with existing code
from config.validation import (
    ConfigValidator,
    validate_config_or_exit,
    ValidationResult,
    ValidationReport
)

# Export for backward compatibility
__all__ = [
    "ConfigValidator",
    "validate_config_or_exit",
    "ValidationResult",
    "ValidationReport",
]


# Maintain command-line interface for backward compatibility
if __name__ == "__main__":
    """
    Run validation from command line.

    WHY: Allows standalone validation testing.
    PATTERNS: Strategy pattern for exit codes.
    """
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
