#!/usr/bin/env python3
"""
WHY: Compiled language test framework runners
RESPONSIBILITY: Execute gtest (C++) and junit (Java) tests
PATTERNS: Strategy Pattern, Template Method Pattern

This module provides runners for compiled language testing frameworks:
- Google Test (gtest): C++ testing framework
- JUnit: Java testing framework
"""

import json
import re
import subprocess
from pathlib import Path
from typing import List

from artemis_exceptions import wrap_exception
from stages.testing.base import BaseFrameworkRunner
from stages.testing.models import TestResult
from stages.testing.exceptions import TestOutputParsingError, TestExecutionError


class GtestRunner(BaseFrameworkRunner):
    """
    WHY: Execute Google Test (C++) tests
    RESPONSIBILITY: Run and parse gtest test results
    PATTERNS: Strategy Pattern

    Google Test is Google's C++ testing framework:
    - Assertions and expectations
    - Test fixtures
    - Death tests
    - JSON output support
    """

    @property
    def framework_name(self) -> str:
        """Framework identifier"""
        return "gtest"

    def _prepare_command(self, test_path: Path) -> List[str]:
        """
        WHY: Build gtest command
        RESPONSIBILITY: Locate test executable and construct command

        Args:
            test_path: Path to test executable or directory

        Returns:
            Command as list

        Raises:
            TestExecutionError: If no test executables found
        """
        test_executables = list(test_path.glob("**/*_test")) + list(test_path.glob("**/test_*"))

        if not test_executables:
            raise TestExecutionError(
                "No gtest executables found",
                {"path": str(test_path)}
            )

        test_exe = test_executables[0]
        return [str(test_exe), "--gtest_output=json:test_results.json"]

    @wrap_exception(TestOutputParsingError, "Failed to parse gtest output")
    def _parse_results(
        self,
        result: subprocess.CompletedProcess,
        duration: float
    ) -> TestResult:
        """
        WHY: Extract gtest test metrics
        RESPONSIBILITY: Parse JSON or text output

        Gtest supports JSON output which provides structured results.
        Falls back to text parsing if JSON unavailable.

        Args:
            result: Completed process
            duration: Execution time

        Returns:
            Structured test result
        """
        output = result.stdout + result.stderr

        json_file = Path("test_results.json")
        if json_file.exists():
            return self._parse_json_output(json_file, result.returncode, duration, output)

        return self._parse_text_output(output, result.returncode, duration)

    def _parse_json_output(
        self,
        json_file: Path,
        exit_code: int,
        duration: float,
        output: str
    ) -> TestResult:
        """
        WHY: Parse gtest JSON output
        RESPONSIBILITY: Extract metrics from JSON

        Args:
            json_file: Path to JSON results
            exit_code: Process exit code
            duration: Execution time
            output: Raw output

        Returns:
            Structured test result
        """
        with open(json_file, 'r') as f:
            test_data = json.load(f)

        total = test_data.get('tests', 0)
        failures = test_data.get('failures', 0)
        errors = test_data.get('errors', 0)
        passed = total - failures - errors

        return TestResult(
            framework=self.framework_name,
            passed=passed,
            failed=failures,
            skipped=0,
            errors=errors,
            total=total,
            exit_code=exit_code,
            duration=duration,
            output=output
        )

    def _parse_text_output(
        self,
        output: str,
        exit_code: int,
        duration: float
    ) -> TestResult:
        """
        WHY: Parse gtest text output as fallback
        RESPONSIBILITY: Extract metrics from text

        Args:
            output: Raw output
            exit_code: Process exit code
            duration: Execution time

        Returns:
            Structured test result
        """
        passed = output.count("[       OK ]")
        failed = output.count("[  FAILED  ]")

        return TestResult(
            framework=self.framework_name,
            passed=passed,
            failed=failed,
            skipped=0,
            errors=0,
            total=passed + failed,
            exit_code=exit_code,
            duration=duration,
            output=output
        )


class JunitRunner(BaseFrameworkRunner):
    """
    WHY: Execute JUnit (Java) tests
    RESPONSIBILITY: Run and parse junit test results via Maven/Gradle
    PATTERNS: Strategy Pattern

    JUnit is Java's standard testing framework:
    - Annotations-based tests
    - Assertions
    - Test lifecycle
    - Integration with build tools
    """

    @property
    def framework_name(self) -> str:
        """Framework identifier"""
        return "junit"

    def _prepare_command(self, test_path: Path) -> List[str]:
        """
        WHY: Build junit command via build tool
        RESPONSIBILITY: Detect Maven/Gradle and construct command

        Args:
            test_path: Path to test directory

        Returns:
            Command as list

        Raises:
            TestExecutionError: If no build file found
        """
        if (test_path / "pom.xml").exists():
            return ["mvn", "test"]

        if (test_path / "build.gradle").exists():
            return ["gradle", "test"]

        raise TestExecutionError(
            "No Maven or Gradle build file found",
            {"path": str(test_path)}
        )

    @wrap_exception(TestOutputParsingError, "Failed to parse junit output")
    def _parse_results(
        self,
        result: subprocess.CompletedProcess,
        duration: float
    ) -> TestResult:
        """
        WHY: Extract junit test metrics
        RESPONSIBILITY: Parse Maven/Gradle output

        Output format: "Tests run: X, Failures: Y, Errors: Z, Skipped: W"

        Args:
            result: Completed process
            duration: Execution time

        Returns:
            Structured test result
        """
        output = result.stdout + result.stderr

        match = re.search(r'Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+)', output)

        if match:
            total = int(match.group(1))
            failures = int(match.group(2))
            errors = int(match.group(3))
            skipped = int(match.group(4))
            passed = total - failures - errors - skipped
        else:
            total = failures = errors = skipped = passed = 0

        return TestResult(
            framework=self.framework_name,
            passed=passed,
            failed=failures,
            skipped=skipped,
            errors=errors,
            total=total,
            exit_code=result.returncode,
            duration=duration,
            output=output
        )
