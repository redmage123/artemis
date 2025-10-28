#!/usr/bin/env python3
"""
Module: supervisor/recovery/strategies.py

WHY: Concrete recovery strategies for different error types
RESPONSIBILITY: Implement specific recovery approaches (JSON fix, retry, defaults, skip)
PATTERNS: Strategy (polymorphic recovery), Chain of Responsibility (fallback sequence)

Recovery Strategies:
1. JSONParsingStrategy: Fix malformed JSON responses from LLM
2. RetryStrategy: Exponential backoff retry for transient errors
3. DefaultValueStrategy: Substitute defaults for missing keys
4. SkipStageStrategy: Skip non-critical stages

Design Philosophy:
- Each strategy is independent and focused on one error type
- Strategies compose into a fallback chain
- New strategies can be added without modifying existing ones
"""

import re
import json
from typing import Dict, Any, Optional

from supervisor.recovery.strategy import RecoveryStrategy


class JSONParsingStrategy(RecoveryStrategy):
    """
    Fix JSON parsing errors by extracting JSON from markdown.

    WHY: LLM responses often wrap JSON in markdown code blocks
    RESPONSIBILITY: Extract and parse JSON from markdown-wrapped responses
    PERFORMANCE: O(n) regex search on response text
    """

    def __init__(self):
        super().__init__("json_parsing_fix")

    def can_handle(self, error: Exception, context: Dict[str, Any]) -> bool:
        """
        Check if error is JSON-related.

        Args:
            error: The exception
            context: Execution context

        Returns:
            True if this is a JSON parsing error
        """
        # Guard clause: No error
        if not error:
            return False

        # Guard clause: Wrong error type
        if not isinstance(error, (ValueError, TypeError)):
            return False

        # Check if error message mentions JSON or parsing
        error_msg = str(error).lower()
        return "json" in error_msg or "parse" in error_msg

    def recover(self, error: Exception, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract JSON from markdown and parse it.

        Args:
            error: The exception
            context: Execution context

        Returns:
            Recovery result with parsed JSON, or None if failed
        """
        # Guard clause: No raw response available
        raw_response = context.get("raw_response", "")
        if not raw_response:
            return None

        try:
            # Try to extract JSON from markdown code block
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', raw_response, re.DOTALL)

            # Guard clause: No JSON found in markdown block
            if not json_match:
                return None

            cleaned_json = json_match.group(1)
            parsed = json.loads(cleaned_json)

            return {
                "success": True,
                "strategy": self.name,
                "parsed_data": parsed,
                "message": "Successfully extracted and parsed JSON from markdown code block"
            }

        except Exception as e:
            return None


class RetryStrategy(RecoveryStrategy):
    """
    Retry with exponential backoff for transient errors.

    WHY: Transient errors often resolve with retry and backoff
    RESPONSIBILITY: Schedule retries with increasing delays
    PERFORMANCE: Exponential backoff (2^n seconds) prevents API overload
    """

    def __init__(self, max_retries: int = 3):
        super().__init__("retry_with_backoff")
        self.max_retries = max_retries

    def can_handle(self, error: Exception, context: Dict[str, Any]) -> bool:
        """
        Check if retry limit not exceeded.

        Args:
            error: The exception
            context: Execution context

        Returns:
            True if can still retry
        """
        retry_count = context.get("retry_count", 0)
        return retry_count < self.max_retries

    def recover(self, error: Exception, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Schedule retry with exponential backoff.

        Args:
            error: The exception
            context: Execution context

        Returns:
            Recovery result with backoff delay
        """
        retry_count = context.get("retry_count", 0)

        # Guard clause: Max retries exceeded
        if retry_count >= self.max_retries:
            return None

        # Calculate exponential backoff
        backoff_seconds = 2 ** retry_count

        return {
            "success": True,
            "strategy": self.name,
            "retry_count": retry_count + 1,
            "backoff_seconds": backoff_seconds,
            "message": f"Retrying with {backoff_seconds}s backoff (attempt {retry_count + 1})"
        }


class DefaultValueStrategy(RecoveryStrategy):
    """
    Substitute default values for missing keys.

    WHY: Missing keys can be filled with sensible defaults to continue execution
    RESPONSIBILITY: Provide default values for common missing keys
    PERFORMANCE: O(1) dictionary lookup for default values
    """

    def __init__(self):
        super().__init__("default_values")
        # Strategy pattern: Dictionary mapping of keys to default values
        self.defaults = {
            "approach": "standard",
            "architecture": "modular",
            "strategy": "default",
            "method": "default",
            "priority": "medium",
            "developer": "unknown",
            "status": "pending",
            "result": "unknown",
            "score": 0,
            "count": 0,
            "enabled": False
        }

    def can_handle(self, error: Exception, context: Dict[str, Any]) -> bool:
        """
        Check if error is missing key error.

        Args:
            error: The exception
            context: Execution context

        Returns:
            True if this is a KeyError or AttributeError
        """
        return isinstance(error, (KeyError, AttributeError))

    def recover(self, error: Exception, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Provide default value for missing key.

        Args:
            error: The exception
            context: Execution context

        Returns:
            Recovery result with default value
        """
        # Extract missing key from error
        missing_key = str(error).strip("'\"")

        # Get default for this key
        default_value = self.defaults.get(missing_key)

        # Guard clause: No default available for this key
        if default_value is None:
            return None

        # Apply default value to context
        context[missing_key] = default_value

        return {
            "success": True,
            "strategy": self.name,
            "missing_key": missing_key,
            "default_value": default_value,
            "message": f"Used default value for missing key '{missing_key}'"
        }


class SkipStageStrategy(RecoveryStrategy):
    """
    Skip non-critical stages to continue pipeline execution.

    WHY: Non-critical stages can be skipped to keep pipeline progressing
    RESPONSIBILITY: Identify and skip non-critical stages
    PERFORMANCE: O(1) set membership check
    """

    def __init__(self):
        super().__init__("skip_stage")
        # Define non-critical stages (use set for O(1) lookup)
        self.non_critical_stages = {"ui_ux", "code_review", "documentation"}

    def can_handle(self, error: Exception, context: Dict[str, Any]) -> bool:
        """
        Check if stage is non-critical.

        Args:
            error: The exception
            context: Execution context

        Returns:
            True if stage can be skipped
        """
        stage_name = context.get("stage_name", "")
        return stage_name.lower() in self.non_critical_stages

    def recover(self, error: Exception, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Mark stage as skipped.

        Args:
            error: The exception
            context: Execution context

        Returns:
            Recovery result with skip confirmation
        """
        stage_name = context.get("stage_name", "")

        # Guard clause: Stage is critical, cannot skip
        if stage_name.lower() not in self.non_critical_stages:
            return None

        return {
            "success": True,
            "strategy": self.name,
            "stage_name": stage_name,
            "message": f"Skipped non-critical stage '{stage_name}'"
        }
