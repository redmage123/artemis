#!/usr/bin/env python3
"""
Build System Execution Exceptions

WHY: Separates execution-time errors from validation errors, enabling
     different recovery strategies for compilation failures, test failures,
     and timeout scenarios.

RESPONSIBILITY: Define exceptions for build execution failures including
                compilation errors, test failures, and timeout scenarios.

PATTERNS:
- Exception Hierarchy: Specialized exceptions for different execution phases
- Context Enrichment: Each exception carries phase-specific diagnostic data
- Timeout Pattern: Dedicated exception for timeout scenarios

Design Philosophy:
- Execution errors may be transient (retry) or permanent (fix code)
- Test failures are distinct from build failures (different recovery)
- Timeouts are distinct (may need resource adjustment)
- Rich context enables intelligent retry strategies
"""

from typing import Dict, Any, Optional, List
from build_managers.exceptions.base import (
    BuildSystemError,
    CONTEXT_BUILD_SYSTEM,
    CONTEXT_EXIT_CODE,
    CONTEXT_PHASE,
    CONTEXT_TIMEOUT
)


class BuildExecutionError(BuildSystemError):
    """
    Error during build execution.

    WHY: Distinguishes build/compilation failures from validation or test
         failures, enabling targeted error reporting and recovery strategies.

    RESPONSIBILITY: Signal that build process failed during execution
                   (compilation errors, missing dependencies, syntax errors).

    PATTERNS:
    - Phase Tracking: Captures which build phase failed (compile, package, install)
    - Exit Code Preservation: Stores process exit code for analysis
    - Error Aggregation: Can collect multiple error messages

    Example:
        >>> raise BuildExecutionError(
        ...     "Maven build failed with compilation errors",
        ...     context={
        ...         'build_system': 'maven',
        ...         'phase': 'compile',
        ...         'exit_code': 1,
        ...         'errors': [
        ...             'Error: Cannot find symbol MyClass',
        ...             'Error: Package com.example does not exist'
        ...         ],
        ...         'command': 'mvn clean compile',
        ...         'working_dir': '/path/to/project'
        ...     }
        ... )

    Common Context Keys:
        - build_system: Name of the build system
        - phase: Build phase that failed (compile, test, package, install)
        - exit_code: Process exit code
        - errors: List of error messages from build output
        - warnings: List of warning messages
        - command: Full command that was executed
        - working_dir: Working directory where command was run
        - stdout: Standard output capture
        - stderr: Standard error capture
    """

    def get_errors(self) -> List[str]:
        """
        Get list of error messages from build output.

        WHY: Functional accessor for error messages without exposing
             internal context structure.

        PERFORMANCE: O(1) dictionary lookup

        Returns:
            List of error messages (empty list if none)

        Example:
            >>> error.get_errors()
            ['Error: Cannot find symbol MyClass']
        """
        return self.get_context_value('errors', [])

    def get_phase(self) -> Optional[str]:
        """
        Get build phase that failed.

        WHY: Enables phase-specific error handling and recovery strategies.

        Returns:
            Build phase name or None

        Example:
            >>> error.get_phase()
            'compile'
        """
        return self.get_context_value(CONTEXT_PHASE)

    def get_exit_code(self) -> Optional[int]:
        """
        Get process exit code.

        WHY: Exit code analysis enables automated error categorization.

        Returns:
            Process exit code or None

        Example:
            >>> error.get_exit_code()
            1
        """
        return self.get_context_value(CONTEXT_EXIT_CODE)


