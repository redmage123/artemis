#!/usr/bin/env python3
"""
WHY: Specialized test framework runners
RESPONSIBILITY: Execute Robot Framework, Hypothesis, and JMeter tests
PATTERNS: Strategy Pattern, Template Method Pattern

This module provides runners for specialized testing frameworks:
- Robot Framework: Keyword-driven acceptance testing
- Hypothesis: Property-based testing
- JMeter: Load and performance testing
"""

import re
import subprocess
from pathlib import Path
from typing import List
import xml.etree.ElementTree as ET

from artemis_exceptions import wrap_exception
from stages.testing.base import BaseFrameworkRunner
from stages.testing.models import TestResult
from stages.testing.exceptions import TestOutputParsingError, TestExecutionError


class RobotRunner(BaseFrameworkRunner):
    """
    WHY: Execute Robot Framework tests
    RESPONSIBILITY: Run and parse robot framework test results
    PATTERNS: Strategy Pattern

    Robot Framework is a keyword-driven testing framework:
    - Plain-text syntax readable by non-programmers
    - Keyword-based approach
    - Extensive library ecosystem
    - HTML reports
    """

    @property
    def framework_name(self) -> str:
        """Framework identifier"""
        return "robot"

    def _prepare_command(self, test_path: Path) -> List[str]:
        """
        WHY: Build robot framework command
        RESPONSIBILITY: Construct command with XML output

        Args:
            test_path: Path to tests

        Returns:
            Command as list
        """
        output_dir = test_path.parent / "robot_results"
        output_dir.mkdir(exist_ok=True)

        return [
            "robot",
            "--outputdir", str(output_dir),
            "--output", "output.xml",
            str(test_path)
        ]

    @wrap_exception(TestOutputParsingError, "Failed to parse robot framework output")
    def _parse_results(
        self,
        result: subprocess.CompletedProcess,
        duration: float
    ) -> TestResult:
        """
        WHY: Extract robot framework test metrics
        RESPONSIBILITY: Parse XML or text output

        Args:
            result: Completed process
            duration: Execution time

        Returns:
            Structured test result
        """
        output = result.stdout + result.stderr

        output_xml = Path("robot_results/output.xml")
        if output_xml.exists():
            return self._parse_xml_output(output_xml, result.returncode, duration, output)

        return self._parse_text_output(output, result.returncode, duration)

    def _parse_xml_output(
        self,
        xml_file: Path,
        exit_code: int,
        duration: float,
        output: str
    ) -> TestResult:
        """
        WHY: Parse robot framework XML output
        RESPONSIBILITY: Extract metrics from XML

        Args:
            xml_file: Path to XML results
            exit_code: Process exit code
            duration: Execution time
            output: Raw output

        Returns:
            Structured test result
        """
        tree = ET.parse(xml_file)
        root = tree.getroot()

        stats = root.find('.//statistics/total/stat')
        if stats is not None:
            passed = int(stats.get('pass', 0))
            failed = int(stats.get('fail', 0))
            total = passed + failed

            return TestResult(
                framework=self.framework_name,
                passed=passed,
                failed=failed,
                skipped=0,
                errors=0,
                total=total,
                exit_code=exit_code,
                duration=duration,
                output=output
            )

        return self._parse_text_output(output, exit_code, duration)

    def _parse_text_output(
        self,
        output: str,
        exit_code: int,
        duration: float
    ) -> TestResult:
        """
        WHY: Parse robot framework text output as fallback
        RESPONSIBILITY: Extract metrics from text

        Args:
            output: Raw output
            exit_code: Process exit code
            duration: Execution time

        Returns:
            Structured test result
        """
        match = re.search(r'(\d+) critical tests, (\d+) passed, (\d+) failed', output)
        if match:
            total = int(match.group(1))
            passed = int(match.group(2))
            failed = int(match.group(3))
        else:
            total = passed = failed = 0

        return TestResult(
            framework=self.framework_name,
            passed=passed,
            failed=failed,
            skipped=0,
            errors=0,
            total=total,
            exit_code=exit_code,
            duration=duration,
            output=output
        )


