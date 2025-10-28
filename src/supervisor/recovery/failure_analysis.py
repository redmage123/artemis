#!/usr/bin/env python3
"""
Module: supervisor/recovery/failure_analysis.py

WHY: Analyze failures to extract actionable information for recovery
RESPONSIBILITY: Parse errors, extract context, identify error patterns
PATTERNS: Strategy (error type mapping), Template Method (common analysis flow)

Design Philosophy:
- Extract structured information from unstructured errors
- Map error types to exception classes
- Provide context for recovery strategies
"""

import re
from typing import Dict, Any, Optional, Tuple


class FailureAnalyzer:
    """
    Analyze failures to extract recovery information.

    WHY: Structured failure analysis enables targeted recovery strategies
    RESPONSIBILITY: Parse errors, extract file/line info, categorize failures

    Design Pattern: Strategy (error type mapping)
    - Error type -> Exception class mapping (avoid if/elif chains)
    - Context extraction strategies per error category
    """

    def __init__(self):
        """Initialize failure analyzer."""
        # Strategy pattern: Map error types to exception classes
        self.exception_map = {
            "KeyError": KeyError,
            "TypeError": TypeError,
            "AttributeError": AttributeError,
            "ValueError": ValueError
        }

    def create_exception(self, error_type: str, error_message: str) -> Exception:
        """
        Create an exception instance from type and message.

        WHY: Convert error info from crash reports into exception objects
        RESPONSIBILITY: Map error type strings to exception instances
        PERFORMANCE: O(1) dictionary lookup for exception class mapping

        Args:
            error_type: Type of exception (e.g., "KeyError")
            error_message: Error message

        Returns:
            Exception instance
        """
        # Get exception class or default to Exception
        exception_class = self.exception_map.get(error_type, Exception)
        return exception_class(error_message)

    def extract_file_and_line(self, traceback_info: str) -> Optional[Tuple[str, int]]:
        """
        Extract file path and line number from traceback.

        WHY: Pinpoint error location for code fix
        RESPONSIBILITY: Parse traceback to extract file/line
        PERFORMANCE: O(n) regex search on traceback string

        Args:
            traceback_info: Traceback string

        Returns:
            Tuple of (file_path, line_number) or None if not found
        """
        # Guard clause: No traceback info
        if not traceback_info:
            return None

        # Extract file path and line number
        file_match = re.search(r'File "([^"]+)", line (\d+)', traceback_info)

        # Guard clause: Could not extract file path
        if not file_match:
            return None

        file_path = file_match.group(1)
        line_number = int(file_match.group(2))

        return (file_path, line_number)

    def read_error_context(
        self,
        file_path: str,
        line_number: int,
        context_lines: int = 10
    ) -> Optional[Dict[str, Any]]:
        """
        Read source code context around error line.

        WHY: Provide surrounding code for LLM analysis
        RESPONSIBILITY: Read file and extract context lines
        PERFORMANCE: O(n) file reading, O(1) slicing

        Args:
            file_path: Path to source file
            line_number: Line number with error
            context_lines: Number of lines before/after to include

        Returns:
            Dict with context lines and problem line, or None if failed
        """
        try:
            # Read the source file
            with open(file_path, 'r') as f:
                all_lines = f.readlines()

            # Guard clause: Line number out of range
            if line_number > len(all_lines):
                return None

            # Get context lines
            context_start = max(0, line_number - context_lines)
            context_end = min(len(all_lines), line_number + context_lines)
            context = all_lines[context_start:context_end]
            problem_line = all_lines[line_number - 1]

            return {
                "context_lines": context,
                "problem_line": problem_line,
                "context_start": context_start,
                "context_end": context_end,
                "total_lines": len(all_lines)
            }

        except Exception:
            return None

    def analyze_crash(self, crash_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze crash information.

        WHY: Extract structured information from crash report
        RESPONSIBILITY: Parse crash info into actionable recovery context
        PERFORMANCE: O(1) dictionary operations, O(n) traceback parsing

        Args:
            crash_info: Crash information dict

        Returns:
            Analyzed crash context
        """
        error_type = crash_info.get("error_type", "Unknown")
        error_message = crash_info.get("error", "Unknown error")
        traceback_info = crash_info.get("traceback", "")

        # Create exception object
        exception = self.create_exception(error_type, error_message)

        # Extract file and line
        file_line = self.extract_file_and_line(traceback_info)

        result = {
            "exception": exception,
            "error_type": error_type,
            "error_message": error_message,
            "traceback": traceback_info
        }

        # Add file/line info if available
        if file_line:
            file_path, line_number = file_line
            result["file_path"] = file_path
            result["line_number"] = line_number

            # Read context
            context = self.read_error_context(file_path, line_number)
            if context:
                result["error_context"] = context

        return result

    def categorize_error(self, error: Exception) -> str:
        """
        Categorize error for recovery strategy selection.

        WHY: Different error categories need different recovery strategies
        RESPONSIBILITY: Map errors to recovery categories
        PERFORMANCE: O(1) type checking

        Args:
            error: The exception

        Returns:
            Error category string
        """
        # Strategy pattern: Map error types to categories (avoid if/elif)
        error_categories = {
            KeyError: "missing_data",
            AttributeError: "missing_data",
            ValueError: "data_format",
            TypeError: "data_format",
            TimeoutError: "timeout",
            ConnectionError: "network"
        }

        # Get category for error type
        error_type = type(error)
        return error_categories.get(error_type, "unknown")
