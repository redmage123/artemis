#!/usr/bin/env python3
"""
LLM Client - Unified Interface for OpenAI and Anthropic APIs

Single Responsibility: Provide unified interface to multiple LLM providers
Open/Closed: Can add new providers without modifying existing code
Liskov Substitution: All clients implement LLMClientInterface
Interface Segregation: Minimal interface with just what's needed
Dependency Inversion: Depends on LLMClientInterface abstraction
"""

import os
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass
from enum import Enum

from artemis_exceptions import (
    LLMClientError,
    ConfigurationError,
    LLMAPIError,
    wrap_exception
)


class LLMProvider(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


@dataclass
class LLMMessage:
    """Represents a message in a conversation"""
    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class LLMResponse:
    """Standardized response from any LLM provider"""
    content: str
    model: str
    provider: str
    usage: Dict[str, int]  # {"prompt_tokens": X, "completion_tokens": Y, "total_tokens": Z}
    raw_response: Dict  # Full API response for debugging


class LLMClientInterface(ABC):
    """
    Abstract base class for all LLM clients

    Single Responsibility: Define contract for LLM communication

    Why this exists: Provides unified interface for multiple LLM providers (OpenAI,
    Anthropic), enabling easy provider switching without code changes.

    Design Pattern: Strategy Pattern - different providers are interchangeable strategies
    SOLID: Interface Segregation - minimal interface with only essential methods

    Benefits:
    - Switch providers via config (no code changes)
    - Test with mock LLM without API costs
    - Standardized error handling across providers
    - Unified usage tracking and cost monitoring
    """

    @abstractmethod
    def complete(
        self,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        response_format: Optional[Dict] = None
    ) -> LLMResponse:
        """
        Send messages to LLM and get response

        Args:
            messages: Conversation history (system, user, assistant messages)
            model: Specific model to use (provider default if None)
            temperature: Sampling temperature 0.0-1.0 (lower = more deterministic)
            max_tokens: Maximum tokens in response (cost control)
            response_format: Optional format spec (e.g., {"type": "json_object"})

        Returns:
            Standardized LLMResponse with content, usage, and metadata
        """
        pass

    @abstractmethod
    def complete_stream(
        self,
        messages: List[LLMMessage],
        on_token_callback: Optional[Callable[[str], bool]] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        response_format: Optional[Dict] = None
    ) -> LLMResponse:
        """
        Send messages to LLM and get response with streaming (token-by-token).

        Args:
            messages: Conversation history (system, user, assistant messages)
            on_token_callback: Optional callback called for each token.
                              Receives token string, returns True to continue or False to stop.
            model: Specific model to use (provider default if None)
            temperature: Sampling temperature 0.0-1.0 (lower = more deterministic)
            max_tokens: Maximum tokens in response (cost control)
            response_format: Optional format spec (e.g., {"type": "json_object"})

        Returns:
            Standardized LLMResponse with content, usage, and metadata

        WHY: Enables real-time validation during generation.
             Callback can stop generation if hallucination detected.
        """
        pass

    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        pass


class OpenAIClient(LLMClientInterface):
    """
    OpenAI API client

    Single Responsibility: Handle OpenAI API communication only
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ConfigurationError(
                "OpenAI API key not provided and OPENAI_API_KEY env var not set",
                context={"provider": "openai"}
            )

        # Import OpenAI library (lazy import)
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("openai library not installed. Run: pip install openai")

    def complete(
        self,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        response_format: Optional[Dict] = None
    ) -> LLMResponse:
        """Send messages to OpenAI and get response"""
        # Convert our LLMMessage format to OpenAI format
        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        # Default model
        if model is None:
            model = "gpt-4o"  # Latest GPT-4o model (supports temperature)

        # Build API call kwargs
        api_kwargs = {
            "model": model,
            "messages": openai_messages,
            "temperature": temperature,
        }

        # Note: Newer OpenAI models use max_completion_tokens instead of max_tokens
        # o1 and GPT-5 models don't support custom temperature parameter
        if model.startswith("o1") or model.startswith("gpt-5"):
            # These models only support temperature=1 (default), so we omit it
            del api_kwargs["temperature"]
            api_kwargs["max_completion_tokens"] = max_tokens
        else:
            # Most modern models now use max_completion_tokens
            # Use max_completion_tokens for all models (GPT-4o, etc.)
            api_kwargs["max_completion_tokens"] = max_tokens

        # Add response_format if specified (for JSON mode)
        if response_format:
            api_kwargs["response_format"] = response_format

        # Call OpenAI API
        response = self.client.chat.completions.create(**api_kwargs)

        # Extract response
        content = response.choices[0].message.content

        # Build usage info
        usage = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens
        }

        return LLMResponse(
            content=content,
            model=response.model,
            provider="openai",
            usage=usage,
            raw_response=response.model_dump()
        )

    def generate_text(
        self,
        messages: Optional[List[LLMMessage]] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        response_format: Optional[Dict] = None,
        system_message: Optional[str] = None,
        user_message: Optional[str] = None
    ) -> LLMResponse:
        """
        Alias for complete() to match ai_query_service expectations

        Supports two calling conventions:
        1. messages parameter (List[LLMMessage])
        2. system_message + user_message parameters (strings)
        """
        # Convert system_message/user_message to messages format
        if messages is None and (system_message or user_message):
            messages = []
            if system_message:
                messages.append(LLMMessage(role="system", content=system_message))
            if user_message:
                messages.append(LLMMessage(role="user", content=user_message))

        if not messages:
            raise ValueError("Either 'messages' or 'system_message'/'user_message' must be provided")

        return self.complete(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format
        )

    def complete_stream(
        self,
        messages: List[LLMMessage],
        on_token_callback: Optional[Callable[[str], bool]] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        response_format: Optional[Dict] = None
    ) -> LLMResponse:
        """
        Send messages to OpenAI and get response with streaming.

        WHY: Enables real-time validation during code generation.
             Callback can stop generation if hallucination detected.

        Args:
            messages: Conversation history
            on_token_callback: Called for each token, returns True to continue or False to stop
            model: Model to use (default: gpt-4o)
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            response_format: Optional format spec

        Returns:
            LLMResponse with full content (accumulated from stream)
        """
        # Convert our LLMMessage format to OpenAI format
        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        # Default model
        if model is None:
            model = "gpt-4o"

        # Build API call kwargs
        api_kwargs = {
            "model": model,
            "messages": openai_messages,
            "temperature": temperature,
            "stream": True  # Enable streaming
        }

        # Handle model-specific parameters (same logic as complete())
        if model.startswith("o1") or model.startswith("gpt-5"):
            del api_kwargs["temperature"]
            api_kwargs["max_completion_tokens"] = max_tokens
        else:
            api_kwargs["max_completion_tokens"] = max_tokens

        if response_format:
            api_kwargs["response_format"] = response_format

        # Call OpenAI API with streaming
        stream = self.client.chat.completions.create(**api_kwargs)

        # Accumulate streamed content (avoid nested ifs - extract to helper)
        full_content, stopped_early = self._process_openai_stream(stream, on_token_callback)

        # Build usage info (estimate if stopped early)
        usage = {
            "prompt_tokens": 0,  # Not available in streaming
            "completion_tokens": len(full_content.split()),  # Estimate
            "total_tokens": len(full_content.split())
        }

        return LLMResponse(
            content=full_content,
            model=model,
            provider="openai",
            usage=usage,
            raw_response={"stopped_early": stopped_early}
        )

    def _process_openai_stream(
        self,
        stream,
        on_token_callback: Optional[Callable[[str], bool]]
    ) -> Tuple[str, bool]:
        """
        Process OpenAI stream and accumulate tokens.

        WHY: Extracted from complete_stream() to avoid nested ifs.
        PATTERNS: Early return pattern when callback stops generation.

        Returns:
            Tuple of (full_content, stopped_early)
        """
        full_content = ""
        stopped_early = False

        for chunk in stream:
            # Skip chunks without content (early return pattern)
            if not chunk.choices[0].delta.content:
                continue

            token = chunk.choices[0].delta.content
            full_content += token

            # Process callback if provided (avoid nested ifs)
            should_stop = self._process_token_callback(token, on_token_callback)
            if should_stop:
                stopped_early = True
                break

        return full_content, stopped_early

    def _process_token_callback(
        self,
        token: str,
        callback: Optional[Callable[[str], bool]]
    ) -> bool:
        """
        Process token callback.

        WHY: Extracted to avoid nested ifs in stream processing.
        PERFORMANCE: Early return if no callback.

        Returns:
            True if generation should stop, False otherwise
        """
        # Early return if no callback (avoid nested if)
        if not callback:
            return False

        should_continue = callback(token)
        return not should_continue  # Return True to stop

    def get_available_models(self) -> List[str]:
        """Get available OpenAI models"""
        return [
            "gpt-5",  # Latest GPT-5 (supports temperature)
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
            "o1-preview",  # Reasoning model (no temperature support)
            "o1-mini"  # Reasoning model (no temperature support)
        ]


class AnthropicClient(LLMClientInterface):
    """
    Anthropic API client

    Single Responsibility: Handle Anthropic API communication only
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ConfigurationError(
                "Anthropic API key not provided and ANTHROPIC_API_KEY env var not set",
                context={"provider": "anthropic"}
            )

        # Import Anthropic library (lazy import)
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError("anthropic library not installed. Run: pip install anthropic")

    def complete(
        self,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        response_format: Optional[Dict] = None
    ) -> LLMResponse:
        """Send messages to Anthropic and get response"""
        # Anthropic requires system message to be separate
        system_message = None
        anthropic_messages = []

        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                anthropic_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

        # Default model
        if model is None:
            model = "claude-sonnet-4-5-20250929"  # Claude Sonnet 4.5

        # Note: Anthropic doesn't support response_format parameter
        # JSON mode is achieved through prompt engineering for Claude

        # Call Anthropic API
        kwargs = {
            "model": model,
            "messages": anthropic_messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        if system_message:
            kwargs["system"] = system_message

        response = self.client.messages.create(**kwargs)

        # Extract response
        content = response.content[0].text

        # Build usage info
        usage = {
            "prompt_tokens": response.usage.input_tokens,
            "completion_tokens": response.usage.output_tokens,
            "total_tokens": response.usage.input_tokens + response.usage.output_tokens
        }

        return LLMResponse(
            content=content,
            model=response.model,
            provider="anthropic",
            usage=usage,
            raw_response=response.model_dump()
        )

    def complete_stream(
        self,
        messages: List[LLMMessage],
        on_token_callback: Optional[Callable[[str], bool]] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        response_format: Optional[Dict] = None
    ) -> LLMResponse:
        """
        Send messages to Anthropic and get response with streaming.

        WHY: Enables real-time validation during code generation.
             Callback can stop generation if hallucination detected.

        Args:
            messages: Conversation history
            on_token_callback: Called for each token, returns True to continue or False to stop
            model: Model to use (default: claude-sonnet-4-5)
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            response_format: Not supported by Anthropic (ignored)

        Returns:
            LLMResponse with full content (accumulated from stream)
        """
        # Anthropic requires system message to be separate
        system_message = None
        anthropic_messages = []

        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                anthropic_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

        # Default model
        if model is None:
            model = "claude-sonnet-4-5-20250929"

        # Call Anthropic API with streaming
        kwargs = {
            "model": model,
            "messages": anthropic_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True  # Enable streaming
        }

        if system_message:
            kwargs["system"] = system_message

        stream = self.client.messages.stream(**kwargs)

        # Accumulate streamed content (avoid nested ifs - extract to helper)
        full_content, stopped_early = self._process_anthropic_stream(stream, on_token_callback)

        # Build usage info (estimate if stopped early)
        usage = {
            "prompt_tokens": 0,  # Not available in streaming
            "completion_tokens": len(full_content.split()),  # Estimate
            "total_tokens": len(full_content.split())
        }

        return LLMResponse(
            content=full_content,
            model=model,
            provider="anthropic",
            usage=usage,
            raw_response={"stopped_early": stopped_early}
        )

    def _process_anthropic_stream(
        self,
        stream,
        on_token_callback: Optional[Callable[[str], bool]]
    ) -> Tuple[str, bool]:
        """
        Process Anthropic stream and accumulate tokens.

        WHY: Extracted from complete_stream() to avoid nested ifs.
        PATTERNS: Early return pattern when callback stops generation.

        Returns:
            Tuple of (full_content, stopped_early)
        """
        full_content = ""
        stopped_early = False

        with stream as message_stream:
            for text in message_stream.text_stream:
                full_content += text

                # Process callback if provided (avoid nested ifs)
                # Reuse OpenAI's callback processor (same logic)
                should_stop = self._process_token_callback(text, on_token_callback)
                if should_stop:
                    stopped_early = True
                    break

        return full_content, stopped_early

    def _process_token_callback(
        self,
        token: str,
        callback: Optional[Callable[[str], bool]]
    ) -> bool:
        """
        Process token callback.

        WHY: Extracted to avoid nested ifs in stream processing.
        PERFORMANCE: Early return if no callback.

        Returns:
            True if generation should stop, False otherwise
        """
        # Early return if no callback (avoid nested if)
        if not callback:
            return False

        should_continue = callback(token)
        return not should_continue  # Return True to stop

    def get_available_models(self) -> List[str]:
        """Get available Anthropic models"""
        return [
            "claude-sonnet-4-5-20250929",
            "claude-sonnet-4-20250514",
            "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]


class LLMClientFactory:
    """
    Factory for creating LLM clients

    Single Responsibility: Create appropriate LLM client based on provider
    Open/Closed: Can add new providers without modifying existing code
    """

    # Strategy pattern: Dictionary mapping instead of if/elif chain (SOLID: Open/Closed)
    _PROVIDER_STRATEGIES = {
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
        """
        client_class = LLMClientFactory._PROVIDER_STRATEGIES.get(provider)

        if not client_class:
            raise ConfigurationError(
                f"Unsupported provider: {provider}",
                context={
                    "provider": str(provider),
                    "supported": list(LLMClientFactory._PROVIDER_STRATEGIES.keys())
                }
            )

        return client_class(api_key=api_key)

    # Strategy pattern: Dictionary mapping for provider string -> enum (no if/elif chains)
    _PROVIDER_STRING_MAP = {
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


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_llm_client(
    provider: str = "openai",
    api_key: Optional[str] = None
) -> LLMClientInterface:
    """
    Convenience function to create LLM client

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
    if provider.lower() == "openai":
        return LLMClientFactory.create(LLMProvider.OPENAI, api_key)
    elif provider.lower() == "anthropic":
        return LLMClientFactory.create(LLMProvider.ANTHROPIC, api_key)
    else:
        raise ConfigurationError(
            f"Invalid provider: {provider}",
            context={"provider": provider, "supported": ["openai", "anthropic"]}
        )


# Type alias for backwards compatibility - but keep Factory methods accessible
class LLMClient:
    """
    Backwards compatibility wrapper

    Provides both type compatibility (for isinstance checks) and factory methods
    """
    @staticmethod
    def create_from_env() -> LLMClientInterface:
        """Create LLM client from environment variables"""
        return LLMClientFactory.create_from_env()

    @staticmethod
    def create(provider: LLMProvider, api_key: Optional[str] = None) -> LLMClientInterface:
        """Create LLM client"""
        return LLMClientFactory.create(provider, api_key)


# ============================================================================
# MAIN - TESTING
# ============================================================================

if __name__ == "__main__":
    """Test LLM client"""
    import sys

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
