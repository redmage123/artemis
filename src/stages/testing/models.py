#!/usr/bin/env python3
"""
WHY: Shared data models for test execution
RESPONSIBILITY: Define immutable test result structures and framework enums
PATTERNS: Data Transfer Object (DTO), Enum Pattern

This module provides immutable data structures for test results and framework
definitions, ensuring type safety and consistency across all test runners.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict


class TestFramework(Enum):
    """
    WHY: Type-safe framework identification
    RESPONSIBILITY: Define all supported test frameworks
    """
    PYTEST = "pytest"
    UNITTEST = "unittest"
    GTEST = "gtest"
    JUNIT = "junit"
    JEST = "jest"
    ROBOT = "robot"
    HYPOTHESIS = "hypothesis"
    JMETER = "jmeter"
    PLAYWRIGHT = "playwright"
    APPIUM = "appium"
    SELENIUM = "selenium"


@dataclass(frozen=True)
class TestResult:
    """
    WHY: Immutable test execution results
    RESPONSIBILITY: Encapsulate all test outcome data
    PATTERNS: Immutable DTO

    Immutability ensures result integrity and thread safety.
    Computed properties provide derived metrics without storing redundant data.
    """
    framework: str
    passed: int
    failed: int
    skipped: int
    errors: int
    total: int
    exit_code: int
    duration: float
    output: str
    metadata: Dict = field(default_factory=dict)

    @property
    def pass_rate(self) -> float:
        """
        WHY: Calculate test success percentage
        RESPONSIBILITY: Provide pass rate metric

        Returns:
            Pass rate percentage (0-100)
        """
        if self.total == 0:
            return 0.0
        return round((self.passed / self.total) * 100, 2)

    @property
    def success(self) -> bool:
        """
        WHY: Determine overall test success
        RESPONSIBILITY: Provide binary success indicator

        Success criteria:
        - No failures
        - No errors
        - At least one test ran

        Returns:
            True if all tests passed
        """
        return self.failed == 0 and self.errors == 0 and self.total > 0
