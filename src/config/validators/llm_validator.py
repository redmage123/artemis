#!/usr/bin/env python3
"""
LLM Provider Validation Module

WHY: Validates LLM provider configuration and API keys to fail fast before pipeline runs

RESPONSIBILITY: Validate LLM provider selection and API key presence/format

PATTERNS: Strategy pattern for provider-specific validation, guard clauses for early returns
"""

import os
from typing import Dict, Any, Callable
from ..models import ValidationResult
from ..constants import (
    VALID_LLM_PROVIDERS,
    DEFAULT_LLM_PROVIDER,
    PROVIDER_CONFIGS
)


class LLMProviderValidator:
    """
    Validates LLM provider configuration

    WHY: Single Responsibility - handles only LLM provider validation

    PATTERNS: Strategy pattern for provider-specific validation
    """

    def validate_provider(self) -> ValidationResult:
        """
        Check LLM provider configuration

        WHY: Validates that configured LLM provider is supported
        PERFORMANCE: O(1) set membership check

        Returns:
            ValidationResult for provider check
        """
        provider = os.getenv("ARTEMIS_LLM_PROVIDER", DEFAULT_LLM_PROVIDER)

        # Guard clause: Invalid provider
        if provider not in VALID_LLM_PROVIDERS:
            return ValidationResult(
                check_name="LLM Provider",
                passed=False,
                message=f"Invalid provider '{provider}'",
                fix_suggestion=f"Set ARTEMIS_LLM_PROVIDER to one of: {', '.join(VALID_LLM_PROVIDERS)}"
            )

        # Success case
        return ValidationResult(
            check_name="LLM Provider",
            passed=True,
            message=f"Provider set to '{provider}'"
        )

    def validate_api_keys(self) -> ValidationResult:
        """
        Check LLM API keys are present

        WHY: Validates API keys before pipeline runs to fail fast
        PATTERNS: Strategy pattern via dictionary mapping, guard clauses for early returns
        PERFORMANCE: O(1) dictionary lookup

        Returns:
            ValidationResult for API key check
        """
        provider = os.getenv("ARTEMIS_LLM_PROVIDER", DEFAULT_LLM_PROVIDER)

        # Guard clause: Unknown provider
        config = PROVIDER_CONFIGS.get(provider)
        if not config:
            return ValidationResult(
                check_name="LLM Provider",
                passed=False,
                message=f"Unknown provider: {provider}",
                fix_suggestion="Set ARTEMIS_LLM_PROVIDER to 'openai', 'anthropic', or 'mock'"
            )

        # Guard clause: Mock provider (no API key needed)
        if config.get("is_mock"):
            return ValidationResult(
                check_name=config["name"],
                passed=True,
                message="Using mock LLM (no API key needed)",
                severity="warning"
            )

        # Check API key for real providers
        api_key = os.getenv(config["env_var"])

        # Guard clause: API key not set
        if not api_key:
            return ValidationResult(
                check_name=config["name"],
                passed=False,
                message=f"{config['env_var']} not set",
                fix_suggestion=config["fix_suggestion"]
            )

        # Guard clause: Validate format if validator provided
        if config.get("validator") and not config["validator"](api_key):
            return ValidationResult(
                check_name=config["name"],
                passed=False,
                message=config["error_msg"],
                fix_suggestion=config.get("validation_msg", config["fix_suggestion"])
            )

        # Success case: API key present and valid
        return ValidationResult(
            check_name=config["name"],
            passed=True,
            message="API key present" + (" and valid format" if config.get("validator") else "")
        )
