#!/usr/bin/env python3
"""
WHY: Define rate limit configurations for LLM providers
RESPONSIBILITY: Centralize provider-specific limits
PATTERNS: Configuration object, Dispatch table

Provider limits based on official API documentation (2025).
"""

from typing import Dict


# Dispatch table: OpenAI model limits
OPENAI_LIMITS: Dict[str, Dict[str, int]] = {
    "gpt-4o": {
        "requests_per_minute": 100,
        "tokens_per_minute": 20000
    },
    "gpt-4o-mini": {
        "requests_per_minute": 300,
        "tokens_per_minute": 100000
    },
    "default": {
        "requests_per_minute": 50,
        "tokens_per_minute": 10000
    }
}


# Dispatch table: Anthropic model limits
ANTHROPIC_LIMITS: Dict[str, Dict[str, int]] = {
    "claude-sonnet-4-5": {
        "requests_per_minute": 50,
        "tokens_per_minute": 10000
    },
    "default": {
        "requests_per_minute": 30,
        "tokens_per_minute": 5000
    }
}
