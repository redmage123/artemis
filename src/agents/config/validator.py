#!/usr/bin/env python3
"""
Configuration Validator Module

WHY: Handles all configuration validation logic including API keys,
value constraints, and cost limits. Separates validation from loading.

RESPONSIBILITY: Validate configuration against schema rules and requirements

PATTERNS:
- Guard clauses to reduce nesting (max 1 level)
- Strategy pattern using PROVIDER_KEY_MAP dispatch table
- Single Responsibility - only validates, doesn't load or generate
"""

from typing import Dict, List, Any

from agents.config.models import (
    ConfigValidationResult,
    ConfigSchema,
    PROVIDER_KEY_MAP
)


class ConfigValidator:
    """
    Configuration Validator

    WHY: Centralizes all validation logic. Makes validation rules
    easy to test and extend independently.

    RESPONSIBILITY: Validate configuration values and constraints
    """

    @staticmethod
    def validate_llm_keys(
        config: Dict[str, Any],
        provider: str,
        require_llm_key: bool,
        missing_keys: List[str]
    ) -> None:
        """
        Validate LLM API keys based on provider

        WHY: Ensures correct API key is present for selected provider.
        Uses strategy pattern to avoid if/elif chains.

        Args:
            config: Configuration dictionary
            provider: LLM provider name
            require_llm_key: Whether to require LLM key validation
            missing_keys: List to append missing keys to
        """
        # Guard clause: skip validation if not required
        if not require_llm_key:
            return

        # Strategy pattern: Use dictionary mapping instead of if/elif
        required_key = PROVIDER_KEY_MAP.get(provider)

        # Guard clause: no key mapping for provider
        if not required_key:
            return

        # Check if key exists and has value
        key_value = config.get(required_key)
        if not key_value:
            missing_keys.append(required_key)

    @staticmethod
    def validate_config_values(
        config: Dict[str, Any],
        invalid_keys: List[str]
    ) -> None:
        """
        Validate configuration values against valid_values constraints

        WHY: Ensures configuration values are within allowed ranges.
        Uses guard clauses to reduce nesting.

        Args:
            config: Configuration dictionary
            invalid_keys: List to append invalid keys to
        """
        schema = ConfigSchema.get_schema()

        for key, key_schema in schema.items():
            value = config.get(key)

            # Guard clause: skip if no value
            if not value:
                continue

            # Guard clause: skip if no valid_values constraint
            valid_values = key_schema.get('valid_values')
            if not valid_values:
                continue

            # Check if value is valid
            if value not in valid_values:
                invalid_keys.append(f"{key}={value} (valid: {valid_values})")

    @staticmethod
    def validate_cost_limit(
        config: Dict[str, Any],
        warnings: List[str],
        invalid_keys: List[str]
    ) -> None:
        """
        Validate cost limit configuration

        WHY: Ensures cost limit is numeric and reasonable.
        Warns if limit may be too low.

        Args:
            config: Configuration dictionary
            warnings: List to append warnings to
            invalid_keys: List to append invalid keys to
        """
        cost_limit_str = config.get('ARTEMIS_COST_LIMIT_USD')

        # Guard clause: no cost limit set
        if not cost_limit_str:
            return

        # Attempt to parse as float
        try:
            limit = float(cost_limit_str)
            # Warn if limit is very low
            if limit < 1.0:
                warnings.append(
                    f"Cost limit ${limit:.2f} may be too low for pipeline execution"
                )
        except (ValueError, TypeError):
            invalid_keys.append('ARTEMIS_COST_LIMIT_USD (must be numeric)')

    @staticmethod
    def generate_config_summary(config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate configuration summary for validation result

        WHY: Provides high-level overview of configuration state.
        Useful for logging and debugging.

        Args:
            config: Configuration dictionary

        Returns:
            Configuration summary dictionary
        """
        return {
            'provider': config.get('ARTEMIS_LLM_PROVIDER', 'openai'),
            'model': config.get('ARTEMIS_LLM_MODEL', 'default'),
            'rag_db_path': config.get('ARTEMIS_RAG_DB_PATH'),
            'code_review_enabled': config.get('ARTEMIS_ENABLE_CODE_REVIEW', True),
            'max_parallel_developers': config.get('ARTEMIS_MAX_PARALLEL_DEVELOPERS', 3),
            'has_openai_key': bool(config.get('OPENAI_API_KEY')),
            'has_anthropic_key': bool(config.get('ANTHROPIC_API_KEY'))
        }

    @staticmethod
    def validate_configuration(
        config: Dict[str, Any],
        require_llm_key: bool = True
    ) -> ConfigValidationResult:
        """
        Validate complete configuration

        WHY: Main validation entry point. Coordinates all validation checks
        and returns structured result.

        Args:
            config: Configuration dictionary
            require_llm_key: Require LLM API key based on provider

        Returns:
            ConfigValidationResult with validation status
        """
        missing_keys: List[str] = []
        invalid_keys: List[str] = []
        warnings: List[str] = []

        # Get provider for validation
        provider = config.get('ARTEMIS_LLM_PROVIDER', 'openai')

        # Run validation checks
        ConfigValidator.validate_llm_keys(
            config, provider, require_llm_key, missing_keys
        )
        ConfigValidator.validate_config_values(config, invalid_keys)
        ConfigValidator.validate_cost_limit(config, warnings, invalid_keys)

        # Generate summary
        config_summary = ConfigValidator.generate_config_summary(config)

        # Determine overall validity
        is_valid = len(missing_keys) == 0 and len(invalid_keys) == 0

        return ConfigValidationResult(
            is_valid=is_valid,
            missing_keys=missing_keys,
            invalid_keys=invalid_keys,
            warnings=warnings,
            config_summary=config_summary
        )

    @staticmethod
    def validate_required_keys(
        config: Dict[str, Any],
        required_keys: List[str]
    ) -> List[str]:
        """
        Validate that required keys are present

        WHY: Generic validation for required configuration keys.
        Used for custom validation scenarios.

        Args:
            config: Configuration dictionary
            required_keys: List of required keys

        Returns:
            List of missing keys
        """
        missing_keys: List[str] = []

        for key in required_keys:
            value = config.get(key)
            if not value:
                missing_keys.append(key)

        return missing_keys

    @staticmethod
    def is_valid_provider(provider: str) -> bool:
        """
        Check if provider is valid

        WHY: Validates provider string against known providers.

        Args:
            provider: Provider name

        Returns:
            True if valid, False otherwise
        """
        valid_providers = ConfigSchema.get_valid_values('ARTEMIS_LLM_PROVIDER')

        # Guard clause: no valid providers defined
        if not valid_providers:
            return True

        return provider in valid_providers
