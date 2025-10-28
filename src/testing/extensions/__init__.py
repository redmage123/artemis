#!/usr/bin/env python3
"""
WHY: Provide unified interface for test runner extensions
RESPONSIBILITY: Export public API for test framework execution
PATTERNS: Facade pattern for simplified package interface
"""

from .models import TestResult, ExtensionConfig
from .extensions_core import (
    run_test_extension,
    get_supported_frameworks,
    register_custom_runner
)
from .runners import (
    BaseTestRunner,
    JestRunner,
    RobotRunner,
    HypothesisRunner,
    JMeterRunner,
    PlaywrightRunner,
    AppiumRunner,
    SeleniumRunner
)

# Backward compatibility - expose original function names
from pathlib import Path


def run_jest(test_path: Path, timeout: int = 120) -> TestResult:
    """Run Jest tests - backward compatibility wrapper"""
    return run_test_extension("jest", test_path, timeout)


def run_robot(test_path: Path, timeout: int = 120) -> TestResult:
    """Run Robot Framework tests - backward compatibility wrapper"""
    return run_test_extension("robot", test_path, timeout)


def run_hypothesis(test_path: Path, timeout: int = 120) -> TestResult:
    """Run Hypothesis tests - backward compatibility wrapper"""
    return run_test_extension("hypothesis", test_path, timeout)


def run_jmeter(test_path: Path, timeout: int = 120) -> TestResult:
    """Run JMeter tests - backward compatibility wrapper"""
    return run_test_extension("jmeter", test_path, timeout)


def run_playwright(test_path: Path, timeout: int = 120) -> TestResult:
    """Run Playwright tests - backward compatibility wrapper"""
    return run_test_extension("playwright", test_path, timeout)


def run_appium(test_path: Path, timeout: int = 120) -> TestResult:
    """Run Appium tests - backward compatibility wrapper"""
    return run_test_extension("appium", test_path, timeout)


def run_selenium(test_path: Path, timeout: int = 120) -> TestResult:
    """Run Selenium tests - backward compatibility wrapper"""
    return run_test_extension("selenium", test_path, timeout)


__all__ = [
    # Models
    "TestResult",
    "ExtensionConfig",
    # Core functions
    "run_test_extension",
    "get_supported_frameworks",
    "register_custom_runner",
    # Runners
    "BaseTestRunner",
    "JestRunner",
    "RobotRunner",
    "HypothesisRunner",
    "JMeterRunner",
    "PlaywrightRunner",
    "AppiumRunner",
    "SeleniumRunner",
    # Backward compatibility
    "run_jest",
    "run_robot",
    "run_hypothesis",
    "run_jmeter",
    "run_playwright",
    "run_appium",
    "run_selenium",
]
