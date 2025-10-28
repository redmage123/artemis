#!/usr/bin/env python3
"""
WHY: Define data models for test execution results and extension configuration
RESPONSIBILITY: Provide type-safe test result representation with computed properties
PATTERNS: Dataclass pattern, Property pattern for computed values
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class TestResult:
    """
    WHY: Standardize test execution results across all test frameworks
    RESPONSIBILITY: Store test metrics and provide computed statistics
    PATTERNS: Dataclass for immutable data, properties for computed values
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

    @property
    def pass_rate(self) -> float:
        """
        WHY: Calculate success percentage for test run
        RESPONSIBILITY: Compute pass rate safely handling zero total
        """
        if self.total == 0:
            return 0.0
        return round((self.passed / self.total) * 100, 2)

    @property
    def success(self) -> bool:
        """
        WHY: Provide quick success/failure determination
        RESPONSIBILITY: Check if test run had no failures or errors
        """
        return self.failed == 0 and self.errors == 0


@dataclass
class ExtensionConfig:
    """
    WHY: Configure test runner extensions with runtime parameters
    RESPONSIBILITY: Store configuration for test execution
    PATTERNS: Dataclass for configuration management
    """
    timeout: int = 120
    verbose: bool = True
    coverage: bool = False
    headless: bool = True

    def __post_init__(self) -> None:
        """
        WHY: Validate configuration values on initialization
        RESPONSIBILITY: Ensure timeout is positive
        """
        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")
