"""
Module: agents/developer/llm_client_wrapper.py

WHY: Wrap LLM client with developer-specific logic and streaming validation.
RESPONSIBILITY: Handle all LLM API calls with validation, parsing, and error handling.
PATTERNS: Strategy Pattern (streaming vs standard), Callback Pattern, Guard Clauses.

This module handles:
- LLM API calls with developer-specific system prompts
- Streaming validation for real-time hallucination detection
- JSON response parsing and validation
- Debug logging of prompts and responses

EXTRACTED FROM: standalone_developer_agent.py (lines 1729-1905)
"""

import os
import json
from typing import Dict, List, Optional
from artemis_stage_interface import LoggerInterface
from llm_client import LLMMessage, LLMResponse
from artemis_exceptions import LLMResponseParsingError, create_wrapped_exception

# Import validation integration
try:
    from validation import (
        get_validation_strategy_for_task,
        get_validation_summary_for_llm,
        ValidationStrategy
    )
    VALIDATION_INTEGRATION_AVAILABLE = True
except ImportError:
    VALIDATION_INTEGRATION_AVAILABLE = False

# Import StreamingValidator if available
try:
    from streaming_validator import StreamingValidatorFactory, StreamingValidationResult
    STREAMING_VALIDATOR_AVAILABLE = True
except ImportError:
    STREAMING_VALIDATOR_AVAILABLE = False