class HypothesisRunner(BaseFrameworkRunner):
    """
    WHY: Execute Hypothesis property-based tests
    RESPONSIBILITY: Run and parse hypothesis test results
    PATTERNS: Strategy Pattern

    Hypothesis is a property-based testing framework:
    - Automatic test case generation
    - Property-based testing
    - Shrinking of failing examples
    - Integrates with pytest
    """

    @property
    def framework_name(self) -> str:
        """Framework identifier"""
        return "hypothesis"

    def _prepare_command(self, test_path: Path) -> List[str]:
        """
        WHY: Build hypothesis command
        RESPONSIBILITY: Construct pytest command with hypothesis flags

        Args:
            test_path: Path to tests

        Returns:
            Command as list
        """
        return [
            "pytest",
            str(test_path),
            "-v",
            "--tb=short",
            "--hypothesis-show-statistics"
        ]

    @wrap_exception(TestOutputParsingError, "Failed to parse hypothesis output")
    def _parse_results(
        self,
        result: subprocess.CompletedProcess,
        duration: float
    ) -> TestResult:
        """
        WHY: Extract hypothesis test metrics
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


class JmeterRunner(BaseFrameworkRunner):
    """
    WHY: Execute JMeter load/performance tests
    RESPONSIBILITY: Run and parse jmeter test results
    PATTERNS: Strategy Pattern

    JMeter is Apache's load testing tool:
    - Performance and load testing
    - Protocol support (HTTP, FTP, JDBC, etc.)
    - Distributed testing
    - Result analysis
    """

    @property
    def framework_name(self) -> str:
        """Framework identifier"""
        return "jmeter"

    def _prepare_command(self, test_path: Path) -> List[str]:
        """
        WHY: Build jmeter command
        RESPONSIBILITY: Locate .jmx file and construct command

        Args:
            test_path: Path to test directory

        Returns:
            Command as list

        Raises:
            TestExecutionError: If no .jmx files found
        """
        jmx_files = list(test_path.glob("**/*.jmx"))

        if not jmx_files:
            raise TestExecutionError(
                "No JMeter test plan files (.jmx) found",
                {"path": str(test_path)}
            )

        jmx_file = jmx_files[0]
        results_dir = test_path / "jmeter_results"
        results_dir.mkdir(exist_ok=True)

        return [
            "jmeter",
            "-n",
            "-t", str(jmx_file),
            "-l", str(results_dir / "results.jtl"),
            "-j", str(results_dir / "jmeter.log")
        ]

    @wrap_exception(TestOutputParsingError, "Failed to parse jmeter output")
    def _parse_results(
        self,
        result: subprocess.CompletedProcess,
        duration: float
    ) -> TestResult:
        """
        WHY: Extract jmeter test metrics
        RESPONSIBILITY: Parse JTL results file

        JMeter doesn't have pass/fail like unit tests.
        We count samples executed as "passed" if JMeter completed successfully.

        Args:
            result: Completed process
            duration: Execution time

        Returns:
            Structured test result
        """
        output = result.stdout + result.stderr

        if result.returncode == 0:
            results_file = Path("jmeter_results/results.jtl")
            if results_file.exists():
                with open(results_file, 'r') as f:
                    lines = f.readlines()
                    total = len([l for l in lines if l.strip() and not l.startswith('<')])

                return TestResult(
                    framework=self.framework_name,
                    passed=total,
                    failed=0,
                    skipped=0,
                    errors=0,
                    total=total,
                    exit_code=result.returncode,
                    duration=duration,
                    output=output
                )

        return TestResult(
            framework=self.framework_name,
            passed=0,
            failed=1,
            skipped=0,
            errors=0,
            total=1,
            exit_code=result.returncode,
            duration=duration,
            output=output
        )
