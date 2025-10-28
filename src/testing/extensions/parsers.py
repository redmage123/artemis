#!/usr/bin/env python3
"""
WHY: Parse test output from different frameworks into standardized results
RESPONSIBILITY: Extract test metrics from framework-specific output formats
PATTERNS: Strategy pattern via dispatch tables, guard clauses for error handling
"""

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from .models import TestResult


def parse_jest_output(output: str, exit_code: int, duration: float) -> TestResult:
    """
    WHY: Parse Jest JSON output into standardized TestResult
    RESPONSIBILITY: Extract test counts from Jest's JSON or fallback to text parsing
    """
    # Try JSON parsing first
    json_match = re.search(r'\{.*"numTotalTests".*\}', output, re.DOTALL)
    if json_match:
        try:
            jest_data = json.loads(json_match.group(0))
            return TestResult(
                framework="jest",
                passed=jest_data.get('numPassedTests', 0),
                failed=jest_data.get('numFailedTests', 0),
                skipped=jest_data.get('numPendingTests', 0),
                errors=0,
                total=jest_data.get('numTotalTests', 0),
                exit_code=exit_code,
                duration=duration,
                output=output
            )
        except json.JSONDecodeError:
            pass

    # Fallback to text parsing
    passed = output.count("✓") or output.count("PASS")
    failed = output.count("✕") or output.count("FAIL")

    return TestResult(
        framework="jest",
        passed=passed,
        failed=failed,
        skipped=0,
        errors=0,
        total=passed + failed,
        exit_code=exit_code,
        duration=duration,
        output=output
    )


def parse_robot_output(
    output: str,
    exit_code: int,
    duration: float,
    output_dir: Path
) -> TestResult:
    """
    WHY: Parse Robot Framework XML or text output
    RESPONSIBILITY: Extract test statistics from output.xml or console output
    """
    # Try XML parsing first
    output_xml = output_dir / "output.xml"
    if output_xml.exists():
        try:
            tree = ET.parse(output_xml)
            root = tree.getroot()
            stats = root.find('.//statistics/total/stat')

            if stats is not None:
                passed = int(stats.get('pass', 0))
                failed = int(stats.get('fail', 0))

                return TestResult(
                    framework="robot",
                    passed=passed,
                    failed=failed,
                    skipped=0,
                    errors=0,
                    total=passed + failed,
                    exit_code=exit_code,
                    duration=duration,
                    output=output
                )
        except (ET.ParseError, ValueError):
            pass

    # Fallback to text parsing
    match = re.search(r'(\d+) critical tests, (\d+) passed, (\d+) failed', output)
    if match:
        total = int(match.group(1))
        passed = int(match.group(2))
        failed = int(match.group(3))
    else:
        total = passed = failed = 0

    return TestResult(
        framework="robot",
        passed=passed,
        failed=failed,
        skipped=0,
        errors=0,
        total=total,
        exit_code=exit_code,
        duration=duration,
        output=output
    )


def parse_pytest_output(
    output: str,
    exit_code: int,
    duration: float,
    framework: str = "pytest"
) -> TestResult:
    """
    WHY: Parse pytest output (used by Hypothesis, Playwright, Appium, Selenium)
    RESPONSIBILITY: Count test results from pytest console output
    """
    passed = output.count(" PASSED")
    failed = output.count(" FAILED")
    skipped = output.count(" SKIPPED")

    return TestResult(
        framework=framework,
        passed=passed,
        failed=failed,
        skipped=skipped,
        errors=0,
        total=passed + failed + skipped,
        exit_code=exit_code,
        duration=duration,
        output=output
    )


def parse_jmeter_output(
    output: str,
    exit_code: int,
    duration: float,
    results_dir: Path
) -> TestResult:
    """
    WHY: Parse JMeter results from .jtl file
    RESPONSIBILITY: Count test samples from JMeter results
    """
    if exit_code != 0:
        return TestResult(
            framework="jmeter",
            passed=0,
            failed=1,
            skipped=0,
            errors=0,
            total=1,
            exit_code=exit_code,
            duration=duration,
            output=output
        )

    # Read results.jtl to count samples
    results_file = results_dir / "results.jtl"
    if not results_file.exists():
        return TestResult(
            framework="jmeter",
            passed=0,
            failed=1,
            skipped=0,
            errors=0,
            total=1,
            exit_code=1,
            duration=duration,
            output=output
        )

    try:
        with open(results_file, 'r') as f:
            lines = f.readlines()
            total = len([l for l in lines if l.strip() and not l.startswith('<')])

        return TestResult(
            framework="jmeter",
            passed=total,
            failed=0,
            skipped=0,
            errors=0,
            total=total,
            exit_code=exit_code,
            duration=duration,
            output=output
        )
    except Exception:
        return TestResult(
            framework="jmeter",
            passed=0,
            failed=1,
            skipped=0,
            errors=0,
            total=1,
            exit_code=1,
            duration=duration,
            output=output
        )


def create_timeout_result(framework: str, timeout: int) -> TestResult:
    """
    WHY: Generate standardized timeout error results
    RESPONSIBILITY: Create TestResult for timeout scenarios
    """
    return TestResult(
        framework=framework,
        passed=0,
        failed=0,
        skipped=0,
        errors=1,
        total=0,
        exit_code=1,
        duration=timeout,
        output=f"Error: Tests timed out after {timeout} seconds"
    )


def create_error_result(framework: str, error: Exception) -> TestResult:
    """
    WHY: Generate standardized error results
    RESPONSIBILITY: Create TestResult for exception scenarios
    """
    return TestResult(
        framework=framework,
        passed=0,
        failed=0,
        skipped=0,
        errors=1,
        total=0,
        exit_code=1,
        duration=0.0,
        output=f"Error running {framework}: {error}"
    )
