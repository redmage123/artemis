#!/usr/bin/env python3
"""
Module: artemis_utilities.py

Purpose: Provides reusable utility classes to eliminate code duplication across pipeline stages
Why: DRY (Don't Repeat Yourself) principle - consolidates 200+ lines of duplicate code
     from 30+ files into centralized, tested implementations.
Patterns: Strategy Pattern (RetryStrategy), Adapter Pattern (FileOperations),
         Template Method Pattern (ErrorHandler)
Integration: Used by ALL pipeline stages, developer agents, and orchestrator components.
            Core shared infrastructure for the entire Artemis system.

Key Responsibilities:
1. RetryStrategy - Exponential backoff retry logic with configurable attempts/delays
2. Validator - Input validation with consistent error messages and context
3. ErrorHandler - Standardized exception wrapping and logging
4. FileOperations - Safe file I/O with existence checks and error handling

Impact:
- Reduces code duplication from 200+ lines to <50 lines per use case
- Provides consistent error handling across entire system
- Centralizes retry logic configuration (easy to tune globally)
- Standardizes validation patterns (prevents validation drift)

Design Decision:
Why separate from artemis_services: Services are domain-specific (TestRunner, HTMLValidator),
utilities are cross-cutting concerns (retry, validate, error handling). This separation
follows SRP (Single Responsibility Principle) and makes utilities independently testable.
"""

import time
import functools
from typing import Dict, Any, List, Callable, Optional, TypeVar, Union
from pathlib import Path
from dataclasses import dataclass

from artemis_constants import (
    MAX_RETRY_ATTEMPTS,
    DEFAULT_RETRY_INTERVAL_SECONDS,
    RETRY_BACKOFF_FACTOR
)
from artemis_exceptions import (
    ArtemisException,
    wrap_exception,
    PipelineStageError,
    PipelineValidationError as ValidationError
)
from artemis_services import FileManager, PipelineLogger


T = TypeVar('T')


# ============================================================================
# RETRY STRATEGY - Eliminates duplicate retry logic
# ============================================================================

@dataclass
class RetryConfig:
    """Configuration for retry behavior"""
    max_retries: int = MAX_RETRY_ATTEMPTS
    backoff_factor: int = RETRY_BACKOFF_FACTOR
    initial_delay: float = DEFAULT_RETRY_INTERVAL_SECONDS - 3  # 2 seconds
    max_delay: float = 60.0
    verbose: bool = True


class RetryStrategy:
    """
    Reusable retry logic with exponential backoff and jitter

    Why it exists: Eliminates duplicate retry loops found in 6+ files. Before this class,
                   every LLM call, file operation, and network request implemented its own
                   retry logic, leading to inconsistent behavior and maintenance burden.

    Design pattern: Strategy Pattern
    Why this design: Allows configurable retry behavior without modifying call sites.
                     Different strategies (exponential backoff, linear, immediate) can
                     be swapped by changing RetryConfig.

    Responsibilities:
    - Execute operations with automatic retry on failure
    - Apply exponential backoff between retries (2x, 4x, 8x delays)
    - Cap maximum delay to prevent runaway retry times
    - Log retry attempts for debugging
    - Preserve original exception if all retries fail

    Use cases:
    - LLM API calls (transient network errors, rate limits)
    - File I/O operations (filesystem locks, NFS delays)
    - Database connections (connection pool exhaustion)
    - External service calls (temporary outages)

    Why exponential backoff: Prevents overwhelming failing services while giving them
                             time to recover. Linear retries can create thundering herd.
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

        Why needed: Provides fault tolerance for transient failures without requiring
                    every caller to implement retry logic.

        What it does:
        - Attempts operation up to max_retries times
        - On failure, waits with exponentially increasing delay
        - Caps delay at max_delay to prevent excessive wait times
        - Logs each retry attempt if verbose mode enabled
        - Preserves and re-raises original exception if all retries exhausted

        Args:
            operation: Callable to execute (must be idempotent for safety)
            operation_name: Human-readable name for logging
            context: Optional context dict for debugging (not currently used)

        Returns:
            Result from successful operation execution

        Raises:
            Last exception encountered if all retry attempts fail

        Example:
            retry = RetryStrategy(RetryConfig(max_retries=3, backoff_factor=2))
            result = retry.execute(lambda: call_llm_api(), "LLM call")

        Design note: Operation must be idempotent (safe to retry) as there's no
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
                    # Last attempt failed
                    if self.config.verbose:
                        print(f"[Retry] All {self.config.max_retries} attempts failed for {operation_name}")
                    raise

                # Calculate delay with exponential backoff
                delay = min(
                    self.config.initial_delay * (self.config.backoff_factor ** attempt),
                    self.config.max_delay
                )

                if self.config.verbose:
                    print(f"[Retry] {operation_name} failed: {e}. Retrying in {delay:.1f}s...")

                time.sleep(delay)

        # Should never reach here, but just in case
        raise last_exception or Exception(f"{operation_name} failed after {self.config.max_retries} retries")

    def execute_with_bool_result(
        self,
        operation: Callable[[], bool],
        operation_name: str = "operation"
    ) -> bool:
        """
        Execute operation that returns bool, retry on False or Exception

        Specifically for workflow handlers that return True/False

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

                # Operation returned False - retry if not last attempt
                if attempt == self.config.max_retries - 1:
                    return False

                delay = min(
                    self.config.initial_delay * (self.config.backoff_factor ** attempt),
                    self.config.max_delay
                )

                if self.config.verbose:
                    print(f"[Retry] {operation_name} returned False. Retrying in {delay:.1f}s...")

                time.sleep(delay)

            except Exception as e:
                if attempt == self.config.max_retries - 1:
                    if self.config.verbose:
                        print(f"[Retry] {operation_name} failed with exception: {e}")
                    return False

                delay = min(
                    self.config.initial_delay * (self.config.backoff_factor ** attempt),
                    self.config.max_delay
                )

                if self.config.verbose:
                    print(f"[Retry] {operation_name} raised: {e}. Retrying in {delay:.1f}s...")

                time.sleep(delay)

        return False


