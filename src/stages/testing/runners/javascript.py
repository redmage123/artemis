#!/usr/bin/env python3
"""
WHY: JavaScript test framework runners
RESPONSIBILITY: Execute Jest tests
PATTERNS: Strategy Pattern, Template Method Pattern

This module provides runners for JavaScript testing frameworks:
- Jest: Facebook's JavaScript testing framework
"""

import json
import re
import subprocess
from pathlib import Path
from typing import List

from artemis_exceptions import wrap_exception
from stages.testing.base import BaseFrameworkRunner
from stages.testing.models import TestResult
from stages.testing.exceptions import TestOutputParsingError


class JestRunner(BaseFrameworkRunner):
    """
    WHY: Execute Jest (JavaScript/TypeScript) tests
    RESPONSIBILITY: Run and parse jest test results
    PATTERNS: Strategy Pattern

    Jest is Facebook's JavaScript testing framework:
    - Zero configuration
    - Snapshot testing
    - Coverage reports
    - Parallel execution
    """

    @property
    def framework_name(self) -> str:
        """Framework identifier"""
        return "jest"

    def _prepare_command(self, test_path: Path) -> List[str]:
        """
        WHY: Build jest command
        RESPONSIBILITY: Construct command with JSON output

        Args:
            test_path: Path to tests

        Returns:
            Command as list
        """
        return ["npx", "jest", str(test_path), "--json", "--coverage=false"]

    @wrap_exception(TestOutputParsingError, "Failed to parse jest output")
    def _parse_results(
        self,
        result: subprocess.CompletedProcess,
        duration: float
    ) -> TestResult:
        """
        WHY: Extract jest test metrics
        RESPONSIBILITY: Parse JSON or text output

        Jest provides JSON output which we parse for structured results.
        Falls back to text parsing if JSON unavailable.

        Args:
            result: Completed process
            duration: Execution time

        Returns:
            Structured test result
        """
        output = result.stdout + result.stderr

        json_match = re.search(r'\{.*"numTotalTests".*\}', output, re.DOTALL)
        if json_match:
            return self._parse_json_output(json_match.group(0), result.returncode, duration, output)

        return self._parse_text_output(output, result.returncode, duration)

    def _parse_json_output(
        self,
        json_str: str,
        exit_code: int,
        duration: float,
        output: str
    ) -> TestResult:
        """
        WHY: Parse jest JSON output
        RESPONSIBILITY: Extract metrics from JSON

        Args:
            json_str: JSON string
            exit_code: Process exit code
            duration: Execution time
            output: Raw output

        Returns:
            Structured test result
        """
        try:
            jest_data = json.loads(json_str)

            total = jest_data.get('numTotalTests', 0)
            passed = jest_data.get('numPassedTests', 0)
            failed = jest_data.get('numFailedTests', 0)
            skipped = jest_data.get('numPendingTests', 0)

            return TestResult(
                framework=self.framework_name,
                passed=passed,
                failed=failed,
                skipped=skipped,
                errors=0,
                total=total,
                exit_code=exit_code,
                duration=duration,
                output=output
            )
        except json.JSONDecodeError:
            return self._parse_text_output(output, exit_code, duration)

    def _parse_text_output(
        self,
        output: str,
        exit_code: int,
        duration: float
    ) -> TestResult:
        """
        WHY: Parse jest text output as fallback
        RESPONSIBILITY: Extract metrics from text

        Args:
            output: Raw output
            exit_code: Process exit code
            duration: Execution time

        Returns:
            Structured test result
        """
        passed = output.count("✓") or output.count("PASS")
        failed = output.count("✕") or output.count("FAIL")

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
