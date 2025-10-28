#!/usr/bin/env python3
"""
WHY: Python test framework runners
RESPONSIBILITY: Execute pytest and unittest tests
PATTERNS: Strategy Pattern, Template Method Pattern

This module provides runners for Python's two main testing frameworks:
- pytest: Modern, feature-rich testing framework
- unittest: Standard library testing framework
"""

import re
from collections import Counter
from pathlib import Path
from typing import List
import subprocess

from artemis_exceptions import wrap_exception
from stages.testing.base import BaseFrameworkRunner
from stages.testing.models import TestResult
from stages.testing.exceptions import TestOutputParsingError


class PytestRunner(BaseFrameworkRunner):
    """
    WHY: Execute pytest tests
    RESPONSIBILITY: Run and parse pytest test results
    PATTERNS: Strategy Pattern

    Pytest is Python's most popular testing framework, featuring:
    - Simple assert statements
    - Powerful fixtures
    - Parametrized tests
    - Plugin ecosystem
    """

    @property
    def framework_name(self) -> str:
        """Framework identifier"""
        return "pytest"

    def _prepare_command(self, test_path: Path) -> List[str]:
        """
        WHY: Build pytest command
        RESPONSIBILITY: Construct command with optimal flags

        Args:
            test_path: Path to tests

        Returns:
            Command as list
        """
        return ["pytest", str(test_path), "-v", "--tb=short", "--color=no"]

    @wrap_exception(TestOutputParsingError, "Failed to parse pytest output")
    def _parse_results(
        self,
        result: subprocess.CompletedProcess,
        duration: float
    ) -> TestResult:
        """
        WHY: Extract pytest test metrics
        RESPONSIBILITY: Parse pytest output for test counts

        Uses single-pass regex parsing (O(n)) instead of multiple count() calls (O(4n))
        for better performance.

        Args:
            result: Completed process
            duration: Execution time

        Returns:
            Structured test result
        """
        output = result.stdout + result.stderr

        pattern = re.compile(r' (PASSED|FAILED|SKIPPED|ERROR)')
        matches = pattern.findall(output)
        counts = Counter(matches)

        passed = counts.get('PASSED', 0)
        failed = counts.get('FAILED', 0)
        skipped = counts.get('SKIPPED', 0)
        errors = counts.get('ERROR', 0)

        return TestResult(
            framework=self.framework_name,
            passed=passed,
            failed=failed,
            skipped=skipped,
            errors=errors,
            total=passed + failed + skipped + errors,
            exit_code=result.returncode,
            duration=duration,
            output=output
        )


class UnittestRunner(BaseFrameworkRunner):
    """
    WHY: Execute unittest tests
    RESPONSIBILITY: Run and parse unittest test results
    PATTERNS: Strategy Pattern

    Unittest is Python's standard library testing framework:
    - Class-based test organization
    - setUp/tearDown fixtures
    - Test discovery
    - No external dependencies
    """

    @property
    def framework_name(self) -> str:
        """Framework identifier"""
        return "unittest"

    def _prepare_command(self, test_path: Path) -> List[str]:
        """
        WHY: Build unittest discovery command
        RESPONSIBILITY: Construct command with discovery

        Args:
            test_path: Path to tests

        Returns:
            Command as list
        """
        self._ensure_init_files(test_path)
        return ["python", "-m", "unittest", "discover", "-s", str(test_path), "-v"]

    def _ensure_init_files(self, test_path: Path) -> None:
        """
        WHY: Unittest requires __init__.py for package discovery
        RESPONSIBILITY: Create missing __init__.py files

        Args:
            test_path: Test directory path
        """
        if not test_path.is_dir():
            return

        dirs_needing_init = [test_path] + [d for d in test_path.rglob("*") if d.is_dir()]

        for directory in dirs_needing_init:
            init_file = directory / "__init__.py"
            init_file.touch(exist_ok=True)

    @wrap_exception(TestOutputParsingError, "Failed to parse unittest output")
    def _parse_results(
        self,
        result: subprocess.CompletedProcess,
        duration: float
    ) -> TestResult:
        """
        WHY: Extract unittest test metrics
        RESPONSIBILITY: Parse unittest output for test counts

        Unittest output format: "Ran X tests in Y.YYYs"

        Args:
            result: Completed process
            duration: Execution time

        Returns:
            Structured test result
        """
        output = result.stdout + result.stderr

        ran_match = re.search(r'Ran (\d+) tests', output)
        total = int(ran_match.group(1)) if ran_match else 0

        failures = output.count("FAIL:")
        errors = output.count("ERROR:")

        import_errors = output.count("ImportError:") + output.count("ModuleNotFoundError:")
        if total == 0 and import_errors > 0:
            errors = import_errors
            total = import_errors

        passed = total - failures - errors

        return TestResult(
            framework=self.framework_name,
            passed=passed,
            failed=failures,
            skipped=0,
            errors=errors,
            total=total,
            exit_code=result.returncode,
            duration=duration,
            output=output
        )