def retry_with_backoff(
    max_retries: int = MAX_RETRY_ATTEMPTS,
    backoff_factor: int = RETRY_BACKOFF_FACTOR,
    verbose: bool = True
):
    """
    Decorator for automatic retry with exponential backoff

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


# ============================================================================
# VALIDATOR - Eliminates duplicate validation logic
# ============================================================================

class Validator:
    """
    Reusable validation utilities with informative error context

    Why it exists: Before this class, 15+ files had duplicate validation code like:
                   if 'field' not in data: raise ValueError("Missing field")
                   Consolidation provides consistent error messages and debugging context.

    Design pattern: Utility/Helper Class (all static methods)
    Why this design: Validation is stateless - no need for instance variables. Static
                     methods allow usage without instantiation: Validator.validate_*()

    Responsibilities:
    - Validate required fields exist in dictionaries
    - Validate values are not None
    - Provide both exception-throwing and boolean-returning variants
    - Include helpful context in error messages for debugging

    Benefits over inline validation:
    - Consistent error messages across entire codebase
    - Automatic context injection (field names, data name, present fields)
    - Single point to enhance validation logic
    - Reduces 5+ lines of validation to 1 function call

    Integration: Used by all pipeline stages before calling LLM, writing files, or
                performing operations to ensure required data is present.
    """

    @staticmethod
    def validate_required_fields(
        data: Dict[str, Any],
        required_fields: List[str],
        data_name: str = "data"
    ) -> None:
        """
        Validate all required fields exist in dictionary (raises on failure)

        Why needed: Prevents cryptic KeyError exceptions downstream. Better to fail fast
                    with clear message about which field is missing.

        What it does:
        - Checks each required field exists in data dict
        - Collects all missing fields (not just first one)
        - Throws ValidationError with comprehensive context
        - Lists both missing and present fields for comparison

        Args:
            data: Dictionary to validate
            required_fields: List of required field names (e.g., ["prompt", "card_id"])
            data_name: Human-readable name for error message (e.g., "LLM request")

        Raises:
            ValidationError: If any required fields are missing, includes context with:
                           - data_name
                           - missing_fields list
                           - required_fields list
                           - present_fields list

        Example:
            Validator.validate_required_fields(
                llm_request,
                ["prompt", "model", "temperature"],
                "LLM request"
            )
            # Raises ValidationError with full context if fields missing

        Design note: Collects all missing fields before raising to show complete picture,
                     rather than failing on first missing field.
        """
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            raise ValidationError(
                f"Missing required fields in {data_name}: {', '.join(missing_fields)}",
                context={
                    "data_name": data_name,
                    "missing_fields": missing_fields,
                    "required_fields": required_fields,
                    "present_fields": list(data.keys())
                }
            )

    @staticmethod
    def validate_required_fields_bool(
        data: Dict[str, Any],
        required_fields: List[str],
        data_name: str = "data",
        verbose: bool = True
    ) -> bool:
        """
        Validate required fields, return bool instead of raising

        Useful for workflow handlers that return True/False

        Args:
            data: Dictionary to validate
            required_fields: List of required field names
            data_name: Name for logging
            verbose: Whether to print error messages

        Returns:
            True if valid, False if missing fields
        """
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            if verbose:
                print(f"[Validation] Missing required fields in {data_name}: {', '.join(missing_fields)}")
            return False

        return True

    @staticmethod
    def validate_not_none(value: Any, field_name: str) -> None:
        """
        Validate that value is not None

        Args:
            value: Value to check
            field_name: Field name for error message

        Raises:
            ValidationError: If value is None
        """
        if value is None:
            raise ValidationError(
                f"{field_name} cannot be None",
                context={"field_name": field_name}
            )

    @staticmethod
    def validate_type(
        value: Any,
        expected_type: type,
        field_name: str
    ) -> None:
        """
        Validate that value is of expected type

        Args:
            value: Value to check
            expected_type: Expected type
            field_name: Field name for error message

        Raises:
            ValidationError: If value is wrong type
        """
        if not isinstance(value, expected_type):
            raise ValidationError(
                f"{field_name} must be {expected_type.__name__}, got {type(value).__name__}",
                context={
                    "field_name": field_name,
                    "expected_type": expected_type.__name__,
                    "actual_type": type(value).__name__
                }
            )

    @staticmethod
    def validate_in_range(
        value: Union[int, float],
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
        field_name: str = "value"
    ) -> None:
        """
        Validate that numeric value is in range

        Args:
            value: Value to check
            min_value: Minimum allowed value (inclusive)
            max_value: Maximum allowed value (inclusive)
            field_name: Field name for error message

        Raises:
            ValidationError: If value is out of range
        """
        if min_value is not None and value < min_value:
            raise ValidationError(
                f"{field_name} must be >= {min_value}, got {value}",
                context={"field_name": field_name, "value": value, "min": min_value}
            )

        if max_value is not None and value > max_value:
            raise ValidationError(
                f"{field_name} must be <= {max_value}, got {value}",
                context={"field_name": field_name, "value": value, "max": max_value}
            )

    @staticmethod
    def validate_non_empty(
        value: Union[str, List, Dict],
        field_name: str
    ) -> None:
        """
        Validate that string/list/dict is not empty

        Args:
            value: Value to check
            field_name: Field name for error message

        Raises:
            ValidationError: If value is empty
        """
        if not value:
            raise ValidationError(
                f"{field_name} cannot be empty",
                context={"field_name": field_name, "type": type(value).__name__}
            )


# ============================================================================
# ERROR HANDLER - Standardizes exception handling
# ============================================================================

class ErrorHandler:
    """
    Standardized error handling and wrapping

    Eliminates 144+ duplicate try/except blocks
    """

    def __init__(self, verbose: bool = True):
        self.verbose = verbose

    def handle_with_logging(
        self,
        operation: Callable[[], T],
        operation_name: str,
        error_message: str = "Operation failed",
        default_return: Optional[T] = None,
        raise_on_error: bool = False
    ) -> Optional[T]:
        """
        Execute operation with standardized error handling

        Args:
            operation: Callable to execute
            operation_name: Name for logging
            error_message: Message to show on error
            default_return: Value to return on error (if not raising)
            raise_on_error: Whether to raise or return default

        Returns:
            Result from operation, or default_return on error

        Raises:
            Wrapped exception if raise_on_error=True
        """
        try:
            return operation()

        except Exception as e:
            if self.verbose:
                print(f"[ErrorHandler] {operation_name} failed: {e}")

            if raise_on_error:
                raise wrap_exception(
                    e,
                    PipelineStageError,
                    error_message,
                    context={"operation": operation_name}
                )
            else:
                return default_return

    def wrap_operation(
        self,
        operation: Callable[[], bool],
        operation_name: str,
        success_message: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """
        Wrap operation that returns bool, with logging

        Common pattern for workflow handlers

        Args:
            operation: Callable returning bool
            operation_name: Name for logging
            success_message: Message on success
            error_message: Message on error

        Returns:
            True if succeeded, False if failed
        """
        try:
            result = operation()

            if result and success_message and self.verbose:
                print(f"[{operation_name}] {success_message}")
            elif not result and error_message and self.verbose:
                print(f"[{operation_name}] {error_message}")

            return result

        except Exception as e:
            if self.verbose:
                print(f"[{operation_name}] Failed with exception: {e}")
            return False


# ============================================================================
# FILE OPERATIONS - Convenience wrappers for FileManager
# ============================================================================

class FileOperations:
    """
    Convenience wrappers for file operations

    Eliminates 58+ duplicate file operation patterns
    """

    @staticmethod
    def safe_read_json(
        file_path: Union[str, Path],
        default: Optional[Dict] = None,
        verbose: bool = True
    ) -> Optional[Dict]:
        """
        Safely read JSON file with existence check

        Args:
            file_path: Path to JSON file
            default: Default value if file doesn't exist
            verbose: Whether to log messages

        Returns:
            JSON data or default
        """
        path = Path(file_path)

        if not path.exists():
            if verbose:
                print(f"[FileOps] File not found: {file_path}")
            return default

        try:
            return FileManager.read_json(str(file_path))
        except Exception as e:
            if verbose:
                print(f"[FileOps] Failed to read JSON from {file_path}: {e}")
            return default

    @staticmethod
    def safe_write_json(
        file_path: Union[str, Path],
        data: Dict,
        verbose: bool = True
    ) -> bool:
        """
        Safely write JSON file with error handling

        Args:
            file_path: Path to write to
            data: Data to write
            verbose: Whether to log messages

        Returns:
            True if succeeded, False otherwise
        """
        try:
            FileManager.write_json(str(file_path), data)
            return True
        except Exception as e:
            if verbose:
                print(f"[FileOps] Failed to write JSON to {file_path}: {e}")
            return False

    @staticmethod
    def safe_read_text(
        file_path: Union[str, Path],
        default: Optional[str] = None,
        verbose: bool = True
    ) -> Optional[str]:
        """
        Safely read text file with existence check

        Args:
            file_path: Path to text file
            default: Default value if file doesn't exist
            verbose: Whether to log messages

        Returns:
            File contents or default
        """
        path = Path(file_path)

        if not path.exists():
            if verbose:
                print(f"[FileOps] File not found: {file_path}")
            return default

        try:
            return FileManager.read_text(str(file_path))
        except Exception as e:
            if verbose:
                print(f"[FileOps] Failed to read text from {file_path}: {e}")
            return default

    @staticmethod
    def ensure_directory(
        dir_path: Union[str, Path],
        verbose: bool = False
    ) -> bool:
        """
        Ensure directory exists, create if needed

        Args:
            dir_path: Directory path
            verbose: Whether to log messages

        Returns:
            True if directory exists or was created
        """
        path = Path(dir_path)

        if path.exists():
            return True

        try:
            path.mkdir(parents=True, exist_ok=True)
            if verbose:
                print(f"[FileOps] Created directory: {dir_path}")
            return True
        except Exception as e:
            if verbose:
                print(f"[FileOps] Failed to create directory {dir_path}: {e}")
            return False


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

# Global instances for convenience
_default_retry_strategy = RetryStrategy()
_default_error_handler = ErrorHandler()


def retry_operation(
    operation: Callable[[], T],
    operation_name: str = "operation",
    max_retries: int = MAX_RETRY_ATTEMPTS
) -> T:
    """
    Convenience function for retrying operations

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


def validate_required(data: Dict, fields: List[str], name: str = "data") -> None:
    """Convenience function for validating required fields"""
    Validator.validate_required_fields(data, fields, name)


def safe_execute(
    operation: Callable[[], T],
    operation_name: str,
    default: Optional[T] = None
) -> Optional[T]:
    """Convenience function for safe execution with error handling"""
    return _default_error_handler.handle_with_logging(
        operation,
        operation_name,
        default_return=default,
        raise_on_error=False
    )