class TestExecutionError(BuildSystemError):
    """
    Error during test execution.

    WHY: Distinguishes test failures from build failures, enabling different
         recovery strategies (rerun tests, skip tests, fix tests).

    RESPONSIBILITY: Signal that test execution failed (test failures,
                   configuration issues, missing test dependencies).

    PATTERNS:
    - Test Result Aggregation: Captures test statistics (run, passed, failed)
    - Failed Test Tracking: Lists which specific tests failed
    - Distinction: Separates test failures from test execution errors

    Example:
        >>> raise TestExecutionError(
        ...     "5 tests failed",
        ...     context={
        ...         'build_system': 'gradle',
        ...         'tests_run': 50,
        ...         'tests_passed': 45,
        ...         'tests_failed': 5,
        ...         'tests_skipped': 0,
        ...         'failed_tests': [
        ...             'UserServiceTest.testCreate',
        ...             'UserServiceTest.testUpdate',
        ...             'OrderServiceTest.testProcess'
        ...         ],
        ...         'test_output': '...',
        ...         'duration_seconds': 120
        ...     }
        ... )

    Common Context Keys:
        - build_system: Name of the build system
        - tests_run: Total number of tests executed
        - tests_passed: Number of tests that passed
        - tests_failed: Number of tests that failed
        - tests_skipped: Number of tests that were skipped
        - failed_tests: List of failed test names
        - test_output: Captured test output
        - duration_seconds: Test execution duration
    """

    def get_failed_tests(self) -> List[str]:
        """
        Get list of failed test names.

        WHY: Enables targeted test rerun or analysis of failures.

        Returns:
            List of failed test names (empty if none)

        Example:
            >>> error.get_failed_tests()
            ['UserServiceTest.testCreate', 'OrderServiceTest.testProcess']
        """
        return self.get_context_value('failed_tests', [])

    def get_test_statistics(self) -> Dict[str, int]:
        """
        Get test execution statistics.

        WHY: Functional accessor for test metrics without exposing context.

        Returns:
            Dictionary with test counts (run, passed, failed, skipped)

        Example:
            >>> error.get_test_statistics()
            {'run': 50, 'passed': 45, 'failed': 5, 'skipped': 0}
        """
        return {
            'run': self.get_context_value('tests_run', 0),
            'passed': self.get_context_value('tests_passed', 0),
            'failed': self.get_context_value('tests_failed', 0),
            'skipped': self.get_context_value('tests_skipped', 0)
        }

    def get_failure_rate(self) -> float:
        """
        Calculate test failure rate.

        WHY: Provides quick metric for test health assessment.

        PERFORMANCE: O(1) calculation from stored statistics

        Returns:
            Failure rate as decimal (0.0 to 1.0), or 0.0 if no tests run

        Example:
            >>> error.get_failure_rate()
            0.10  # 10% failure rate
        """
        stats = self.get_test_statistics()
        tests_run = stats['run']

        # Guard clause: Avoid division by zero
        if tests_run == 0:
            return 0.0

        return stats['failed'] / tests_run


class BuildTimeoutError(BuildSystemError):
    """
    Build operation timed out.

    WHY: Distinguishes timeout from other failures, enabling resource
         adjustment strategies (increase timeout, optimize build, add resources).

    RESPONSIBILITY: Signal that build, test, or other operation exceeded
                   configured timeout limit.

    PATTERNS:
    - Timeout Pattern: Dedicated exception for timeout scenarios
    - Resource Tracking: Captures timeout value and operation duration
    - Operation Context: Identifies which operation timed out

    Example:
        >>> raise BuildTimeoutError(
        ...     "Build timed out after 600 seconds",
        ...     context={
        ...         'build_system': 'cargo',
        ...         'operation': 'build',
        ...         'timeout': 600,
        ...         'elapsed': 605,
        ...         'command': 'cargo build --release',
        ...         'suggestion': 'Increase timeout or optimize build'
        ...     }
        ... )

    Common Context Keys:
        - build_system: Name of the build system
        - operation: Operation that timed out (build, test, install)
        - timeout: Configured timeout in seconds
        - elapsed: Actual time elapsed before timeout
        - command: Command that timed out
        - suggestion: Suggested remediation
    """

    def get_timeout(self) -> Optional[int]:
        """
        Get configured timeout value.

        WHY: Functional accessor for timeout without exposing context.

        Returns:
            Timeout in seconds or None

        Example:
            >>> error.get_timeout()
            600
        """
        return self.get_context_value(CONTEXT_TIMEOUT)

    def get_elapsed_time(self) -> Optional[float]:
        """
        Get elapsed time before timeout.

        WHY: Helps determine if operation was close to completion.

        Returns:
            Elapsed time in seconds or None

        Example:
            >>> error.get_elapsed_time()
            605.3
        """
        return self.get_context_value('elapsed')

    def get_suggestion(self) -> Optional[str]:
        """
        Get remediation suggestion.

        WHY: Provides actionable guidance to resolve timeout.

        Returns:
            Suggestion string or None

        Example:
            >>> error.get_suggestion()
            'Increase timeout or optimize build'
        """
        return self.get_context_value('suggestion')


# Module-level constants for execution context keys (DRY principle)
CONTEXT_ERRORS = "errors"
CONTEXT_WARNINGS = "warnings"
CONTEXT_COMMAND = "command"
CONTEXT_WORKING_DIR = "working_dir"
CONTEXT_STDOUT = "stdout"
CONTEXT_STDERR = "stderr"
CONTEXT_TESTS_RUN = "tests_run"
CONTEXT_TESTS_PASSED = "tests_passed"
CONTEXT_TESTS_FAILED = "tests_failed"
CONTEXT_TESTS_SKIPPED = "tests_skipped"
CONTEXT_FAILED_TESTS = "failed_tests"
CONTEXT_OPERATION = "operation"
CONTEXT_ELAPSED = "elapsed"
CONTEXT_SUGGESTION = "suggestion"
