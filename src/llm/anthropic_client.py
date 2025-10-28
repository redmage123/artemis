#!/usr/bin/env python3
"""
Anthropic Client - Anthropic API implementation

WHY: Isolate Anthropic-specific API communication.
RESPONSIBILITY: Handle all Anthropic API interactions.
PATTERNS: Strategy Pattern, Adapter Pattern.

Single Responsibility: Handle Anthropic API communication only
"""

import os
from typing import List, Optional, Dict, Callable, Tuple

from llm.llm_interface import LLMClientInterface
from llm.llm_models import LLMMessage, LLMResponse
from llm.stream_processor import StreamProcessor
from artemis_exceptions import ConfigurationError


class AnthropicClient(LLMClientInterface):
    """
    Anthropic API client

    WHY: Adapter for Anthropic's API to our standardized interface.
    RESPONSIBILITY: Translate between our interface and Anthropic's API.
    PATTERNS: Adapter Pattern, Lazy Loading.

    BENEFITS:
    - Isolates Anthropic-specific code
    - Easy to update when Anthropic API changes
    - Can be mocked for testing
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Anthropic client

        WHY: Lazy initialization of Anthropic library (only loaded if needed).
        PATTERNS: Lazy loading, Guard clause for API key validation.

        Args:
            api_key: Optional API key (uses ANTHROPIC_API_KEY env var if not provided)

        Raises:
            ConfigurationError: If API key not provided and env var not set
            ImportError: If anthropic library not installed
        """
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
        """
        Send messages to Anthropic and get response

        WHY: Primary completion interface for Anthropic.
        RESPONSIBILITY: Execute synchronous Anthropic API call.
        PATTERNS: Guard clauses, system message extraction.

        Args:
            messages: Conversation history
            model: Model to use (default: claude-sonnet-4-5)
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            response_format: Not supported by Anthropic (ignored)

        Returns:
            Standardized LLMResponse
        """
        # Anthropic requires system message to be separate
        system_message, anthropic_messages = self._extract_system_message(messages)

        # Default model
        if model is None:
            model = "claude-sonnet-4-5-20250929"  # Claude Sonnet 4.5

        # Build API call kwargs
        kwargs = self._build_api_kwargs(model, anthropic_messages, temperature, max_tokens, system_message)

        # Note: Anthropic doesn't support response_format parameter
        # JSON mode is achieved through prompt engineering for Claude

        # Call Anthropic API
        response = self.client.messages.create(**kwargs)

        # Extract and return standardized response
        return self._build_response(response)

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

        RESPONSIBILITY: Execute streaming Anthropic API call.
        PATTERNS: Observer pattern for token callbacks.

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
        system_message, anthropic_messages = self._extract_system_message(messages)

        # Default model
        if model is None:
            model = "claude-sonnet-4-5-20250929"

        # Build API call kwargs
        kwargs = self._build_api_kwargs(model, anthropic_messages, temperature, max_tokens, system_message)
        kwargs["stream"] = True  # Enable streaming

        # Call Anthropic API with streaming
        stream = self.client.messages.stream(**kwargs)

        # Accumulate streamed content
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

    def get_available_models(self) -> List[str]:
        """
        Get available Anthropic models

        WHY: Enable model discovery and validation.
        RESPONSIBILITY: Return list of supported Anthropic models.

        Returns:
            List of Anthropic model identifiers
        """
        return [
            "claude-sonnet-4-5-20250929",
            "claude-sonnet-4-20250514",
            "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]

    def _extract_system_message(self, messages: List[LLMMessage]) -> Tuple[Optional[str], List[Dict]]:
        """
        Extract system message and convert to Anthropic format

        WHY: Anthropic requires system message to be separate from messages array.
        RESPONSIBILITY: Separate system message and convert other messages.
        PATTERNS: Early return pattern, list comprehension.

        Args:
            messages: List of LLMMessage objects

        Returns:
            Tuple of (system_message, anthropic_messages)
        """
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

        return system_message, anthropic_messages

    def _build_api_kwargs(
        self,
        model: str,
        messages: List[Dict],
        temperature: float,
        max_tokens: int,
        system_message: Optional[str]
    ) -> Dict:
        """
        Build Anthropic API kwargs

        WHY: Centralize API parameter construction.
        RESPONSIBILITY: Build kwargs with optional system message.
        PATTERNS: Guard clause for system message.

        Args:
            model: Model identifier
            messages: Anthropic-format messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            system_message: Optional system message

        Returns:
            Dictionary of API kwargs
        """
        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        if system_message:
            kwargs["system"] = system_message

        return kwargs

    def _build_response(self, response) -> LLMResponse:
        """
        Build standardized response from Anthropic response

        WHY: Centralize response parsing logic.
        RESPONSIBILITY: Convert Anthropic response to our standard format.

        Args:
            response: Anthropic API response object

        Returns:
            Standardized LLMResponse
        """
        content = response.content[0].text

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

    def _process_anthropic_stream(
        self,
        stream,
        on_token_callback: Optional[Callable[[str], bool]]
    ) -> Tuple[str, bool]:
        """
        Process Anthropic stream and accumulate tokens.

        WHY: Extracted from complete_stream() to avoid nested ifs.
        PATTERNS: Early return pattern when callback stops generation.

        Args:
            stream: Anthropic stream object
            on_token_callback: Optional callback for each token

        Returns:
            Tuple of (full_content, stopped_early)
        """
        full_content = ""
        stopped_early = False

        with stream as message_stream:
            for text in message_stream.text_stream:
                full_content += text

                # Process callback if provided
                should_stop = StreamProcessor.process_token_callback(text, on_token_callback)
                if should_stop:
                    stopped_early = True
                    break

        return full_content, stopped_early
