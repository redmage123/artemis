#!/usr/bin/env python3
"""
WHY: Web automation test framework runners
RESPONSIBILITY: Execute Playwright, Selenium, and Appium tests
PATTERNS: Strategy Pattern, Template Method Pattern

This module provides runners for web and mobile automation frameworks:
- Playwright: Modern browser automation
- Selenium: Classic browser automation
- Appium: Mobile app automation
"""

import subprocess
from pathlib import Path
from typing import List

from artemis_exceptions import wrap_exception
from stages.testing.base import BaseFrameworkRunner
from stages.testing.models import TestResult
from stages.testing.exceptions import TestOutputParsingError


class PlaywrightRunner(BaseFrameworkRunner):
    """
    WHY: Execute Playwright browser automation tests
    RESPONSIBILITY: Run and parse playwright test results
    PATTERNS: Strategy Pattern

    Playwright is Microsoft's modern browser automation framework:
    - Cross-browser support (Chromium, Firefox, WebKit)
    - Auto-wait capabilities
    - Network interception
    - Mobile emulation
    """

    @property
    def framework_name(self) -> str:
        """Framework identifier"""
        return "playwright"

    def _prepare_command(self, test_path: Path) -> List[str]:
        """
        WHY: Build playwright command
        RESPONSIBILITY: Construct pytest command for playwright tests

        Playwright typically runs via pytest plugin.

        Args:
            test_path: Path to tests

        Returns:
            Command as list
        """
        return ["pytest", str(test_path), "-v", "--tb=short", "--headed"]

    @wrap_exception(TestOutputParsingError, "Failed to parse playwright output")
    def _parse_results(
        self,
        result: subprocess.CompletedProcess,
        duration: float
    ) -> TestResult:
        """
        WHY: Extract playwright test metrics
        RESPONSIBILITY: Parse pytest output

        Args:
            result: Completed process
            duration: Execution time

        Returns:
            Structured test result
        """
        output = result.stdout + result.stderr

        passed = output.count(" PASSED")
        failed = output.count(" FAILED")
        skipped = output.count(" SKIPPED")

        return TestResult(
            framework=self.framework_name,
            passed=passed,
            failed=failed,
            skipped=skipped,
            errors=0,
            total=passed + failed + skipped,
            exit_code=result.returncode,
            duration=duration,
            output=output
        )


class SeleniumRunner(BaseFrameworkRunner):
    """
    WHY: Execute Selenium browser automation tests
    RESPONSIBILITY: Run and parse selenium test results
    PATTERNS: Strategy Pattern

    Selenium is the classic browser automation framework:
    - WebDriver protocol
    - Cross-browser support
    - Mature ecosystem
    - Language bindings for many languages
    """

    @property
    def framework_name(self) -> str:
        """Framework identifier"""
        return "selenium"

    def _prepare_command(self, test_path: Path) -> List[str]:
        """
        WHY: Build selenium command
        RESPONSIBILITY: Construct pytest command for selenium tests

        Args:
            test_path: Path to tests

        Returns:
            Command as list
        """
        return ["pytest", str(test_path), "-v", "--tb=short"]

    @wrap_exception(TestOutputParsingError, "Failed to parse selenium output")
    def _parse_results(
        self,
        result: subprocess.CompletedProcess,
        duration: float
    ) -> TestResult:
        """
        WHY: Extract selenium test metrics
        RESPONSIBILITY: Parse pytest output

        Args:
            result: Completed process
            duration: Execution time

        Returns:
            Structured test result
        """
        output = result.stdout + result.stderr

        passed = output.count(" PASSED")
        failed = output.count(" FAILED")
        skipped = output.count(" SKIPPED")

        return TestResult(
            framework=self.framework_name,
            passed=passed,
            failed=failed,
            skipped=skipped,
            errors=0,
            total=passed + failed + skipped,
            exit_code=result.returncode,
            duration=duration,
            output=output
        )


class AppiumRunner(BaseFrameworkRunner):
    """
    WHY: Execute Appium mobile automation tests
    RESPONSIBILITY: Run and parse appium test results
    PATTERNS: Strategy Pattern

    Appium is the standard for mobile app automation:
    - iOS and Android support
    - Native, hybrid, and mobile web apps
    - WebDriver protocol
    - Cross-platform tests
    """

    @property
    def framework_name(self) -> str:
        """Framework identifier"""
        return "appium"

    def _prepare_command(self, test_path: Path) -> List[str]:
        """
        WHY: Build appium command
        RESPONSIBILITY: Construct pytest command for appium tests

        Args:
            test_path: Path to tests

        Returns:
            Command as list
        """
        return ["pytest", str(test_path), "-v", "--tb=short"]

    @wrap_exception(TestOutputParsingError, "Failed to parse appium output")
    def _parse_results(
        self,
        result: subprocess.CompletedProcess,
        duration: float
    ) -> TestResult:
        """
        WHY: Extract appium test metrics
        RESPONSIBILITY: Parse pytest output

        Args:
            result: Completed process
            duration: Execution time

        Returns:
            Structured test result
        """
        output = result.stdout + result.stderr

        passed = output.count(" PASSED")
        failed = output.count(" FAILED")
        skipped = output.count(" SKIPPED")

        return TestResult(
            framework=self.framework_name,
            passed=passed,
            failed=failed,
            skipped=skipped,
            errors=0,
            total=passed + failed + skipped,
            exit_code=result.returncode,
            duration=duration,
            output=output
        )
