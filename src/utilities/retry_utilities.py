#!/usr/bin/env python3
"""
Module: utilities/retry_utilities.py

WHY: Provides fault-tolerant retry logic with exponential backoff for transient failures.
     Eliminates duplicate retry loops found in 6+ files, providing consistent retry behavior
     across LLM calls, file operations, and network requests.

RESPONSIBILITY:
- Execute operations with automatic retry on failure
- Apply exponential backoff between retries (2x, 4x, 8x delays)
- Cap maximum delay to prevent runaway retry times
- Log retry attempts for debugging
- Preserve original exception if all retries fail

PATTERNS:
- Strategy Pattern: Configurable retry behavior without modifying call sites
- Decorator Pattern: @retry_with_backoff for declarative retry behavior
- Template Method Pattern: execute() defines retry algorithm, subclasses can customize

Integration: Used by LLM API calls, file I/O, database connections, external service calls.
"""

import time
import functools
from typing import Callable, Optional, Dict, Any, TypeVar
from dataclasses import dataclass

from artemis_constants import (
    MAX_RETRY_ATTEMPTS,
    DEFAULT_RETRY_INTERVAL_SECONDS,
    RETRY_BACKOFF_FACTOR
)


T = TypeVar('T')


@dataclass
class RetryConfig:
    """
    Configuration for retry behavior

    WHY: Encapsulates all retry parameters in single object for easy passing/modification.

    Attributes:
        max_retries: Maximum number of retry attempts
        backoff_factor: Multiplier for exponential backoff (2 = double delay each time)
        initial_delay: Starting delay in seconds
        max_delay: Maximum delay cap to prevent excessive wait times
        verbose: Whether to print retry messages for debugging
    """
    max_retries: int = MAX_RETRY_ATTEMPTS
    backoff_factor: int = RETRY_BACKOFF_FACTOR
    initial_delay: float = DEFAULT_RETRY_INTERVAL_SECONDS - 3  # 2 seconds
    max_delay: float = 60.0
    verbose: bool = True


