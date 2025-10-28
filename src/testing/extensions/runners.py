#!/usr/bin/env python3
"""
WHY: Execute tests using different testing frameworks
RESPONSIBILITY: Run framework-specific test commands and capture results
PATTERNS: Strategy pattern for different runners, guard clauses for validation
"""

import subprocess
import time
from pathlib import Path
from typing import List, Optional, Dict, Any, Callable
from .models import TestResult, ExtensionConfig
from .parsers import (
    parse_jest_output,
    parse_robot_output,
    parse_pytest_output,
    parse_jmeter_output,
    create_timeout_result,
    create_error_result
)


class BaseTestRunner:
    """
    WHY: Provide common test execution infrastructure
    RESPONSIBILITY: Handle subprocess execution and error handling
    PATTERNS: Template method pattern, guard clauses for validation
    """

    def __init__(self, framework: str) -> None:
        """
        WHY: Initialize runner with framework name
        RESPONSIBILITY: Store framework identifier
        """
        self.framework = framework

    def run(
        self,
        test_path: Path,
        timeout: int = 120
    ) -> TestResult:
        """
        WHY: Execute test command and handle errors
        RESPONSIBILITY: Run subprocess with timeout and exception handling
        """
        if not test_path.exists():
            return create_error_result(
                self.framework,
                FileNotFoundError(f"Test path not found: {test_path}")
            )

        start_time = time.time()

        try:
            cmd = self._build_command(test_path)
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            duration = time.time() - start_time
            output = result.stdout + result.stderr

            return self._parse_output(
                output,
                result.returncode,
                duration,
                test_path
            )

        except subprocess.TimeoutExpired:
            return create_timeout_result(self.framework, timeout)
        except Exception as e:
            return create_error_result(self.framework, e)

    def _build_command(self, test_path: Path) -> List[str]:
        """
        WHY: Construct framework-specific command
        RESPONSIBILITY: Override in subclasses
        """
        raise NotImplementedError("Subclasses must implement _build_command")

    def _parse_output(
        self,
        output: str,
        exit_code: int,
        duration: float,
        test_path: Path
    ) -> TestResult:
        """
        WHY: Parse framework-specific output
        RESPONSIBILITY: Override in subclasses
        """
        raise NotImplementedError("Subclasses must implement _parse_output")


class JestRunner(BaseTestRunner):
    """
    WHY: Run Jest JavaScript/TypeScript tests
    RESPONSIBILITY: Execute Jest with JSON output and parse results
    """

    def __init__(self) -> None:
        super().__init__("jest")

    def _build_command(self, test_path: Path) -> List[str]:
        """WHY: Build Jest command with JSON output"""
        return [
            "npx", "jest",
            str(test_path),
            "--json",
            "--coverage=false"
        ]

    def _parse_output(
        self,
        output: str,
        exit_code: int,
        duration: float,
        test_path: Path
    ) -> TestResult:
        """WHY: Parse Jest JSON or text output"""
        return parse_jest_output(output, exit_code, duration)


class RobotRunner(BaseTestRunner):
    """
    WHY: Run Robot Framework acceptance tests
    RESPONSIBILITY: Execute Robot with XML output and parse statistics
    """

    def __init__(self) -> None:
        super().__init__("robot")

    def _build_command(self, test_path: Path) -> List[str]:
        """WHY: Build Robot Framework command with XML output"""
        output_dir = test_path.parent / "robot_results"
        output_dir.mkdir(exist_ok=True)
        self.output_dir = output_dir

        return [
            "robot",
            "--outputdir", str(output_dir),
            "--output", "output.xml",
            str(test_path)
        ]

    def _parse_output(
        self,
        output: str,
        exit_code: int,
        duration: float,
        test_path: Path
    ) -> TestResult:
        """WHY: Parse Robot XML or text output"""
        return parse_robot_output(output, exit_code, duration, self.output_dir)


