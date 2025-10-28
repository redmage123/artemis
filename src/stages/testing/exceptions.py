#!/usr/bin/env python3
"""
WHY: Testing-specific exception hierarchy
RESPONSIBILITY: Provide granular error types for test runner failures
PATTERNS: Exception Hierarchy, Context Preservation

This module defines a clear exception hierarchy that allows precise error
handling and reporting throughout the testing pipeline.
"""

from artemis_exceptions import PipelineStageError


class TestRunnerError(PipelineStageError):
    """
    WHY: Base exception for all test runner errors
    RESPONSIBILITY: Root of testing exception hierarchy
    """
    pass


class TestPathNotFoundError(TestRunnerError):
    """
    WHY: Test path validation failure
    RESPONSIBILITY: Signal missing test directory/file
    """
    pass


class TestFrameworkNotFoundError(TestRunnerError):
    """
    WHY: Framework installation validation failure
    RESPONSIBILITY: Signal missing test framework executable
    """
    pass


class TestExecutionError(TestRunnerError):
    """
    WHY: Test execution failure
    RESPONSIBILITY: Signal errors during test execution
    """
    pass


class TestTimeoutError(TestRunnerError):
    """
    WHY: Test execution timeout
    RESPONSIBILITY: Signal test timeout expiration
    """
    pass


class TestOutputParsingError(TestRunnerError):
    """
    WHY: Test output parsing failure
    RESPONSIBILITY: Signal errors parsing test framework output
    """
    pass
