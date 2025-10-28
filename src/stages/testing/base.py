#!/usr/bin/env python3
"""
WHY: Abstract base for framework-specific test runners
RESPONSIBILITY: Define template method for test execution
PATTERNS: Template Method Pattern, Strategy Pattern, Protocol

This module provides the abstract base class that all framework runners
implement, ensuring consistent test execution flow while allowing
framework-specific customization.
"""

import os
import subprocess
import time
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Protocol

from artemis_exceptions import wrap_exception
from stages.testing.models import TestResult
from stages.testing.exceptions import (
    TestPathNotFoundError,
    TestFrameworkNotFoundError,
    TestExecutionError,
    TestTimeoutError
)


class FrameworkRunner(Protocol):
    """
    WHY: Define framework runner interface
    RESPONSIBILITY: Type-safe protocol for framework runners
    PATTERNS: Protocol Pattern (structural typing)
    """

    def run(self, test_path: Path, timeout: int) -> TestResult:
        """Run tests and return results"""
        ...


class BaseFrameworkRunner(ABC):
    """
    WHY: Template method for test execution
    RESPONSIBILITY: Define standard test execution flow
    PATTERNS: Template Method Pattern

    This abstract base class implements the Template Method pattern,
    defining the skeleton of test execution while allowing subclasses
    to override specific steps.

    Execution flow:
    1. Validate test path exists
    2. Prepare framework-specific command
    3. Execute command with timeout and environment setup
    4. Parse framework-specific output
    5. Return structured result

    Guard Clauses: Max 1 level nesting throughout
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        WHY: Dependency injection for logging
        RESPONSIBILITY: Initialize runner with optional logger

        Args:
            logger: Optional logger instance (creates default if None)
        """
        self.logger = logger or logging.getLogger(self.__class__.__name__)

    @wrap_exception(TestExecutionError, "Test execution failed")
    def run(self, test_path: Path, timeout: int) -> TestResult:
        """
        WHY: Execute tests with consistent flow
        RESPONSIBILITY: Template method orchestrating test execution
        PATTERNS: Template Method Pattern

        Args:
            test_path: Path to test directory or file
            timeout: Maximum execution time in seconds

        Returns:
            TestResult with execution details

        Raises:
            TestPathNotFoundError: If test path doesn't exist
            TestFrameworkNotFoundError: If framework not installed
            TestExecutionError: If test execution fails
            TestTimeoutError: If tests exceed timeout
        """
        self._validate_test_path(test_path)

        start_time = time.time()

        try:
            cmd = self._prepare_command(test_path)
            raw_result = self._execute_command(cmd, test_path, timeout)
            duration = time.time() - start_time

            return self._parse_results(raw_result, duration)

        except subprocess.TimeoutExpired as e:
            duration = time.time() - start_time
            raise TestTimeoutError(
                f"Tests timed out after {timeout} seconds",
                {"framework": self.framework_name, "timeout": timeout}
            ) from e
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"Test execution failed: {e}", exc_info=True)
            raise TestExecutionError(
                f"Failed to execute {self.framework_name} tests",
                {"framework": self.framework_name, "error": str(e)}
            ) from e

    def _validate_test_path(self, test_path: Path) -> None:
        """
        WHY: Early validation prevents cryptic errors
        RESPONSIBILITY: Ensure test path exists

        Args:
            test_path: Path to validate

        Raises:
            TestPathNotFoundError: If path doesn't exist
        """
        if not test_path.exists():
            raise TestPathNotFoundError(
                f"Test path not found: {test_path}",
                {"path": str(test_path)}
            )

    @abstractmethod
    def _prepare_command(self, test_path: Path) -> List[str]:
        """
        WHY: Framework-specific command construction
        RESPONSIBILITY: Build command line for test execution

        Args:
            test_path: Path to test directory or file

        Returns:
            Command as list of strings
        """
        pass

    def _execute_command(
        self,
        cmd: List[str],
        test_path: Path,
        timeout: int
    ) -> subprocess.CompletedProcess:
        """
        WHY: Execute test command with proper environment
        RESPONSIBILITY: Run command with timeout and PYTHONPATH setup

        Args:
            cmd: Command to execute
            test_path: Path to test directory or file
            timeout: Maximum execution time

        Returns:
            CompletedProcess with stdout/stderr

        Raises:
            TestFrameworkNotFoundError: If framework executable not found
            TestExecutionError: If execution fails
        """
        try:
            self.logger.info(f"Executing: {' '.join(cmd)}")

            env = os.environ.copy()
            cwd = str(test_path.parent) if test_path.is_file() else str(test_path)
            env = self._setup_pythonpath(test_path, env)

            return subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd,
                env=env
            )
        except FileNotFoundError as e:
            raise TestFrameworkNotFoundError(
                f"{self.framework_name} not found in PATH",
                {"framework": self.framework_name, "command": cmd[0]}
            ) from e
        except Exception as e:
            raise TestExecutionError(
                f"Failed to execute test command: {str(e)}",
                {"framework": self.framework_name, "command": cmd}
            ) from e

    def _setup_pythonpath(self, test_path: Path, env: dict) -> dict:
        """
        WHY: Enable tests to import from developer's src directory
        RESPONSIBILITY: Add src directory to PYTHONPATH

        This handles the common pattern where tests are in developer-X/tests/
        and need to import from developer-X/src/

        Args:
            test_path: Path to test directory or file
            env: Environment dictionary to modify

        Returns:
            Modified environment dictionary
        """
        try:
            return self._add_src_to_pythonpath(test_path, env)
        except Exception as e:
            self.logger.warning(f"Failed to setup PYTHONPATH: {e}")
            return env

    def _add_src_to_pythonpath(self, test_path: Path, env: dict) -> dict:
        """
        WHY: Add src directory to PYTHONPATH if it exists
        RESPONSIBILITY: Locate and add src directory

        Args:
            test_path: Path to test directory or file
            env: Environment dictionary

        Returns:
            Modified environment dictionary
        """
        test_dir = test_path.parent if test_path.is_file() else test_path
        developer_root = test_dir.parent
        src_dir = developer_root / "src"

        if not (src_dir.exists() and src_dir.is_dir()):
            return env

        existing_path = env.get('PYTHONPATH', '')
        env['PYTHONPATH'] = f"{src_dir}:{existing_path}" if existing_path else str(src_dir)
        self.logger.info(f"Added to PYTHONPATH: {src_dir}")

        return env

    @abstractmethod
    def _parse_results(
        self,
        result: subprocess.CompletedProcess,
        duration: float
    ) -> TestResult:
        """
        WHY: Framework-specific result parsing
        RESPONSIBILITY: Extract test metrics from output

        Args:
            result: Completed subprocess result
            duration: Test execution time

        Returns:
            Structured TestResult
        """
        pass

    @property
    @abstractmethod
    def framework_name(self) -> str:
        """
        WHY: Framework identification
        RESPONSIBILITY: Return framework name

        Returns:
            Framework name string
        """
        pass
