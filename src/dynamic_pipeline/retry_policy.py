#!/usr/bin/env python3
"""
Module: retry_policy.py

WHY: Transient failures (network issues, rate limits) should retry. Permanent failures
     (syntax errors) should not. This policy encapsulates retry logic and backoff.

RESPONSIBILITY: Configure and determine retry behavior for stage execution failures.

PATTERNS:
    - Configuration Object: Encapsulates retry settings
    - Exponential Backoff: Prevents thundering herd and gives issues time to resolve
    - Guard Clauses: Early returns for retry decision logic
"""

from dataclasses import dataclass, field
from typing import Set


@dataclass
class RetryPolicy:
    """
    Configuration for stage retry behavior.

    Why it exists: Transient failures (network, rate limits) should retry,
    permanent failures (syntax errors) should not. Encapsulates retry logic.

    Design pattern: Configuration Object

    Retry strategy:
    - Retries only specified exception types
    - Exponential backoff between attempts
    - Maximum retry limit
    - Per-stage override capability
    """
    max_retries: int = 3
    retryable_exceptions: Set[type] = field(default_factory=lambda: {
        # Examples of retryable exception types
        # In real system, import actual exception classes
        Exception  # Placeholder - replace with actual retryable types
    })
    backoff_multiplier: float = 2.0
    initial_delay: float = 1.0

    def should_retry(self, exception: Exception, attempt: int) -> bool:
        """
        Determine if exception should trigger retry.

        Why needed: Centralizes retry decision logic. Checks both exception
        type and attempt count.

        Args:
            exception: Exception that occurred
            attempt: Current attempt number (0-indexed)

        Returns:
            True if should retry, False if should fail
        """
        # Guard clause: Exceeded max retries
        if attempt >= self.max_retries:
            return False

        # Check if exception type is retryable
        return any(isinstance(exception, exc_type) for exc_type in self.retryable_exceptions)

    def get_delay(self, attempt: int) -> float:
        """
        Calculate delay before next retry (exponential backoff).

        Why needed: Exponential backoff prevents thundering herd and
        gives transient issues time to resolve.

        Args:
            attempt: Attempt number (0-indexed)

        Returns:
            Delay in seconds before next retry
        """
        return self.initial_delay * (self.backoff_multiplier ** attempt)
