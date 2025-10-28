#!/usr/bin/env python3
"""
Configuration Validation Package

WHY: Provides modular configuration validation for Artemis startup

RESPONSIBILITY: Export all validation components for easy import

PATTERNS: Package initialization with public API exports
"""

# Export models
from .models import ValidationResult, ValidationReport

# Export main validator
from .validator import ConfigValidator, validate_config_or_exit

# Export validator strategies (for direct use if needed)
from .validators import (
    LLMProviderValidator,
    PathValidator,
    DatabaseValidator,
    MessengerValidator,
    RAGDatabaseValidator,
    ResourceLimitValidator,
    OptionalServiceValidator
)

# Export report utilities
from .report_generator import generate_report, print_report, print_result

# Export constants (for reference)
from .constants import (
    VALID_LLM_PROVIDERS,
    VALID_MESSENGER_TYPES,
    VALID_PERSISTENCE_TYPES,
    DEFAULT_LLM_PROVIDER,
    DEFAULT_MESSENGER_TYPE,
    DEFAULT_PERSISTENCE_TYPE,
    PROVIDER_CONFIGS
)

# Export path utilities
from .path_utils import resolve_relative_path, ensure_directory_writable, get_script_directory

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
