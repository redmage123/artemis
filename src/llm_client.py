#!/usr/bin/env python3
"""
LLM Client - Backward Compatibility Wrapper

WHY: Maintain backward compatibility while using modular implementation.
RESPONSIBILITY: Re-export all components from llm package.
PATTERNS: Facade Pattern, Re-export Pattern.

Single Responsibility: Provide backward-compatible interface to refactored code
Open/Closed: Implementation changes don't affect existing imports
"""

# Re-export all components from llm package for backward compatibility
from llm.llm_models import (
    LLMProvider,
    LLMMessage,
    LLMResponse
)

from llm.llm_interface import LLMClientInterface

from llm.openai_client import OpenAIClient
from llm.anthropic_client import AnthropicClient

from llm.llm_factory import LLMClientFactory

from llm.stream_processor import StreamProcessor

from typing import Optional


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_llm_client(
    provider: str = "openai",
    api_key: Optional[str] = None
) -> LLMClientInterface:
    """
    Convenience function to create LLM client

    WHY: Provides simple string-based interface for client creation.
    RESPONSIBILITY: Delegate to factory with string conversion.

    Args:
        provider: "openai" or "anthropic"
        api_key: API key (optional, will use env var if not provided)

    Returns:
        LLMClientInterface implementation

    Example:
        client = create_llm_client("openai")
        messages = [
            LLMMessage(role="system", content="You are a helpful assistant"),
            LLMMessage(role="user", content="Write a Python function to add two numbers")
        ]
        response = client.complete(messages)
        print(response.content)
    """
    return LLMClientFactory.create_from_string(provider, api_key)


# Backwards compatibility wrapper
class LLMClient:
    """
    Backwards compatibility wrapper

    WHY: Preserve existing code that uses LLMClient.create_from_env() or LLMClient.create().
    RESPONSIBILITY: Delegate to factory methods.
    PATTERNS: Facade Pattern.

    Provides both type compatibility (for isinstance checks) and factory methods
    """
    @staticmethod
    def create_from_env() -> LLMClientInterface:
        """
        Create LLM client from environment variables

        WHY: Backward compatibility for existing code.
        """
        return LLMClientFactory.create_from_env()

    @staticmethod
    def create(provider: LLMProvider, api_key: Optional[str] = None) -> LLMClientInterface:
        """
        Create LLM client

        WHY: Backward compatibility for existing code.
        """
        return LLMClientFactory.create(provider, api_key)


# ============================================================================
# MAIN - TESTING
# ============================================================================

if __name__ == "__main__":
    """Test LLM client backward compatibility"""
    import sys
    from artemis_exceptions import wrap_exception, LLMClientError

    # Test with OpenAI
    print("Testing OpenAI client...")
    try:
        openai_client = create_llm_client("openai")
        print(f"✅ OpenAI client created")
        print(f"Available models: {', '.join(openai_client.get_available_models()[:3])}...")

        # Test completion
        messages = [
            LLMMessage(role="system", content="You are a helpful assistant."),
            LLMMessage(role="user", content="Say 'Hello from OpenAI!' and nothing else.")
        ]

        response = openai_client.complete(messages, max_tokens=100)
        print(f"✅ Response: {response.content}")
        print(f"   Model: {response.model}")
        print(f"   Tokens: {response.usage['total_tokens']}")
    except Exception as e:
        error = wrap_exception(
            e,
            LLMClientError,
            "OpenAI test failed",
            {"provider": "openai"}
        )
        print(f"❌ OpenAI test failed: {error}")

    print("\n" + "="*60 + "\n")

    # Test with Anthropic
    print("Testing Anthropic client...")
    try:
        anthropic_client = create_llm_client("anthropic")
        print(f"✅ Anthropic client created")
        print(f"Available models: {', '.join(anthropic_client.get_available_models()[:3])}...")

        # Test completion
        messages = [
            LLMMessage(role="system", content="You are a helpful assistant."),
            LLMMessage(role="user", content="Say 'Hello from Anthropic!' and nothing else.")
        ]

        response = anthropic_client.complete(messages, max_tokens=100)
        print(f"✅ Response: {response.content}")
        print(f"   Model: {response.model}")
        print(f"   Tokens: {response.usage['total_tokens']}")
    except Exception as e:
        error = wrap_exception(
            e,
            LLMClientError,
            "Anthropic test failed",
            {"provider": "anthropic"}
        )
        print(f"❌ Anthropic test failed: {error}")

    print("\n" + "="*60 + "\n")

    # Test backward compatibility with LLMClient class
    print("Testing backward compatibility (LLMClient.create_from_env())...")
    try:
        client = LLMClient.create_from_env()
        print(f"✅ LLMClient.create_from_env() works")
        print(f"Available models: {', '.join(client.get_available_models()[:3])}...")
    except Exception as e:
        error = wrap_exception(
            e,
            LLMClientError,
            "Backward compatibility test failed",
            {}
        )
        print(f"❌ Backward compatibility test failed: {error}")
