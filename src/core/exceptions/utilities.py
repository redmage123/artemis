#!/usr/bin/env python3
"""
Module: core/exceptions/utilities.py

WHY: Provides utility functions and decorators for exception handling across
     Artemis. Eliminates repetitive try-catch-wrap boilerplate in every module.
     Central location for exception wrapping and handling patterns.

RESPONSIBILITY: Provide exception wrapping utilities (create_wrapped_exception,
                @wrap_exception decorator). Single Responsibility - exception utilities.

PATTERNS: Decorator Pattern, Factory Pattern, DRY Principle
          - Decorator: @wrap_exception eliminates boilerplate
          - Factory: create_wrapped_exception standardizes exception creation
          - DRY: Single source of truth for exception wrapping logic

Integration: Used throughout Artemis codebase. Every module that needs to wrap
             exceptions can use these utilities instead of duplicating logic.

Design Decision: Why separate utilities from base exceptions?
    Base exceptions are data structures (classes). Utilities are behaviors
    (functions/decorators). Separation follows Single Responsibility Principle.
"""

from typing import Optional, Dict, Any, Callable, TypeVar
from functools import wraps

from core.exceptions.base import ArtemisException


# Type variable for generic decorator typing
F = TypeVar('F', bound=Callable[..., Any])


def create_wrapped_exception(
    exception: Exception,
    artemis_exception_class: type[ArtemisException],
    message: str,
    context: Optional[Dict[str, Any]] = None
) -> ArtemisException:
    """
    Wrap a generic exception in an Artemis-specific exception (factory function).

    WHY: Standardizes exception wrapping across codebase. Ensures original
         exception is always preserved and context is consistently added.
         Without this, every module duplicates wrapping logic.

    RESPONSIBILITY: Create Artemis exception from generic exception with context.

    PATTERNS: Factory Pattern - centralized exception creation
              Exception Chaining - preserves original exception

    PERFORMANCE: O(1) - simple object creation, no iteration or computation.

    Args:
        exception: Original exception to wrap
        artemis_exception_class: Artemis exception class to wrap with
                                (e.g., RAGQueryError, LLMAPIError)
        message: Human-readable error message describing what failed
        context: Additional context dict (card_id, stage, parameters, etc.)

    Returns:
        Wrapped Artemis exception with original exception preserved

    Example:
        try:
            some_operation()
        except Exception as e:
            raise create_wrapped_exception(
                e,
                RAGQueryError,
                "Failed to query RAG database",
                {"card_id": "123", "query": "test", "collection": "code_examples"}
            )

    Design note: Preserves full exception chain for debugging. Original
                 exception accessible via .original_exception attribute.
    """
    return artemis_exception_class(
        message=message,
        context=context,
        original_exception=exception
    )


def wrap_exception(
    artemis_exception_class: type[ArtemisException],
    message: str
) -> Callable[[F], F]:
    """
    Decorator to automatically wrap exceptions in Artemis exception types.

    WHY: Eliminates repetitive try-except-wrap boilerplate in every method.
         Instead of 10 lines of exception handling, just add one @decorator.
         Reduces code duplication and ensures consistent exception handling.

    RESPONSIBILITY: Wrap decorated function in try-except with Artemis exception.

    PATTERNS: Decorator Pattern - adds behavior without modifying function
              Exception Chaining - preserves original exception
              DRY Principle - write exception handling once, apply to many functions

    What it does:
        - Wraps decorated function in try-except block
        - On exception, wraps in specified Artemis exception type
        - Preserves original exception in original_exception field
        - Adds message prefix to exception
        - Re-raises ArtemisExceptions unchanged (prevents double-wrapping)

    Args:
        artemis_exception_class: Artemis exception type to wrap with
                                (e.g., PipelineStageError, LLMAPIError)
        message: Human-readable message prefix (e.g., "Stage execution failed")

    Returns:
        Decorator function that wraps exceptions

    Example - Without decorator (11 lines):
        def execute(self, card, context):
            try:
                llm_call()
                file.read()
                return result
            except ArtemisException:
                raise  # Don't double-wrap
            except Exception as e:
                raise PipelineStageError(
                    f"Stage execution failed: {e}",
                    original_exception=e
                )

    Example - With decorator (4 lines):
        @wrap_exception(PipelineStageError, "Stage execution failed")
        def execute(self, card, context):
            llm_call()  # Any exception wrapped automatically
            file.read()  # Any exception wrapped automatically
            return result

    Design note: Doesn't wrap ArtemisExceptions to prevent double-wrapping.
                 If function raises LLMError, that exception passes through unchanged.
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except ArtemisException:
                # Guard clause: Early return - don't wrap Artemis exceptions
                # Pattern: Prevent double-wrapping (ArtemisException already wrapped)
                raise
            except Exception as e:
                # Wrap non-Artemis exceptions with context
                raise artemis_exception_class(
                    message=f"{message}: {str(e)}",
                    original_exception=e
                )
        return wrapper  # type: ignore
    return decorator
