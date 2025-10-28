#!/usr/bin/env python3
"""
WHY: Centralized testing orchestration package
RESPONSIBILITY: Universal test framework execution and result reporting
PATTERNS: Facade Pattern, Strategy Pattern, Factory Pattern

This package provides a modular, extensible testing framework that supports
multiple test frameworks (pytest, unittest, gtest, junit, jest, etc.) with
a unified interface.

Architecture:
- models: Test result data structures
- exceptions: Testing-specific exception hierarchy
- base: Abstract framework runner interface (Template Method Pattern)
- runners: Framework-specific runners (Strategy Pattern)
  - python: pytest, unittest
  - compiled: gtest, junit
  - javascript: jest
  - web: playwright, selenium, appium
  - specialized: robot, hypothesis, jmeter
- detection: Framework auto-detection
- factory: Framework runner factory (Factory Pattern)
- runner: Main test runner facade (Facade Pattern)
- cli: Command-line interface helpers
"""

from stages.testing.models import TestResult, TestFramework
from stages.testing.exceptions import (
    TestRunnerError,
    TestPathNotFoundError,
    TestFrameworkNotFoundError,
    TestExecutionError,
    TestTimeoutError,
    TestOutputParsingError
)
from stages.testing.runner import TestRunner
from stages.testing.factory import FrameworkRunnerFactory
from stages.testing.detection import FrameworkDetector

__all__ = [
    # Main interface
    'TestRunner',

    # Models
    'TestResult',
    'TestFramework',

    # Factory and detection
    'FrameworkRunnerFactory',
    'FrameworkDetector',

    # Exceptions
    'TestRunnerError',
    'TestPathNotFoundError',
    'TestFrameworkNotFoundError',
    'TestExecutionError',
    'TestTimeoutError',
    'TestOutputParsingError',
]
