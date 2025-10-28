#!/usr/bin/env python3
"""
LLM Client Interface - Abstract base class for all LLM clients

WHY: Define contract for LLM communication across providers.
RESPONSIBILITY: Specify required methods for any LLM client.
PATTERNS: Strategy Pattern, Interface Segregation Principle.

Single Responsibility: Define contract for LLM communication
Open/Closed: Can implement interface for new providers without changes
Liskov Substitution: All implementations must honor this contract
Interface Segregation: Minimal interface with only essential methods
Dependency Inversion: Depends on abstraction, not concrete implementations
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Callable

from llm.llm_models import LLMMessage, LLMResponse


class LLMClientInterface(ABC):
    """
    Abstract base class for all LLM clients

    WHY: Provides unified interface for multiple LLM providers (OpenAI,
    Anthropic), enabling easy provider switching without code changes.

    DESIGN PATTERN: Strategy Pattern - different providers are interchangeable strategies
    SOLID: Interface Segregation - minimal interface with only essential methods

    BENEFITS:
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

        WHY: Primary interface for LLM completion requests.
        RESPONSIBILITY: Execute synchronous completion request.

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

        WHY: Enables real-time validation during generation.
             Callback can stop generation if hallucination detected.

        RESPONSIBILITY: Execute streaming completion with token-level callbacks.
        PATTERNS: Observer pattern for token callbacks.

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
        """
        pass

    @abstractmethod
    def get_available_models(self) -> List[str]:
        """
        Get list of available models

        WHY: Enable model discovery and validation.
        RESPONSIBILITY: Return provider-specific model list.

        Returns:
            List of model identifiers
        """
        pass
