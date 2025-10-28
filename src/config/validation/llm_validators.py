#!/usr/bin/env python3
"""
LLM Validators - LLM provider and API key validation

WHY: Validates LLM configuration before pipeline runs to fail fast and prevent
     runtime errors when attempting API calls.

RESPONSIBILITY: Validate LLM provider and API key configuration.

PATTERNS: Strategy pattern for provider-specific validation logic.
"""

import os
from typing import List, Optional, Callable, Dict, Any
from config.validation.models import ValidationResult


class LLMProviderValidator:
    """
    Validates LLM provider configuration.

    WHY: Ensures configured LLM provider is supported before pipeline starts.
    RESPONSIBILITY: Validate provider configuration only.
    PATTERNS: Strategy pattern with dictionary mapping.
    """

    # Strategy pattern: Valid providers
    VALID_PROVIDERS = ["openai", "anthropic", "mock"]

    @staticmethod
    def validate() -> ValidationResult:
        """
        Validate LLM provider configuration.

        WHY: Fail-fast validation to catch invalid provider before pipeline runs.
        PERFORMANCE: O(1) set membership check.

        Returns:
            ValidationResult with pass/fail status
        """
        provider = os.getenv("ARTEMIS_LLM_PROVIDER", "openai")

        # Guard clause: Invalid provider
        if provider not in LLMProviderValidator.VALID_PROVIDERS:
            return ValidationResult(
                check_name="LLM Provider",
                passed=False,
                message=f"Invalid provider '{provider}'",
                fix_suggestion=f"Set ARTEMIS_LLM_PROVIDER to one of: {', '.join(LLMProviderValidator.VALID_PROVIDERS)}"
            )

        # Success case
        return ValidationResult(
            check_name="LLM Provider",
            passed=True,
            message=f"Provider set to '{provider}'"
        )


class LLMAPIKeyValidator:
    """
    Validates LLM API keys are present and valid format.

    WHY: Validates API keys before pipeline runs to fail fast.
    RESPONSIBILITY: Validate API key presence and format only.
    PATTERNS: Strategy pattern via dictionary mapping for provider-specific validation.
    """

    # Strategy pattern: Provider-specific configurations
    # WHY: Makes it easy to add new providers without modifying code structure
    PROVIDER_CONFIGS: Dict[str, Dict[str, Any]] = {
        "openai": {
            "env_var": "OPENAI_API_KEY",
            "name": "OpenAI API Key",
            "validator": lambda key: key.startswith("sk-"),
            "error_msg": "API key has invalid format",
            "fix_suggestion": "export OPENAI_API_KEY=sk-...",
            "validation_msg": "OpenAI keys should start with 'sk-'"
        },
        "anthropic": {
            "env_var": "ANTHROPIC_API_KEY",
            "name": "Anthropic API Key",
            "validator": None,
            "fix_suggestion": "export ANTHROPIC_API_KEY=..."
        },
        "mock": {
            "env_var": None,
            "name": "Mock LLM",
            "is_mock": True
        }
    }

    @staticmethod
    def validate() -> ValidationResult:
        """
        Validate LLM API key configuration.

        WHY: Ensures API key is present and valid before making API calls.
        PERFORMANCE: O(1) dictionary lookup and string validation.

        Returns:
            ValidationResult with pass/fail status
        """
        provider = os.getenv("ARTEMIS_LLM_PROVIDER", "openai")

        # Guard clause: Unknown provider
        config = LLMAPIKeyValidator.PROVIDER_CONFIGS.get(provider)
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
