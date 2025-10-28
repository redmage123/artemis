#!/usr/bin/env python3
"""
LLM Package - Unified Interface for Multiple LLM Providers

WHY: Modularize LLM client code into focused, single-responsibility modules.
RESPONSIBILITY: Export all public components for package users.
PATTERNS: Facade Pattern, Package Organization.

Package Structure:
    llm_models.py        - Data structures (LLMMessage, LLMResponse, LLMProvider)
    llm_interface.py     - Abstract base class (LLMClientInterface)
    openai_client.py     - OpenAI API implementation
    anthropic_client.py  - Anthropic API implementation
    llm_factory.py       - Client factory for provider selection
    stream_processor.py  - Token callback processing for streaming

Benefits:
    - Single Responsibility: Each module has one clear purpose
    - Open/Closed: Add new providers without modifying existing code
    - Easier testing: Mock individual components
    - Better maintainability: Changes isolated to specific modules
"""

# Export all public components
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

__all__ = [
    # Models
    "LLMProvider",
    "LLMMessage",
    "LLMResponse",
    # Interface
    "LLMClientInterface",
    # Clients
    "OpenAIClient",
    "AnthropicClient",
    # Factory
    "LLMClientFactory",
    # Utilities
    "StreamProcessor",
]
