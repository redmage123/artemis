#!/usr/bin/env python3
"""
LLM API Workflow Handlers

WHY:
Handles LLM API issues including provider switching, rate limiting,
request retries, and response validation.

RESPONSIBILITY:
- Switch between LLM providers (OpenAI, Anthropic)
- Retry failed LLM requests with backoff
- Handle rate limit errors
- Validate and sanitize LLM responses

PATTERNS:
- Strategy Pattern: Different LLM provider strategies
- Retry Pattern: Exponential backoff for transient failures
- Guard Clauses: Validate responses before processing

INTEGRATION:
- Extends: WorkflowHandler base class
- Used by: WorkflowHandlerFactory for LLM actions
- Imported from: artemis_constants for retry configuration
"""

import time
import json
import re
from typing import Dict, Any

from artemis_constants import MAX_RETRY_ATTEMPTS, RETRY_BACKOFF_FACTOR
from workflows.handlers.base_handler import WorkflowHandler
from artemis_logger import get_logger

logger = get_logger("workflow.llm_handlers")


class SwitchLLMProviderHandler(WorkflowHandler):
    """
    Switch to backup LLM provider

    WHY: Provide failover when primary LLM provider is unavailable
    RESPONSIBILITY: Toggle between OpenAI and Anthropic providers
    """

    def handle(self, context: Dict[str, Any]) -> bool:
        current_provider = context.get("current_provider", "openai")

        if current_provider == "openai":
            context["llm_provider"] = "anthropic"
            print("[Workflow] Switched from OpenAI to Anthropic")
        else:
            context["llm_provider"] = "openai"
            print("[Workflow] Switched from Anthropic to OpenAI")

        return True


class RetryLLMRequestHandler(WorkflowHandler):
    """
    Retry LLM request with backoff

    WHY: Handle transient LLM API failures gracefully
    RESPONSIBILITY: Retry requests with exponential backoff
    PATTERNS: Exponential backoff retry strategy
    """

    def __init__(self):
        self.context = {}

    def handle(self, context: Dict[str, Any]) -> bool:
        self.context = context
        for attempt in range(MAX_RETRY_ATTEMPTS):
            if self._attempt_llm_request(attempt):
                return True

            if attempt == MAX_RETRY_ATTEMPTS - 1:
                return False

        return False

    def _attempt_llm_request(self, attempt: int) -> bool:
        try:
            # Wait with exponential backoff before retry (skip on first attempt)
            if attempt > 0:
                wait_time = RETRY_BACKOFF_FACTOR ** attempt
                logger.info(f"Waiting {wait_time}s before LLM retry {attempt + 1}/{MAX_RETRY_ATTEMPTS}")
                time.sleep(wait_time)

            logger.info(f"LLM retry attempt {attempt + 1}/{MAX_RETRY_ATTEMPTS}")

            # Get LLM client and request parameters from context
            llm_client = self.context.get("llm_client")
            prompt = self.context.get("prompt")
            model = self.context.get("model")

            if not llm_client:
                logger.warning("No LLM client provided in context for retry")
                return False

            if not prompt:
                logger.warning("No prompt provided in context for LLM retry")
                return False

            # Attempt to call the LLM
            response = self._call_llm_client(llm_client, prompt, model)
            if response is None:
                return False

            # Store response in context
            self.context["llm_response"] = response
            logger.info(f"LLM request succeeded on attempt {attempt + 1}")
            return True

        except Exception as e:
            logger.warning(f"LLM request failed on attempt {attempt + 1}: {e}")
            return False

    @staticmethod
    def _call_llm_client(llm_client, prompt: str, model: str):
        """
        Call LLM client using supported method.

        WHY: Separate method selection to avoid nested control flow
        RESPONSIBILITY: Dispatch to appropriate LLM client method
        PATTERNS: Dispatch strategy with guard clauses
        """
        # Try query method
        if hasattr(llm_client, "query"):
            return llm_client.query(prompt, model=model)

        # Try generate method
        if hasattr(llm_client, "generate"):
            return llm_client.generate(prompt, model=model)

        # Try chat_completion method
        if hasattr(llm_client, "chat_completion"):
            return llm_client.chat_completion(prompt, model=model)

        # No supported method found
        logger.error("LLM client does not have a supported method (query/generate/chat_completion)")
        return None


class HandleRateLimitHandler(WorkflowHandler):
    """
    Handle LLM rate limit

    WHY: Respect API rate limits to avoid request rejection
    RESPONSIBILITY: Wait specified duration before retrying
    """

    def handle(self, context: Dict[str, Any]) -> bool:
        wait_time = context.get("wait_time", 60)

        print(f"[Workflow] Rate limited, waiting {wait_time}s...")
        time.sleep(wait_time)

        return True


class ValidateLLMResponseHandler(WorkflowHandler):
    """
    Validate and sanitize LLM response

    WHY: Ensure LLM responses are valid before processing
    RESPONSIBILITY: Validate response format and content
    PATTERNS: Guard clauses for validation logic
    """

    def handle(self, context: Dict[str, Any]) -> bool:
        response = context.get("llm_response", "")

        # Basic validation checks
        if not response or len(response) == 0:
            logger.error("Invalid LLM response: empty response")
            return False

        # Check minimum length
        min_length = context.get("min_response_length", 10)
        if len(response) < min_length:
            logger.error(f"Invalid LLM response: too short (length={len(response)}, min={min_length})")
            return False

        # Check for common error patterns
        error_patterns = [
            r"error",
            r"failed",
            r"unable to",
            r"cannot",
            r"invalid",
            r"timeout",
            r"rate limit",
        ]

        # Only fail if error appears in first 100 chars (likely an error message)
        response_start = response[:100].lower()
        for pattern in error_patterns:
            if re.search(pattern, response_start, re.IGNORECASE):
                logger.warning(f"LLM response may contain error (pattern: {pattern})")
                # Don't fail - just warn, as these words might appear in valid responses

        # Check for required format if specified
        required_format = context.get("required_format")
        if required_format == "json":
            try:
                json.loads(response)
                logger.info("LLM response validated: valid JSON")
            except json.JSONDecodeError as e:
                logger.error(f"Invalid LLM response: expected JSON but got parse error: {e}")
                return False

        elif required_format == "markdown":
            # Basic markdown validation - check for common markdown elements
            self._validate_markdown_response(response)

        # Check for truncation indicators
        truncation_indicators = ["...", "[truncated]", "[cut off]"]
        for indicator in truncation_indicators:
            if indicator in response[-50:]:
                logger.warning(f"LLM response appears truncated (found: {indicator})")

        logger.info("LLM response validated successfully")
        return True

    @staticmethod
    def _validate_markdown_response(response: str) -> None:
        """
        Validate markdown response format.

        WHY: Separate markdown validation to avoid nested control flow
        RESPONSIBILITY: Check for common markdown markers
        PATTERNS: Guard clause
        """
        # Guard: Has markdown markers
        if any(marker in response for marker in ["#", "**", "*", "-", "`", "```"]):
            return

        # No markdown markers found - just warn
        logger.warning("LLM response may not be valid markdown (no markdown markers found)")
