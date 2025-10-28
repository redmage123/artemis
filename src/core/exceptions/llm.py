#!/usr/bin/env python3
"""
Module: core/exceptions/llm.py

WHY: Centralizes all LLM/API related exceptions. LLM errors need special handling
     (rate limits = retry, auth errors = fail fast, timeouts = retry with backoff).
     This module isolates LLM concerns for intelligent error recovery.

RESPONSIBILITY: Define LLM-specific exception types for API calls, parsing,
                rate limits, and authentication. Single Responsibility - only LLM.

PATTERNS: Exception Hierarchy Pattern, Error Classification Pattern
          - Hierarchy: Base LLMException with specific subtypes
          - Classification: Retryable (rate limit) vs permanent (auth) errors

Integration: Used by llm_client.py, ai_orchestration_planner.py, all developer agents,
             and any component that calls OpenAI, Anthropic, or other LLM APIs.

Design Decision: Why separate LLM from general API exceptions?
    LLM errors have unique retry/backoff requirements, cost implications, and
    rate limit handling. Separate module enables LLM-specific error strategies.
"""

from core.exceptions.base import ArtemisException


class LLMException(ArtemisException):
    """
    Base exception for LLM-related errors.

    WHY: Enables catching all LLM errors with single except clause.
         LLM errors often need special handling (retry, fallback, cost tracking).

    RESPONSIBILITY: Base class for all LLM API and processing errors.

    PATTERNS: Exception Hierarchy - specific subtypes inherit from this

    Use case:
        try:
            llm_call()
        except LLMException as e:  # Catches all LLM errors
            log_llm_error(e)
            use_fallback_model()
    """
    pass


# Alias for compatibility with AIQueryService
LLMError = LLMException


class LLMClientError(LLMException):
    """
    Error initializing or using LLM client.

    WHY: Client initialization errors (missing config, invalid model) should
         fail fast rather than retry. Distinguishes setup errors from API errors.

    Example context:
        {"client": "openai", "model": "gpt-4", "config_file": "/path/to/config"}
    """
    pass


class LLMAPIError(LLMException):
    """
    Error calling LLM API (OpenAI, Anthropic, etc.).

    WHY: API errors may be transient (network) or permanent (invalid request).
         This base class covers general API failures, specific subtypes handle
         rate limits and auth separately.

    Example context:
        {"provider": "openai", "endpoint": "/v1/chat/completions",
         "status_code": 500, "attempt": 3}
    """
    pass


class LLMResponseParsingError(LLMException):
    """
    Error parsing LLM response (invalid JSON, missing fields, etc.).

    WHY: Parsing errors indicate LLM returned unexpected format. May need
         prompt adjustment or fallback parsing. Different from API errors.

    PERFORMANCE: Parsing errors don't consume API quota, safe to retry with
                 modified prompt.

    Example context:
        {"response": "partial response...", "expected_format": "json",
         "parser": "json.loads", "error": "JSONDecodeError"}
    """
    pass


class LLMRateLimitError(LLMException):
    """
    LLM API rate limit exceeded.

    WHY: Rate limit errors are RETRYABLE with exponential backoff.
         Must be distinct from other errors to enable retry logic.
         This is a transient error, not a permanent failure.

    PATTERNS: Retryable Error Pattern - orchestrator retries with backoff

    Example context:
        {"provider": "openai", "limit_type": "requests_per_minute",
         "retry_after": 60, "current_usage": 150, "limit": 100}
    """
    pass


class LLMAuthenticationError(LLMException):
    """
    LLM API authentication failed (invalid API key, expired token, etc.).

    WHY: Authentication errors are PERMANENT - do not retry. Must fail fast
         and alert user to fix credentials. Distinct from transient errors.

    PATTERNS: Fail Fast Pattern - no retry, immediate user notification

    Example context:
        {"provider": "anthropic", "key_length": 20, "error": "invalid_api_key"}
    """
    pass