class LLMClientWrapper:
    """
    Wraps LLM client with developer-specific functionality

    WHY: Centralize LLM interactions with consistent validation and error handling
    PATTERNS: Strategy Pattern, Callback Pattern, Guard Clauses
    """

    def __init__(
        self,
        llm_client,
        developer_name: str,
        developer_type: str,
        llm_provider: str,
        llm_model: Optional[str] = None,
        logger: Optional[LoggerInterface] = None,
        enable_validation_awareness: bool = True
    ):
        """
        Initialize LLM client wrapper

        Args:
            llm_client: LLM client instance
            developer_name: Name of developer (e.g., "developer-a")
            developer_type: Type of developer (e.g., "conservative")
            llm_provider: Provider name (e.g., "openai", "anthropic")
            llm_model: Model name (optional)
            logger: Optional logger
            enable_validation_awareness: Include validation pipeline info in prompts
        """
        self.llm_client = llm_client
        self.developer_name = developer_name
        self.developer_type = developer_type
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self.logger = logger
        self.enable_validation_awareness = enable_validation_awareness and VALIDATION_INTEGRATION_AVAILABLE

    def call_llm(
        self,
        prompt: str,
        task_type: str = "code_generation",
        code_complexity: Optional[int] = None,
        is_critical: bool = False,
        has_tests: bool = True
    ) -> LLMResponse:
        """
        Call LLM API with prompt

        Args:
            prompt: User prompt
            task_type: Type of task (for validation strategy selection)
            code_complexity: Estimated code complexity (defaults to prompt length / 10)
            is_critical: Whether code is critical (security, payments, etc.)
            has_tests: Whether tests are expected

        Returns:
            LLM response
        """
        messages = self._build_messages(
            prompt,
            task_type=task_type,
            code_complexity=code_complexity,
            is_critical=is_critical,
            has_tests=has_tests
        )
        self._log_prompt_debug(prompt)

        # Enable JSON mode for OpenAI (Anthropic uses prompt engineering)
        response_format = {"type": "json_object"} if self.llm_provider == "openai" else None

        # Strategy pattern: Use streaming or standard completion
        streaming_validator = self._create_streaming_validator()

        if streaming_validator:
            # Layer 3.6: Streaming Validation (DURING generation)
            response = self._call_llm_with_streaming(messages, response_format, streaming_validator)
        else:
            # Standard completion (no streaming validation)
            response = self.llm_client.complete(
                messages=messages,
                model=self.llm_model,
                temperature=0.7,
                max_tokens=8000,  # Allow longer responses for complete implementations
                response_format=response_format
            )

        self._log_response_debug(response)
        return response

    def parse_implementation(self, content: str) -> Dict:
        """
        Parse implementation from LLM response

        Extracts JSON from response (handles markdown code blocks)

        Args:
            content: LLM response content

        Returns:
            Parsed implementation dict

        Raises:
            LLMResponseParsingError: If JSON parsing fails
        """
        # Try to find JSON in markdown code block
        json_str = self._extract_json_from_content(content)

        try:
            implementation = json.loads(json_str)
            return implementation
        except json.JSONDecodeError as e:
            if self.logger:
                self.logger.log(f"❌ Failed to parse JSON: {e}", "ERROR")
                self.logger.log(f"Raw content:\n{content[:500]}...", "DEBUG")

            raise create_wrapped_exception(
                e,
                LLMResponseParsingError,
                f"Failed to parse implementation JSON from LLM response",
                context={"developer": self.developer_name, "error": str(e)}
            )

    # ========== Private Helper Methods ==========

    def _build_messages(
        self,
        prompt: str,
        task_type: str = "code_generation",
        code_complexity: Optional[int] = None,
        is_critical: bool = False,
        has_tests: bool = True
    ) -> List[LLMMessage]:
        """
        Build LLM messages with developer-specific system prompt

        WHY: Add validation awareness to improve code quality
        PATTERNS: Guard clauses, early returns

        Args:
            prompt: User prompt
            task_type: Type of task (code_generation, refactoring, etc.)
            code_complexity: Estimated code complexity (defaults to prompt length / 10)
            is_critical: Whether code is critical (security, payments, etc.)
            has_tests: Whether tests are expected

        Returns:
            List of LLM messages
        """
        system_prompt = (
            f"You are {self.developer_name}, a {self.developer_type} software developer. "
            f"You follow TDD strictly and apply SOLID principles. "
            f"You write production-quality, complete code. "
            f"You MUST respond with valid JSON only - no explanations, no markdown, just pure JSON."
        )

        # Guard: validation awareness not enabled
        if not self.enable_validation_awareness:
            return [
                LLMMessage(role="system", content=system_prompt),
                LLMMessage(role="user", content=prompt)
            ]

        # Add validation awareness to system prompt
        try:
            # Estimate code size from prompt length if not provided
            if code_complexity is None:
                code_complexity = len(prompt) // 10

            # Get validation strategy for this task
            strategy = get_validation_strategy_for_task(
                task_type=task_type,
                code_size=code_complexity,  # Function expects code_size parameter
                is_critical=is_critical,
                has_tests=has_tests,
                dependencies=0,  # Not available at this level (function expects dependencies parameter)
                logger=self.logger
            )

            # Get concise validation summary
            validation_context = get_validation_summary_for_llm(strategy)

            # Append validation awareness to system prompt
            system_prompt += f"\n\n{validation_context}"

            if self.logger:
                self.logger.log(
                    f"✅ Added validation awareness to system prompt "
                    f"(profile: {strategy.profile.value}, "
                    f"reduction: {strategy.expected_reduction:.0%})",
                    "DEBUG"
                )

        except Exception as e:
            # Guard: validation integration failed - continue without it
            if self.logger:
                self.logger.log(
                    f"⚠️ Failed to add validation awareness: {e}",
                    "WARNING"
                )
            # Continue with base system prompt

        return [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=prompt)
        ]

    def _log_prompt_debug(self, prompt: str):
        """
        Log prompt debug information

        Args:
            prompt: Prompt to log
        """
        # Guard: no logger
        if not self.logger:
            return

        prompt_length = len(prompt)
        self.logger.log(f"📡 Calling {self.llm_provider} API...", "INFO")
        self.logger.log(f"🔍 Prompt length: {prompt_length:,} characters", "DEBUG")
        self.logger.log(f"🔍 Prompt preview (first 1000 chars):\n{prompt[:1000]}", "DEBUG")
        self.logger.log(f"🔍 Prompt preview (last 1000 chars):\n{prompt[-1000:]}", "DEBUG")

        # Check if RAG examples are in the prompt
        if "HIGH-QUALITY" in prompt and "EXAMPLE" in prompt:
            self.logger.log("✅ RAG examples detected in prompt", "DEBUG")
        else:
            self.logger.log("❌ WARNING: No RAG examples found in prompt!", "WARNING")

        # Check if quality requirements are in the prompt
        if "MANDATORY QUALITY REQUIREMENTS" in prompt:
            self.logger.log("✅ Quality requirements detected in prompt", "DEBUG")
        else:
            self.logger.log("❌ WARNING: No quality requirements in prompt!", "WARNING")

    def _log_response_debug(self, response: LLMResponse):
        """
        Log response debug information

        Args:
            response: LLM response
        """
        if self.logger:
            self.logger.log(
                f"✅ Received response ({response.usage['total_tokens']} tokens)",
                "INFO"
            )

    def _create_streaming_validator(self) -> Optional['StreamingValidator']:
        """
        Create streaming validator for real-time validation.

        WHY: Validates code DURING generation, stops hallucinations early.
             Saves tokens and time by stopping generation immediately.
        PATTERNS: Early return pattern (guard clauses).
        PERFORMANCE: Stops generation early on validation failure, saves LLM tokens.

        Returns:
            StreamingValidator if available and enabled, None otherwise
        """
        # Guard: streaming validator not available
        if not STREAMING_VALIDATOR_AVAILABLE:
            return None

        # Guard: streaming validation not enabled
        if not os.getenv("ARTEMIS_ENABLE_STREAMING_VALIDATION", "false").lower() == "true":
            return None

        # Create validator with standard mode
        validator = StreamingValidatorFactory.create_validator(
            mode='standard',  # Can be configured via env var later
            logger=self.logger
        )

        if self.logger:
            self.logger.log(
                "🌊 Streaming validation ENABLED (real-time hallucination detection)",
                "INFO"
            )

        return validator

    def _call_llm_with_streaming(
        self,
        messages: List[LLMMessage],
        response_format: Optional[Dict],
        validator: 'StreamingValidator'
    ) -> LLMResponse:
        """
        Call LLM with streaming validation.

        WHY: Enables real-time validation during code generation.
             Stops generation early if hallucination detected.

        PATTERNS: Callback pattern for streaming validation.

        Args:
            messages: LLM messages
            response_format: Response format dict
            validator: Streaming validator

        Returns:
            LLM response
        """
        # Create callback that validates each token
        def on_token_callback(token: str) -> bool:
            """
            Validate each token during streaming.

            WHY: Called by LLM client for each token.
                 Returns False to stop generation early.

            Args:
                token: Token to validate

            Returns:
                True to continue generation, False to stop
            """
            result = validator.on_token(token)
            return result.should_continue

        # Call LLM with streaming
        response = self.llm_client.complete_stream(
            messages=messages,
            on_token_callback=on_token_callback,
            model=self.llm_model,
            temperature=0.7,
            max_tokens=8000,
            response_format=response_format
        )

        # Log streaming validation statistics
        if self.logger:
            stats = validator.get_stats()
            self.logger.log(
                f"📊 Streaming validation stats: {stats['validation_count']} checks, "
                f"{stats['stop_events']} stops, "
                f"{stats['token_count']} tokens",
                "DEBUG"
            )

        return response

    def _extract_json_from_content(self, content: str) -> str:
        """
        Extract JSON string from content (handles markdown code blocks)

        Args:
            content: Content with potential JSON

        Returns:
            Extracted JSON string
        """
        # Try to find JSON in markdown code block
        if "```json" in content:
            json_start = content.find("```json") + 7
            json_end = content.find("```", json_start)
            return content[json_start:json_end].strip()

        if "```" in content:
            json_start = content.find("```") + 3
            json_end = content.find("```", json_start)
            return content[json_start:json_end].strip()

        # Assume entire content is JSON
        return content.strip()


__all__ = [
    "LLMClientWrapper"
]
