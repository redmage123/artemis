#!/usr/bin/env python3
"""
Module: Maven Build Executor

WHY: Centralized execution of Maven build lifecycle phases and test operations.
RESPONSIBILITY: Execute Maven commands, parse output, extract test results and errors.
PATTERNS: Command pattern, Strategy pattern (different build configurations).

Dependencies: maven_enums, maven_models, subprocess
"""

import subprocess
import re
import time
from pathlib import Path
from typing import List, Optional
import logging

from .maven_enums import MavenPhase
from .maven_models import MavenBuildResult


class BuildExecutor:
    """
    Maven build lifecycle executor.

    WHY: Executes Maven builds with various configurations and parses results.
    RESPONSIBILITY:
    - Execute Maven lifecycle phases (compile, test, package, install)
    - Parse build output for test results, errors, warnings
    - Handle timeouts and failures gracefully

    PATTERNS:
    - Command pattern: Build execution as configurable command
    - Template Method: Common build flow with variation points
    - Strategy pattern: Different build strategies (skip tests, offline, profiles)

    Build Output Parsing:
    - Test results: "Tests run: X, Failures: Y, Errors: Z, Skipped: A"
    - Errors: Lines starting with [ERROR]
    - Warnings: Lines starting with [WARNING]
    - Success indicator: "BUILD SUCCESS" in output
    """

    def __init__(
        self,
        project_dir: Path,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize build executor.

        Args:
            project_dir: Maven project root directory
            logger: Optional logger for output
        """
        self.project_dir = project_dir
        self.logger = logger or logging.getLogger(__name__)

    def build(
        self,
        phase: MavenPhase = MavenPhase.PACKAGE,
        skip_tests: bool = False,
        clean: bool = True,
        offline: bool = False,
        profiles: Optional[List[str]] = None,
        extra_args: Optional[List[str]] = None,
        timeout: int = 600
    ) -> MavenBuildResult:
        """
        Execute Maven build.

        WHY: Central build execution with flexible configuration.
        RESPONSIBILITY: Build command, execute, parse results.

        Args:
            phase: Maven lifecycle phase to execute
            skip_tests: Skip test execution (-DskipTests)
            clean: Run clean before build
            offline: Work offline (use local repository only)
            profiles: Maven profiles to activate (-P flag)
            extra_args: Additional Maven arguments
            timeout: Build timeout in seconds

        Returns:
            MavenBuildResult with build outcome and metrics
        """
        start_time = time.time()

        # Build command using composition
        cmd = self._build_command(phase, skip_tests, clean, offline, profiles, extra_args)

        # Execute and parse results
        try:
            result = self._execute_maven_command(cmd, timeout)
            duration = time.time() - start_time
            output = result.stdout + result.stderr

            return self._parse_build_result(result, output, duration, phase)

        except subprocess.TimeoutExpired:
            return self._create_timeout_result(timeout, time.time() - start_time, phase)
        except Exception as e:
            return self._create_error_result(str(e), time.time() - start_time, phase)

    def run_tests(
        self,
        test_class: Optional[str] = None,
        test_method: Optional[str] = None,
        timeout: int = 300
    ) -> MavenBuildResult:
        """
        Run Maven tests.

        WHY: Specialized test execution with optional filtering.
        RESPONSIBILITY: Execute test phase with optional test selection.

        Args:
            test_class: Specific test class to run (e.g., com.example.MyTest)
            test_method: Specific test method to run (e.g., testSomething)
            timeout: Test timeout in seconds

        Returns:
            MavenBuildResult with test results

        Maven Test Selection:
        - No args: Run all tests
        - -Dtest=MyTest: Run specific test class
        - -Dtest=MyTest#testMethod: Run specific test method
        """
        extra_args = self._build_test_args(test_class, test_method)

        return self.build(
            phase=MavenPhase.TEST,
            skip_tests=False,
            clean=False,
            extra_args=extra_args,
            timeout=timeout
        )

    def _build_command(
        self,
        phase: MavenPhase,
        skip_tests: bool,
        clean: bool,
        offline: bool,
        profiles: Optional[List[str]],
        extra_args: Optional[List[str]]
    ) -> List[str]:
        """
        Build Maven command with all options.

        WHY: Guard clause - construct command before execution.
        RESPONSIBILITY: Assemble command list with all flags and arguments.

        Returns:
            Complete Maven command as list
        """
        cmd = ["mvn"]

        if clean:
            cmd.append("clean")

        cmd.append(phase.value)

        if skip_tests:
            cmd.extend(["-DskipTests", "-Dmaven.test.skip=true"])

        if offline:
            cmd.append("--offline")

        if profiles:
            cmd.append(f"-P{','.join(profiles)}")

        if extra_args:
            cmd.extend(extra_args)

        return cmd

    def _build_test_args(
        self,
        test_class: Optional[str],
        test_method: Optional[str]
    ) -> List[str]:
        """
        Build test selection arguments.

        WHY: Guard clause - construct test args separately.
        RESPONSIBILITY: Build -Dtest argument for test filtering.

        Returns:
            List of test arguments (empty if no filtering)
        """
        if not test_class:
            return []

        test_arg = f"-Dtest={test_class}"
        if test_method:
            test_arg += f"#{test_method}"

        return [test_arg]

    def _execute_maven_command(
        self,
        cmd: List[str],
        timeout: int
    ) -> subprocess.CompletedProcess:
        """
        Execute Maven command.

        WHY: Isolated subprocess execution for testability.
        RESPONSIBILITY: Run Maven command and capture output.

        Args:
            cmd: Maven command as list
            timeout: Timeout in seconds

        Returns:
            CompletedProcess with stdout/stderr
        """
        return subprocess.run(
            cmd,
            cwd=str(self.project_dir),
            capture_output=True,
            text=True,
            timeout=timeout
        )

    def _parse_build_result(
        self,
        result: subprocess.CompletedProcess,
        output: str,
        duration: float,
        phase: MavenPhase
    ) -> MavenBuildResult:
        """
        Parse build execution result.

        WHY: Centralized result parsing logic.
        RESPONSIBILITY: Extract all metrics from Maven output.

        Args:
            result: Subprocess result
            output: Combined stdout/stderr
            duration: Build duration in seconds
            phase: Maven phase that was executed

        Returns:
            MavenBuildResult with parsed metrics
        """
        # Parse test results
        tests_run = self._extract_number(output, r'Tests run: (\d+)')
        tests_failed = self._extract_number(output, r'Failures: (\d+)')
        tests_skipped = self._extract_number(output, r'Skipped: (\d+)')
        tests_passed = tests_run - tests_failed - tests_skipped

        # Extract errors and warnings (limit to avoid huge result objects)
        errors = re.findall(r'\[ERROR\] (.+)', output)
        warnings = re.findall(r'\[WARNING\] (.+)', output)

        # Success requires exit code 0 AND "BUILD SUCCESS" in output
        success = result.returncode == 0 and "BUILD SUCCESS" in output

        return MavenBuildResult(
            success=success,
            exit_code=result.returncode,
            duration=duration,
            output=output,
            phase=phase.value,
            tests_run=tests_run,
            tests_passed=tests_passed,
            tests_failed=tests_failed,
            tests_skipped=tests_skipped,
            errors=errors[:10],  # Limit to first 10 errors
            warnings=warnings[:10]
        )

    def _extract_number(self, text: str, pattern: str) -> int:
        """
        Extract number from text using regex pattern.

        WHY: Reusable pattern for extracting numeric metrics.
        RESPONSIBILITY: Safe regex extraction with default to 0.

        Args:
            text: Text to search
            pattern: Regex pattern with one capture group

        Returns:
            Extracted number or 0 if not found
        """
        match = re.search(pattern, text)
        return int(match.group(1)) if match else 0

    def _create_timeout_result(
        self,
        timeout: int,
        duration: float,
        phase: MavenPhase
    ) -> MavenBuildResult:
        """
        Create result for timeout scenario.

        WHY: Guard clause - handle timeout as special case.
        RESPONSIBILITY: Return failure result with timeout error.

        Returns:
            MavenBuildResult indicating timeout
        """
        return MavenBuildResult(
            success=False,
            exit_code=1,
            duration=duration,
            output=f"Build timed out after {timeout} seconds",
            phase=phase.value,
            errors=[f"Build timeout after {timeout}s"]
        )

    def _create_error_result(
        self,
        error_msg: str,
        duration: float,
        phase: MavenPhase
    ) -> MavenBuildResult:
        """
        Create result for exception scenario.

        WHY: Guard clause - handle exceptions as special case.
        RESPONSIBILITY: Return failure result with error message.

        Returns:
            MavenBuildResult indicating error
        """
        return MavenBuildResult(
            success=False,
            exit_code=1,
            duration=duration,
            output=error_msg,
            phase=phase.value,
            errors=[f"Build error: {error_msg}"]
        )
