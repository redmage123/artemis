#!/usr/bin/env python3
"""
LLM Models - Data structures for LLM communication

WHY: Centralize all data models used across LLM clients.
RESPONSIBILITY: Define standardized message and response formats.
PATTERNS: Dataclass pattern for immutable data structures.

Single Responsibility: Define data structures only
Open/Closed: Can extend with new fields without breaking existing code
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict


class LLMProvider(Enum):
    """
    Supported LLM providers

    WHY: Type-safe provider selection instead of strings.
    BENEFITS: Compile-time checking, IDE autocomplete.
    """
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


@dataclass
class LLMMessage:
    """
    Represents a message in a conversation

    WHY: Standardize message format across all providers.
    RESPONSIBILITY: Hold message role and content.

    Attributes:
        role: Message role ("system", "user", "assistant")
        content: Message text content
    """
    role: str
    content: str


@dataclass
class LLMResponse:
    """
    Standardized response from any LLM provider

    WHY: Unify responses from different providers (OpenAI, Anthropic).
    RESPONSIBILITY: Hold LLM response data with usage metrics.
    BENEFITS: Provider-agnostic response handling.

    Attributes:
        content: Generated text response
        model: Model identifier used for generation
        provider: Provider name (openai, anthropic)
        usage: Token usage stats (prompt, completion, total)
        raw_response: Full API response for debugging
    """
    content: str
    model: str
    provider: str
    usage: Dict[str, int]  # {"prompt_tokens": X, "completion_tokens": Y, "total_tokens": Z}
    raw_response: Dict  # Full API response for debugging
