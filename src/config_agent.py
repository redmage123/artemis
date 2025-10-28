#!/usr/bin/env python3
"""
Configuration Agent - Backward Compatibility Wrapper

WHY: Maintains backward compatibility with existing code while using
the new modular agents/config package structure.

RESPONSIBILITY: Re-export all public APIs from agents.config package

PATTERNS:
- Facade pattern: Provides same interface as before
- Deprecation wrapper: Allows gradual migration

MIGRATION: Code using this module will continue to work unchanged.
New code should import from agents.config directly.

Example:
    Old: from config_agent import ConfigurationAgent, get_config
    New: from agents.config import ConfigurationAgent, get_config
"""

# Re-export all public APIs from agents.config package
from agents.config import (
    # Main agent class and functions
    ConfigurationAgent,
    get_config,
    reset_config,

    # Models and data structures
    ConfigValidationResult,
    ConfigSchema,
    BOOL_STRING_MAP,
    PROVIDER_KEY_MAP,

    # Component classes (for advanced usage)
    ConfigLoader,
    ConfigValidator,
    ConfigGenerator,
)


# CLI Actions for backward compatibility
def _run_validate(config: ConfigurationAgent) -> None:
    """
    Run validation action (CLI helper)

    WHY: Maintains CLI compatibility with original implementation.
    """
    result = config.validate_configuration()

    # Guard clause: handle invalid case
    if not result.is_valid:
        print("\nConfiguration is INVALID")
        exit(1)

    print("\nConfiguration is VALID")
    exit(0)


def _run_export(config: ConfigurationAgent) -> None:
    """
    Run export action (CLI helper)

    WHY: Maintains CLI compatibility with original implementation.
    """
    print(config.export_to_json())


def _run_report(config: ConfigurationAgent) -> None:
    """
    Run report action (CLI helper)

    WHY: Maintains CLI compatibility with original implementation.
    """
    config.print_configuration_report()


# CLI for testing (maintains backward compatibility)
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Artemis Configuration Agent")
    parser.add_argument("--validate", action="store_true", help="Validate configuration")
    parser.add_argument("--report", action="store_true", help="Print configuration report")
    parser.add_argument("--export", action="store_true", help="Export configuration as JSON")
    args = parser.parse_args()

    config = ConfigurationAgent(verbose=True)

    # Guard clause: handle validate first (exits)
    if args.validate:
        _run_validate(config)

    # Guard clause: handle export
    if args.export:
        _run_export(config)
        exit(0)

    # Default action: show report
    _run_report(config)
