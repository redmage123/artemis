#!/usr/bin/env python3
"""
Config Validation - Configuration validation and display utilities

WHAT:
Configuration validation utilities for checking required keys,
displaying validation errors with helpful hints, and determining
Hydra config paths.

WHY:
Separates config validation from entry points, enabling:
- Focused testing of validation logic
- Reusable validation utilities
- Clear error messages with actionable hints
- Clean separation of concerns

RESPONSIBILITY:
- Validate configuration and exit if invalid
- Display validation errors with helpful hints
- Provide hints for common configuration issues (API keys, etc.)
- Determine Hydra config directory path

PATTERNS:
- Guard Clause: Early returns for valid config
- Template Method: Consistent error display format
- Facade Pattern: Simplifies validation logic

EXTRACTED FROM: artemis_orchestrator.py lines 1287-1394
"""

import sys
from typing import Any
from pathlib import Path


def display_validation_errors(config: Any, validation: Any) -> None:
    """
    Display configuration validation errors with helpful hints.

    WHAT:
    Formats and displays configuration validation errors with
    descriptions and helpful hints for common issues.

    WHY:
    Makes configuration errors actionable by providing:
    - Clear error messages
    - Descriptions of missing/invalid keys
    - Hints for setting API keys
    - Instructions for next steps

    Args:
        config: Configuration object with schema
        validation: Validation result object

    PATTERNS:
        - Template Method: Consistent error display format
        - Guard Clause: Handles optional error types
    """
    print("\n" + "="*80)
    print("❌ CONFIGURATION ERROR")
    print("="*80)
    print("\nThe pipeline cannot run due to invalid configuration.\n")

    # Display missing keys if any
    if validation.missing_keys:
        print("Missing Required Keys:")
        # Display missing keys with descriptions
        [print(f"  ❌ {key}\n     Description: {config.CONFIG_SCHEMA.get(key, {}).get('description', 'N/A')}")
         for key in validation.missing_keys]

        # Provide helpful hints for OpenAI
        if 'OPENAI_API_KEY' in validation.missing_keys:
            print(f"\n💡 Set your OpenAI API key:")
            print(f"   export OPENAI_API_KEY='your-key-here'")

        # Provide helpful hints for Anthropic
        if 'ANTHROPIC_API_KEY' in validation.missing_keys:
            print(f"\n💡 Set your Anthropic API key:")
            print(f"   export ANTHROPIC_API_KEY='your-key-here'")

    # Display invalid keys if any
    if validation.invalid_keys:
        print("\nInvalid Configuration Values:")
        [print(f"  ❌ {key}") for key in validation.invalid_keys]

    print("\n" + "="*80)
    print("\n💡 Run with --config-report to see full configuration")
    print("💡 Run with --skip-validation to bypass (NOT RECOMMENDED)\n")


def validate_config_or_exit(config: Any, skip_validation: bool) -> None:
    """
    Validate configuration and exit if invalid.

    WHAT:
    Validates configuration against schema and exits with error
    message if validation fails (unless skip_validation is True).

    WHY:
    Ensures pipeline doesn't run with invalid configuration,
    preventing cryptic errors later. Provides immediate feedback
    about configuration issues.

    Args:
        config: Configuration object to validate
        skip_validation: If True, skip validation

    PATTERNS:
        - Guard Clause: Early returns for skipped/valid config
        - Fail Fast: Exits immediately on invalid config
    """
    # Guard: Validation skipped
    if skip_validation:
        return

    validation = config.validate_configuration(require_llm_key=True)

    # Guard: Validation passed
    if validation.is_valid:
        return

    # Validation failed - display errors and exit
    display_validation_errors(config, validation)
    sys.exit(1)


def get_config_path() -> str:
    """
    Get absolute path to Hydra config directory.

    WHAT:
    Determines the absolute path to the Hydra configuration
    directory relative to this file's location.

    WHY:
    This allows the orchestrator to be run from any directory,
    not just from .agents/agile. Hydra requires absolute or
    relative-to-module paths for config directories.

    Returns:
        Absolute path to the conf directory

    PATTERNS:
        - Path Resolution: Uses __file__ for relative path
    """
    script_dir = Path(__file__).parent.parent  # orchestrator/ -> src/
    return str(script_dir / "conf")
