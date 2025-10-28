#!/usr/bin/env python3
"""
Module: core/exceptions/base.py

WHY: Provides the foundational ArtemisException base class that all Artemis exceptions
     inherit from. This enables unified error handling, context preservation, and
     exception chaining across the entire codebase.

RESPONSIBILITY: Single Responsibility - Define base exception with context and chaining.
                This module does ONE thing: provide the base exception infrastructure.

PATTERNS: Base Class Pattern, Exception Chaining Pattern
          - Base Class: All Artemis exceptions inherit from ArtemisException
          - Chaining: Preserves original_exception to never lose root cause

Design Decision: Why a dedicated base module?
    1. Single source of truth for base exception behavior
    2. Easy to extend base functionality (all exceptions get updates)
    3. Clear separation from specific exception types
    4. Facilitates catch-all error handling (catch ArtemisException)
"""

from typing import Optional, Dict, Any


class ArtemisException(Exception):
    """
    Base exception for all Artemis errors with context preservation.

    WHY: Provides foundation for entire exception hierarchy. Every Artemis
         exception inherits from this to enable:
         1. Catch-all error handling (catch ArtemisException vs Exception)
         2. Context preservation (metadata attached to every exception)
         3. Exception chaining (original_exception never lost)
         4. Consistent error formatting across system

    RESPONSIBILITY: Store error message, context metadata, and original exception.
                    Format human-readable error strings with full debugging info.

    PATTERNS: Base Exception with Context, Exception Chaining
              - Context Pattern: Attach metadata (card_id, stage, file paths)
              - Chaining Pattern: Preserve original exception for debugging

    Use cases:
        - Catch all Artemis errors: except ArtemisException
        - Add context: raise LLMError("API failed", context={"card_id": "001"})
        - Wrap exceptions: raise FileReadError("Read failed", original_exception=e)
        - Debug: exception.context shows metadata, original_exception shows root cause

    Context examples:
        - {"card_id": "TASK-001", "stage": "architecture"}
        - {"file_path": "/path/to/file.py", "operation": "read"}
        - {"llm_model": "gpt-4", "prompt_length": 5000}
        - {"developer": "developer-a", "test_status": "failed"}
    """

    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        """
        Initialize Artemis exception with message, context, and original exception.

        WHY: Captures all information needed for debugging - the WHAT (message),
             the WHERE/WHEN (context), and the WHY (original exception).

        PERFORMANCE: O(1) initialization, context dict stored by reference.

        Args:
            message: Human-readable error message describing what went wrong
            context: Dictionary with debugging metadata (card_id, stage, file paths)
                    Automatically included in error string and logging
            original_exception: Original exception if this is wrapping another exception
                               Preserves root cause for debugging stack traces

        Example:
            raise LLMAPIError(
                "Failed to call OpenAI API",
                context={"model": "gpt-4", "timeout": 30, "attempt": 3},
                original_exception=original_api_exception
            )
        """
        super().__init__(message)
        self.message = message
        self.context = context or {}
        self.original_exception = original_exception

    def __str__(self) -> str:
        """
        Format exception as human-readable string with full context.

        WHY: Default Exception.__str__ only shows message. This adds context
             and original exception for complete debugging picture. Essential
             for log analysis and debugging production issues.

        PERFORMANCE: O(n) where n = number of context items. Single string
                     concatenation operation using join() for efficiency.

        What it does:
            - Starts with error message
            - Appends context dict as "key=value" pairs if present
            - Appends original exception type and message if present
            - Creates single-line string suitable for logging

        Returns:
            Formatted string: "Message (Context: k1=v1, k2=v2) | Caused by: Type: msg"

        Example output:
            "Failed to read file (Context: file_path=/tmp/test.py, operation=read) |
             Caused by: FileNotFoundError: [Errno 2] No such file or directory"
        """
        msg = self.message

        # Guard clause: Add context only if present (early return pattern)
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            msg = f"{msg} (Context: {context_str})"

        # Guard clause: Add original exception only if present
        if self.original_exception:
            exception_type = type(self.original_exception).__name__
            msg = f"{msg} | Caused by: {exception_type}: {self.original_exception}"

        return msg