class HypothesisRunner(BaseTestRunner):
    """
    WHY: Run Hypothesis property-based tests via pytest
    RESPONSIBILITY: Execute pytest with Hypothesis statistics
    """

    def __init__(self) -> None:
        super().__init__("hypothesis")

    def _build_command(self, test_path: Path) -> List[str]:
        """WHY: Build pytest command with Hypothesis flags"""
        return [
            "pytest",
            str(test_path),
            "-v",
            "--tb=short",
            "--hypothesis-show-statistics"
        ]

    def _parse_output(
        self,
        output: str,
        exit_code: int,
        duration: float,
        test_path: Path
    ) -> TestResult:
        """WHY: Parse pytest output for Hypothesis tests"""
        return parse_pytest_output(output, exit_code, duration, "hypothesis")


class JMeterRunner(BaseTestRunner):
    """
    WHY: Run JMeter performance/load tests
    RESPONSIBILITY: Execute JMeter test plans and parse results
    """

    def __init__(self) -> None:
        super().__init__("jmeter")

    def run(
        self,
        test_path: Path,
        timeout: int = 120
    ) -> TestResult:
        """
        WHY: Override run to find .jmx files first
        RESPONSIBILITY: Locate JMeter test plan before execution
        """
        # Find JMeter test plan files
        jmx_files = list(test_path.glob("**/*.jmx"))
        if not jmx_files:
            return create_error_result(
                self.framework,
                FileNotFoundError("No JMeter test plan files (.jmx) found")
            )

        self.jmx_file = jmx_files[0]
        return super().run(test_path, timeout)

    def _build_command(self, test_path: Path) -> List[str]:
        """WHY: Build JMeter command with results output"""
        results_dir = test_path / "jmeter_results"
        results_dir.mkdir(exist_ok=True)
        self.results_dir = results_dir

        return [
            "jmeter",
            "-n",  # Non-GUI mode
            "-t", str(self.jmx_file),
            "-l", str(results_dir / "results.jtl"),
            "-j", str(results_dir / "jmeter.log")
        ]

    def _parse_output(
        self,
        output: str,
        exit_code: int,
        duration: float,
        test_path: Path
    ) -> TestResult:
        """WHY: Parse JMeter .jtl results file"""
        return parse_jmeter_output(output, exit_code, duration, self.results_dir)


class PlaywrightRunner(BaseTestRunner):
    """
    WHY: Run Playwright browser automation tests
    RESPONSIBILITY: Execute Playwright tests via pytest
    """

    def __init__(self) -> None:
        super().__init__("playwright")

    def _build_command(self, test_path: Path) -> List[str]:
        """WHY: Build pytest command for Playwright"""
        return [
            "pytest",
            str(test_path),
            "-v",
            "--tb=short",
            "--headed"
        ]

    def _parse_output(
        self,
        output: str,
        exit_code: int,
        duration: float,
        test_path: Path
    ) -> TestResult:
        """WHY: Parse pytest output for Playwright tests"""
        return parse_pytest_output(output, exit_code, duration, "playwright")


class AppiumRunner(BaseTestRunner):
    """
    WHY: Run Appium mobile automation tests
    RESPONSIBILITY: Execute Appium tests via pytest
    """

    def __init__(self) -> None:
        super().__init__("appium")

    def _build_command(self, test_path: Path) -> List[str]:
        """WHY: Build pytest command for Appium"""
        return [
            "pytest",
            str(test_path),
            "-v",
            "--tb=short"
        ]

    def _parse_output(
        self,
        output: str,
        exit_code: int,
        duration: float,
        test_path: Path
    ) -> TestResult:
        """WHY: Parse pytest output for Appium tests"""
        return parse_pytest_output(output, exit_code, duration, "appium")


class SeleniumRunner(BaseTestRunner):
    """
    WHY: Run Selenium browser automation tests
    RESPONSIBILITY: Execute Selenium tests via pytest
    """

    def __init__(self) -> None:
        super().__init__("selenium")

    def _build_command(self, test_path: Path) -> List[str]:
        """WHY: Build pytest command for Selenium"""
        return [
            "pytest",
            str(test_path),
            "-v",
            "--tb=short"
        ]

    def _parse_output(
        self,
        output: str,
        exit_code: int,
        duration: float,
        test_path: Path
    ) -> TestResult:
        """WHY: Parse pytest output for Selenium tests"""
        return parse_pytest_output(output, exit_code, duration, "selenium")
