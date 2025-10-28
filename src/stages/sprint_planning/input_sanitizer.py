#!/usr/bin/env python3
"""
Module: input_sanitizer.py

WHY: Prevent prompt injection attacks in LLM inputs
RESPONSIBILITY: Sanitize and validate user input for LLM prompts
PATTERNS: Guard clauses for early exit on dangerous patterns
"""

from typing import List
from artemis_stage_interface import LoggerInterface


class InputSanitizer:
    """
    WHY: User input to LLMs can contain malicious prompt injection attempts
    RESPONSIBILITY: Detect and neutralize dangerous patterns in user text
    PATTERNS: Strategy pattern for extensible sanitization rules
    """

    # Known dangerous prompt injection patterns
    DANGEROUS_PATTERNS: List[str] = [
        "ignore previous instructions",
        "ignore all previous instructions",
        "system:",
        "assistant:",
        "new instructions:",
        "<system>",
        "</system>",
    ]

    def __init__(self, logger: LoggerInterface):
        """
        WHY: Logger needed to warn about detected injection attempts
        """
        self.logger = logger

    def sanitize(self, text: str, max_length: int) -> str:
        """
        WHY: Prevent prompt injection and token overflow
        RESPONSIBILITY: Truncate and redact dangerous patterns
        PATTERNS: Guard clauses for early validation

        Args:
            text: User input text
            max_length: Maximum allowed length

        Returns:
            Sanitized text safe for LLM prompts
        """
        if not text:
            return ""

        # Guard: Truncate to max length
        text = text[:max_length]

        # Check for dangerous patterns
        text_lower = text.lower()
        for pattern in self.DANGEROUS_PATTERNS:
            if pattern not in text_lower:
                continue

            self.logger.log(
                f"⚠️ Potential prompt injection detected: {pattern}",
                "WARNING"
            )
            # Redact all case variations
            text = text.replace(pattern, "[REDACTED]")
            text = text.replace(pattern.upper(), "[REDACTED]")
            text = text.replace(pattern.capitalize(), "[REDACTED]")

        return text
