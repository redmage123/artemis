#!/usr/bin/env python3
"""
Stream Processor - Token callback processing for streaming responses

WHY: Centralize token callback logic to avoid duplication.
RESPONSIBILITY: Process token callbacks during streaming.
PATTERNS: Early return pattern, single responsibility.

Single Responsibility: Handle token callback processing
"""

from typing import Optional, Callable


class StreamProcessor:
    """
    Process token callbacks during streaming

    WHY: Avoid code duplication across OpenAI and Anthropic clients.
    RESPONSIBILITY: Execute callbacks and determine if streaming should stop.
    PATTERNS: Strategy pattern for callback execution.
    """

    @staticmethod
    def process_token_callback(
        token: str,
        callback: Optional[Callable[[str], bool]]
    ) -> bool:
        """
        Process token callback.

        WHY: Extracted to avoid nested ifs in stream processing.
        PERFORMANCE: Early return if no callback.

        Args:
            token: Token text to process
            callback: Optional callback function that receives token,
                     returns True to continue or False to stop

        Returns:
            True if generation should stop, False otherwise
        """
        # Early return if no callback (avoid nested if)
        if not callback:
            return False

        should_continue = callback(token)
        return not should_continue  # Return True to stop
