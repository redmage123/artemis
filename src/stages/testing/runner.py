#!/usr/bin/env python3
"""
WHY: Main test runner facade
RESPONSIBILITY: Provide simplified interface for test execution
PATTERNS: Facade Pattern, Dependency Injection

This module provides the main TestRunner class that serves as a facade
to the complex testing subsystem, offering a simple API for running tests
across multiple frameworks.
"""

import logging
from pathlib import Path
from typing import Optional

from artemis_exceptions import wrap_exception
from stages.testing.models import TestResult, TestFramework
from stages.testing.exceptions import TestRunnerError
from stages.testing.factory import FrameworkRunnerFactory
from stages.testing.detection import FrameworkDetector


class TestRunner:
    """
    WHY: Unified interface for multi-framework test execution
    RESPONSIBILITY: Orchestrate test execution across frameworks
    PATTERNS: Facade Pattern, Dependency Injection

    This class provides a simple interface to the complex testing subsystem,
    handling framework detection, runner creation, and test execution.

    Guard Clauses: Max 1 level nesting throughout
    """

    def __init__(
        self,
        framework: Optional[str] = None,
        verbose: bool = False,
        timeout: int = 120,
        logger: Optional[logging.Logger] = None
    ):
        """
        WHY: Initialize test runner with configuration
        RESPONSIBILITY: Set up runner with optional dependencies

        Args:
            framework: Test framework to use (auto-detected if None)
            verbose: Enable verbose output
            timeout: Test execution timeout in seconds
            logger: Optional logger for dependency injection
        """
        self.framework = framework
        self.verbose = verbose
        self.timeout = timeout
        self.logger = logger or self._create_default_logger(verbose)
        self._detector = FrameworkDetector(logger=self.logger)

    def _create_default_logger(self, verbose: bool) -> logging.Logger:
        """
        WHY: Create default logger if none provided
        RESPONSIBILITY: Set up logging with appropriate level

        Args:
            verbose: Whether to enable debug logging

        Returns:
            Configured logger instance
        """
        logger = logging.getLogger("TestRunner")
        logger.setLevel(logging.DEBUG if verbose else logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    @wrap_exception(TestRunnerError, "Test execution failed")
    def run_tests(self, test_path: str) -> TestResult:
        """
        WHY: Execute tests at specified path
        RESPONSIBILITY: Orchestrate full test execution flow

        Flow:
        1. Auto-detect framework if not specified
        2. Convert framework string to enum
        3. Create framework runner via factory
        4. Execute tests
        5. Log results
        6. Return structured result

        Args:
            test_path: Path to test directory or file

        Returns:
            TestResult with execution details

        Raises:
            TestPathNotFoundError: If test path doesn't exist
            TestFrameworkNotFoundError: If framework not installed
            TestExecutionError: If test execution fails
        """
        test_path_obj = Path(test_path)

        if not self.framework:
            self.framework = self._detector.detect_framework(test_path_obj)
            self.logger.info(f"Auto-detected framework: {self.framework}")

        framework_enum = self._get_framework_enum(self.framework)
        runner = FrameworkRunnerFactory.create_runner(framework_enum, self.logger)
        result = runner.run(test_path_obj, self.timeout)

        self._log_results(result)
        return result

    def _get_framework_enum(self, framework: str) -> TestFramework:
        """
        WHY: Convert framework string to enum
        RESPONSIBILITY: Validate and convert framework identifier

        Args:
            framework: Framework name string

        Returns:
            TestFramework enum

        Raises:
            TestRunnerError: If framework unknown
        """
        try:
            return TestFramework(framework)
        except ValueError as e:
            raise TestRunnerError(
                f"Unknown framework: {framework}",
                {
                    "framework": framework,
                    "available": [f.value for f in TestFramework]
                }
            ) from e

    def _log_results(self, result: TestResult) -> None:
        """
        WHY: Log test execution summary
        RESPONSIBILITY: Output test metrics

        Args:
            result: Test result to log
        """
        self.logger.info(
            f"Tests completed: {result.passed} passed, {result.failed} failed, "
            f"{result.skipped} skipped, {result.errors} errors "
            f"({result.pass_rate}% pass rate)"
        )
