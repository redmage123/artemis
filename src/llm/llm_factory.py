#!/usr/bin/env python3
"""
LLM Client Factory - Creates appropriate LLM client based on provider

WHY: Centralize client creation logic with provider selection.
RESPONSIBILITY: Instantiate correct LLM client implementation.
PATTERNS: Factory Pattern, Strategy Pattern with dispatch tables.

Single Responsibility: Create appropriate LLM client based on provider
Open/Closed: Can add new providers without modifying existing code
"""

import os
from typing import Optional, Dict, Type

from llm.llm_interface import LLMClientInterface
from llm.llm_models import LLMProvider
from llm.openai_client import OpenAIClient
from llm.anthropic_client import AnthropicClient
from artemis_exceptions import ConfigurationError


class LLMClientFactory:
    """
    Factory for creating LLM clients

    WHY: Decouple client creation from usage (Factory Pattern).
    RESPONSIBILITY: Map provider enum/string to client class.
    PATTERNS: Factory Pattern, Strategy Pattern with dispatch tables.

    BENEFITS:
    - Add new providers by updating dispatch table only
    - No if/elif chains (Open/Closed Principle)
    - Centralized client creation logic
    """

    # Strategy pattern: Dictionary mapping instead of if/elif chain (SOLID: Open/Closed)
    _PROVIDER_STRATEGIES: Dict[LLMProvider, Type[LLMClientInterface]] = {
        LLMProvider.OPENAI: OpenAIClient,
        LLMProvider.ANTHROPIC: AnthropicClient
    }

    @staticmethod
    def create(
        provider: LLMProvider,
        api_key: Optional[str] = None
    ) -> LLMClientInterface:
        """
        Create LLM client for specified provider.

        WHY: Factory pattern enables adding new providers without code changes.
        PATTERNS: Strategy pattern with dictionary mapping (no if/elif chains).

        Args:
            provider: LLM provider enum (OPENAI, ANTHROPIC)
            api_key: Optional API key (uses env var if not provided)

        Returns:
            LLMClientInterface implementation for the provider

        Raises:
            ConfigurationError: If provider not supported
        """
        client_class = LLMClientFactory._PROVIDER_STRATEGIES.get(provider)

        if not client_class:
            raise ConfigurationError(
                f"Unsupported provider: {provider}",
                context={
                    "provider": str(provider),
                    "supported": [str(p) for p in LLMClientFactory._PROVIDER_STRATEGIES.keys()]
                }
            )

        return client_class(api_key=api_key)

    # Strategy pattern: Dictionary mapping for provider string -> enum (no if/elif chains)
    _PROVIDER_STRING_MAP: Dict[str, LLMProvider] = {
        "openai": LLMProvider.OPENAI,
        "anthropic": LLMProvider.ANTHROPIC
    }

    @staticmethod
    def create_from_env() -> LLMClientInterface:
        """
        Create LLM client from environment variables.

        WHY: Enables provider configuration via environment variables.
        PATTERNS: Strategy pattern with dictionary mapping (no if/elif chains).

        Environment Variables:
            ARTEMIS_LLM_PROVIDER: Provider name ("openai" or "anthropic", default: "openai")

        Returns:
            LLMClientInterface implementation based on env var

        Raises:
            ConfigurationError: If invalid provider in env var
        """
        provider_str = os.getenv("ARTEMIS_LLM_PROVIDER", "openai").lower()

        provider = LLMClientFactory._PROVIDER_STRING_MAP.get(provider_str)

        if not provider:
            raise ConfigurationError(
                f"Invalid ARTEMIS_LLM_PROVIDER: {provider_str}",
                context={
                    "provider": provider_str,
                    "supported": list(LLMClientFactory._PROVIDER_STRING_MAP.keys())
                }
            )

        return LLMClientFactory.create(provider)

    @staticmethod
    def create_from_string(
        provider: str,
        api_key: Optional[str] = None
    ) -> LLMClientInterface:
        """
        Create LLM client from provider string

        WHY: Convenience method for string-based provider selection.
        RESPONSIBILITY: Convert string to enum and delegate to create().

        Args:
            provider: Provider name ("openai" or "anthropic")
            api_key: Optional API key

        Returns:
            LLMClientInterface implementation

        Raises:
            ConfigurationError: If invalid provider string
        """
        provider_enum = LLMClientFactory._PROVIDER_STRING_MAP.get(provider.lower())

        if not provider_enum:
            raise ConfigurationError(
                f"Invalid provider: {provider}",
                context={
                    "provider": provider,
                    "supported": list(LLMClientFactory._PROVIDER_STRING_MAP.keys())
                }
            )

        return LLMClientFactory.create(provider_enum, api_key)