class RetryStrategy:
    """
    Reusable retry logic with exponential backoff and jitter

    WHY: Prevents overwhelming failing services while giving them time to recover.
         Linear retries can create thundering herd problem.

    RESPONSIBILITY:
    - Execute operations with automatic retry on failure
    - Apply exponential backoff between retries
    - Cap maximum delay to prevent runaway retry times
    - Log retry attempts for debugging

    Use cases:
    - LLM API calls (transient network errors, rate limits)
    - File I/O operations (filesystem locks, NFS delays)
    - Database connections (connection pool exhaustion)
    - External service calls (temporary outages)
    """

    def __init__(self, config: Optional[RetryConfig] = None):
        """
        Initialize retry strategy with configuration

        Args:
            config: RetryConfig with max_retries, backoff_factor, delays (optional)
                   Defaults to global constants if not provided
        """
        self.config = config or RetryConfig()

    def execute(
        self,
        operation: Callable[[], T],
        operation_name: str = "operation",
        context: Optional[Dict[str, Any]] = None
    ) -> T:
        """
        Execute operation with retry logic and exponential backoff

        WHY: Provides fault tolerance for transient failures without requiring
             every caller to implement retry logic.

        Args:
            operation: Callable to execute (must be idempotent for safety)
            operation_name: Human-readable name for logging
            context: Optional context dict for debugging (not currently used)

        Returns:
            Result from successful operation execution

        Raises:
            Last exception encountered if all retry attempts fail

        IMPORTANT: Operation must be idempotent (safe to retry) as there's no
                   way to distinguish retryable vs non-retryable failures at this level.
        """
        last_exception = None

        for attempt in range(self.config.max_retries):
            try:
                if self.config.verbose and attempt > 0:
                    print(f"[Retry] Attempt {attempt + 1}/{self.config.max_retries} for {operation_name}")

                result = operation()
                return result

            except Exception as e:
                last_exception = e

                if attempt == self.config.max_retries - 1:
                    if self.config.verbose:
                        print(f"[Retry] All {self.config.max_retries} attempts failed for {operation_name}")
                    raise

                delay = self._calculate_backoff_delay(attempt)

                if self.config.verbose:
                    print(f"[Retry] {operation_name} failed: {e}. Retrying in {delay:.1f}s...")

                time.sleep(delay)

        # Should never reach here, but defensive programming
        raise last_exception or Exception(f"{operation_name} failed after {self.config.max_retries} retries")

    def execute_with_bool_result(
        self,
        operation: Callable[[], bool],
        operation_name: str = "operation"
    ) -> bool:
        """
        Execute operation that returns bool, retry on False or Exception

        WHY: Specifically for workflow handlers that return True/False
             instead of raising exceptions.

        Args:
            operation: Callable returning bool
            operation_name: Name for logging

        Returns:
            True if operation succeeded, False if all retries failed
        """
        for attempt in range(self.config.max_retries):
            try:
                if self.config.verbose and attempt > 0:
                    print(f"[Retry] Attempt {attempt + 1}/{self.config.max_retries} for {operation_name}")

                result = operation()

                if result:
                    return True

                if attempt == self.config.max_retries - 1:
                    return False

                delay = self._calculate_backoff_delay(attempt)

                if self.config.verbose:
                    print(f"[Retry] {operation_name} returned False. Retrying in {delay:.1f}s...")

                time.sleep(delay)

            except Exception as e:
                if attempt == self.config.max_retries - 1:
                    if self.config.verbose:
                        print(f"[Retry] {operation_name} failed with exception: {e}")
                    return False

                delay = self._calculate_backoff_delay(attempt)

                if self.config.verbose:
                    print(f"[Retry] {operation_name} raised: {e}. Retrying in {delay:.1f}s...")

                time.sleep(delay)

        return False

    def _calculate_backoff_delay(self, attempt: int) -> float:
        """
        Calculate exponential backoff delay with cap

        WHY: Extracted to eliminate duplicate delay calculation logic.
             Guard clause pattern - single responsibility method.

        Args:
            attempt: Current attempt number (0-indexed)

        Returns:
            Delay in seconds, capped at max_delay
        """
        delay = self.config.initial_delay * (self.config.backoff_factor ** attempt)
        return min(delay, self.config.max_delay)


def retry_with_backoff(
    max_retries: int = MAX_RETRY_ATTEMPTS,
    backoff_factor: int = RETRY_BACKOFF_FACTOR,
    verbose: bool = True
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator for automatic retry with exponential backoff

    WHY: Provides declarative way to add retry behavior to functions
         without wrapping them in retry_operation() calls.

    Usage:
        @retry_with_backoff(max_retries=3, verbose=True)
        def my_operation():
            # code that might fail
            return result

    Args:
        max_retries: Maximum number of retry attempts
        backoff_factor: Multiplier for exponential backoff
        verbose: Whether to print retry messages
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            config = RetryConfig(
                max_retries=max_retries,
                backoff_factor=backoff_factor,
                verbose=verbose
            )
            strategy = RetryStrategy(config)

            operation = lambda: func(*args, **kwargs)
            return strategy.execute(operation, operation_name=func.__name__)

        return wrapper
    return decorator


def retry_operation(
    operation: Callable[[], T],
    operation_name: str = "operation",
    max_retries: int = MAX_RETRY_ATTEMPTS
) -> T:
    """
    Convenience function for retrying operations

    WHY: Simplifies one-off retry calls without creating RetryStrategy instance.

    Args:
        operation: Callable to retry
        operation_name: Name for logging
        max_retries: Max retry attempts

    Returns:
        Result from operation
    """
    config = RetryConfig(max_retries=max_retries)
    strategy = RetryStrategy(config)
    return strategy.execute(operation, operation_name)
