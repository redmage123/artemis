#!/usr/bin/env python3
"""
OpenAI Client - OpenAI API implementation

WHY: Isolate OpenAI-specific API communication.
RESPONSIBILITY: Handle all OpenAI API interactions.
PATTERNS: Strategy Pattern, Adapter Pattern.

Single Responsibility: Handle OpenAI API communication only
"""

import os
from typing import List, Optional, Dict, Callable, Tuple

from llm.llm_interface import LLMClientInterface
from llm.llm_models import LLMMessage, LLMResponse
from llm.stream_processor import StreamProcessor
from artemis_exceptions import ConfigurationError


class OpenAIClient(LLMClientInterface):
    """
    OpenAI API client

    WHY: Adapter for OpenAI's API to our standardized interface.
    RESPONSIBILITY: Translate between our interface and OpenAI's API.
    PATTERNS: Adapter Pattern, Lazy Loading.

    BENEFITS:
    - Isolates OpenAI-specific code
    - Easy to update when OpenAI API changes
    - Can be mocked for testing
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenAI client

        WHY: Lazy initialization of OpenAI library (only loaded if needed).
        PATTERNS: Lazy loading, Guard clause for API key validation.

        Args:
            api_key: Optional API key (uses OPENAI_API_KEY env var if not provided)

        Raises:
            ConfigurationError: If API key not provided and env var not set
            ImportError: If openai library not installed
        """
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
        """
        Send messages to OpenAI and get response

        WHY: Primary completion interface for OpenAI.
        RESPONSIBILITY: Execute synchronous OpenAI API call.
        PATTERNS: Guard clauses, dispatch table for model-specific params.

        Args:
            messages: Conversation history
            model: Model to use (default: gpt-4o)
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            response_format: Optional format spec (e.g., {"type": "json_object"})

        Returns:
            Standardized LLMResponse
        """
        # Convert our LLMMessage format to OpenAI format
        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        # Default model
        if model is None:
            model = "gpt-4o"  # Latest GPT-4o model (supports temperature)

        # Build API call kwargs
        api_kwargs = self._build_api_kwargs(model, openai_messages, temperature, max_tokens)

        # Add response_format if specified (for JSON mode)
        if response_format:
            api_kwargs["response_format"] = response_format

        # Call OpenAI API
        response = self.client.chat.completions.create(**api_kwargs)

        # Extract and return standardized response
        return self._build_response(response)

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

        WHY: Backward compatibility with existing code.
        RESPONSIBILITY: Convert string messages to LLMMessage format.

        Supports two calling conventions:
        1. messages parameter (List[LLMMessage])
        2. system_message + user_message parameters (strings)

        Args:
            messages: Optional list of LLMMessage objects
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            response_format: Optional format spec
            system_message: Optional system message (alternative to messages)
            user_message: Optional user message (alternative to messages)

        Returns:
            Standardized LLMResponse

        Raises:
            ValueError: If neither messages nor system_message/user_message provided
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

        RESPONSIBILITY: Execute streaming OpenAI API call.
        PATTERNS: Observer pattern for token callbacks.

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
        api_kwargs = self._build_api_kwargs(model, openai_messages, temperature, max_tokens)
        api_kwargs["stream"] = True  # Enable streaming

        if response_format:
            api_kwargs["response_format"] = response_format

        # Call OpenAI API with streaming
        stream = self.client.chat.completions.create(**api_kwargs)

        # Accumulate streamed content
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

    def get_available_models(self) -> List[str]:
        """
        Get available OpenAI models

        WHY: Enable model discovery and validation.
        RESPONSIBILITY: Return list of supported OpenAI models.

        Returns:
            List of OpenAI model identifiers
        """
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

    def _build_api_kwargs(
        self,
        model: str,
        messages: List[Dict],
        temperature: float,
        max_tokens: int
    ) -> Dict:
        """
        Build OpenAI API kwargs

        WHY: Centralize model-specific parameter handling.
        RESPONSIBILITY: Handle differences between model families (o1, gpt-4o, etc.).
        PATTERNS: Dispatch table pattern for model-specific logic.

        Args:
            model: Model identifier
            messages: OpenAI-format messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens

        Returns:
            Dictionary of API kwargs
        """
        api_kwargs = {
            "model": model,
            "messages": messages,
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
            api_kwargs["max_completion_tokens"] = max_tokens

        return api_kwargs

    def _build_response(self, response) -> LLMResponse:
        """
        Build standardized response from OpenAI response

        WHY: Centralize response parsing logic.
        RESPONSIBILITY: Convert OpenAI response to our standard format.

        Args:
            response: OpenAI API response object

        Returns:
            Standardized LLMResponse
        """
        content = response.choices[0].message.content

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

    def _process_openai_stream(
        self,
        stream,
        on_token_callback: Optional[Callable[[str], bool]]
    ) -> Tuple[str, bool]:
        """
        Process OpenAI stream and accumulate tokens.

        WHY: Extracted from complete_stream() to avoid nested ifs.
        PATTERNS: Early return pattern when callback stops generation.

        Args:
            stream: OpenAI stream object
            on_token_callback: Optional callback for each token

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
            should_stop = StreamProcessor.process_token_callback(token, on_token_callback)
            if should_stop:
                stopped_early = True
                break

        return full_content, stopped_early
