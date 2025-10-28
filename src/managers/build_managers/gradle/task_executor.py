#!/usr/bin/env python3
"""
WHY: Execute Gradle tasks (build, test, etc.) and capture results.

RESPONSIBILITY:
- Execute Gradle build tasks via subprocess
- Run tests with optional filtering
- Parse build output for test results
- Extract errors and warnings
- Measure execution duration
- Handle timeouts and failures

PATTERNS:
- Command builder pattern
- Result object for structured output
- Guard clauses for validation
- Timeout handling
- Error extraction via regex
"""

import re
import subprocess
import time
from pathlib import Path
from typing import List, Optional, Any
import logging

from managers.build_managers.gradle.models import GradleBuildResult


class TaskExecutor:
    """
    WHY: Centralized Gradle task execution with result capture.

    RESPONSIBILITY:
    - Build command arguments
    - Execute subprocess with timeout
    - Parse test metrics from output
    - Collect errors and warnings
    - Return structured results

    PATTERNS:
    - Builder pattern for command construction
    - Result object pattern
    - Exception handling for timeouts
    - Logging integration
    """

    def __init__(
        self,
        gradle_cmd: str,
        project_dir: Path,
        logger: Optional[logging.Logger] = None
    ):
        """
        WHY: Initialize executor with Gradle command and project context.

        PATTERNS:
        - Dependency injection (gradle_cmd, logger)
        - Optional logger with fallback
        """
        self.gradle_cmd = gradle_cmd
        self.project_dir = project_dir
        self.logger = logger or logging.getLogger(__name__)

    def execute_build(
        self,
        task: str = "build",
        clean: bool = True,
        offline: bool = False,
        extra_args: Optional[List[str]] = None,
        timeout: int = 600
    ) -> GradleBuildResult:
        """
        WHY: Execute Gradle build with configurable options.

        RESPONSIBILITY:
        - Build command with optional clean
        - Add offline mode if requested
        - Execute with timeout protection
        - Parse and return structured results

        PATTERNS:
        - Guard clause for None extra_args
        - Command builder pattern
        - Exception handling for timeout
        - Result object construction
        """
        start_time = time.time()

        # Build command
        cmd = self._build_command(task, clean, offline, extra_args)

        # Execute build
        try:
            result = self._run_subprocess(cmd, timeout)
            duration = time.time() - start_time

            return self._parse_build_result(
                result=result,
                duration=duration,
                task=task
            )

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return self._create_timeout_result(task, duration, timeout)

        except Exception as e:
            duration = time.time() - start_time
            return self._create_error_result(task, duration, e)

    def execute_tests(
        self,
        test_class: Optional[str] = None,
        test_method: Optional[str] = None,
        timeout: int = 300
    ) -> GradleBuildResult:
        """
        WHY: Execute Gradle tests with optional filtering.

        RESPONSIBILITY:
        - Build test-specific arguments
        - Delegate to execute_build
        - Handle test class/method filtering

        PATTERNS:
        - Delegation to execute_build
        - Optional filtering via --tests flag
        """
        extra_args = self._build_test_args(test_class, test_method)
        return self.execute_build(
            task="test",
            clean=False,
            extra_args=extra_args,
            timeout=timeout
        )

    def get_available_tasks(self, timeout: int = 30) -> List[str]:
        """
        WHY: Query Gradle for available tasks.

        RESPONSIBILITY:
        - Execute 'gradle tasks --quiet'
        - Parse task list from output
        - Extract task names only

        PATTERNS:
        - Guard clause for empty output
        - Line-by-line parsing
        - Exception handling with empty list fallback
        """
        try:
            result = subprocess.run(
                [self.gradle_cmd, "tasks", "--quiet"],
                cwd=str(self.project_dir),
                capture_output=True,
                text=True,
                timeout=timeout
            )

            tasks = []
            for line in result.stdout.splitlines():
                task = self._extract_task_from_line(line)
                if task:
                    tasks.append(task)

            return tasks

        except Exception as e:
            self.logger.warning(f"Failed to get tasks: {e}")
            return []

    def _build_command(
        self,
        task: str,
        clean: bool,
        offline: bool,
        extra_args: Optional[List[str]]
    ) -> List[str]:
        """
        WHY: Build Gradle command with all options.

        PATTERNS:
        - Guard clause for None extra_args
        - Incremental list building
        """
        cmd = [self.gradle_cmd]

        if clean:
            cmd.append("clean")

        cmd.append(task)

        if offline:
            cmd.append("--offline")

        if extra_args:
            cmd.extend(extra_args)

        return cmd

    def _run_subprocess(
        self,
        cmd: List[str],
        timeout: int
    ) -> subprocess.CompletedProcess:
        """
        WHY: Execute subprocess with consistent settings.

        PATTERNS:
        - Single point of subprocess execution
        - Consistent capture and timeout settings
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
        duration: float,
        task: str
    ) -> GradleBuildResult:
        """
        WHY: Parse subprocess result into structured build result.

        RESPONSIBILITY:
        - Combine stdout and stderr
        - Extract test metrics
        - Collect errors and warnings
        - Determine success status

        PATTERNS:
        - Helper method delegation
        - Structured result construction
        """
        output = result.stdout + result.stderr

        # Parse test results
        tests_run = self._extract_number(output, r'(\d+) tests completed')
        tests_failed = self._extract_number(output, r'(\d+) failed')
        tests_skipped = self._extract_number(output, r'(\d+) skipped')
        tests_passed = tests_run - tests_failed - tests_skipped

        # Extract errors and warnings
        errors, warnings = self._extract_errors_and_warnings(output)

        # Determine success
        success = result.returncode == 0 and "BUILD SUCCESSFUL" in output

        return GradleBuildResult(
            success=success,
            exit_code=result.returncode,
            duration=duration,
            output=output,
            task=task,
            tests_run=tests_run,
            tests_passed=tests_passed,
            tests_failed=tests_failed,
            tests_skipped=tests_skipped,
            errors=errors[:10],  # Limit to first 10
            warnings=warnings[:10]
        )

    def _extract_errors_and_warnings(
        self,
        output: str
    ) -> tuple[List[str], List[str]]:
        """
        WHY: Extract error and warning messages from build output.

        PATTERNS:
        - Line-by-line scanning
        - Case-insensitive matching
        - Separate collection
        """
        errors = []
        warnings = []

        for line in output.splitlines():
            line_lower = line.lower()
            if "error:" in line_lower or "failed" in line_lower:
                errors.append(line.strip())
            elif "warning:" in line_lower:
                warnings.append(line.strip())

        return errors, warnings

    def _create_timeout_result(
        self,
        task: str,
        duration: float,
        timeout: int
    ) -> GradleBuildResult:
        """
        WHY: Create result object for timeout failures.

        PATTERNS:
        - Factory method pattern
        - Consistent error format
        """
        return GradleBuildResult(
            success=False,
            exit_code=1,
            duration=duration,
            output=f"Build timed out after {timeout} seconds",
            task=task,
            errors=[f"Build timeout after {timeout}s"]
        )

    def _create_error_result(
        self,
        task: str,
        duration: float,
        error: Exception
    ) -> GradleBuildResult:
        """
        WHY: Create result object for general errors.

        PATTERNS:
        - Factory method pattern
        - Exception to string conversion
        """
        return GradleBuildResult(
            success=False,
            exit_code=1,
            duration=duration,
            output=str(error),
            task=task,
            errors=[f"Build error: {str(error)}"]
        )

    def _build_test_args(
        self,
        test_class: Optional[str],
        test_method: Optional[str]
    ) -> List[str]:
        """
        WHY: Build test filtering arguments.

        PATTERNS:
        - Guard clause for None test_class
        - Optional method appending
        """
        if not test_class:
            return []

        test_spec = f"--tests={test_class}"
        if test_method:
            test_spec += f".{test_method}"

        return [test_spec]

    def _extract_task_from_line(self, line: str) -> Optional[str]:
        """
        WHY: Extract task name from 'gradle tasks' output line.

        PATTERNS:
        - Guard clauses for invalid lines
        - String splitting and stripping
        """
        # Tasks are listed as "taskName - description"
        if " - " not in line or line.startswith("-"):
            return None

        task = line.split(" - ")[0].strip()
        return task if task else None

    @staticmethod
    def _extract_number(text: str, pattern: str) -> int:
        """
        WHY: Extract numeric value from text using regex.

        PATTERNS:
        - Guard clause for no match
        - Safe integer conversion
        """
        match = re.search(pattern, text)
        return int(match.group(1)) if match else 0
