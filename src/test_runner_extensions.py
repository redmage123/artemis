#!/usr/bin/env python3
"""
WHY: Maintain backward compatibility with existing test_runner_extensions usage
RESPONSIBILITY: Re-export testing/extensions package API
PATTERNS: Facade pattern, re-export pattern for migration support

MIGRATION NOTE: This module is a backward compatibility wrapper.
New code should import from testing.extensions directly:
    from testing.extensions import run_jest, TestResult

Original module refactored into testing/extensions/ package with:
- models.py: TestResult and ExtensionConfig
- parsers.py: Output parsing strategies
- runners.py: Framework-specific test runners
- extensions_core.py: Registry and orchestration
- __init__.py: Package exports
"""

from pathlib import Path
from testing.extensions import (
    TestResult,
    ExtensionConfig,
    run_jest,
    run_robot,
    run_hypothesis,
    run_jmeter,
    run_playwright,
    run_appium,
    run_selenium,
    run_test_extension,
    get_supported_frameworks,
    register_custom_runner,
    BaseTestRunner,
    JestRunner,
    RobotRunner,
    HypothesisRunner,
    JMeterRunner,
    PlaywrightRunner,
    AppiumRunner,
    SeleniumRunner,
)

__all__ = [
    # Models
    "TestResult",
    "ExtensionConfig",
    # Framework runners (backward compatibility)
    "run_jest",
    "run_robot",
    "run_hypothesis",
    "run_jmeter",
    "run_playwright",
    "run_appium",
    "run_selenium",
    # Core API
    "run_test_extension",
    "get_supported_frameworks",
    "register_custom_runner",
    # Runner classes
    "BaseTestRunner",
    "JestRunner",
    "RobotRunner",
    "HypothesisRunner",
    "JMeterRunner",
    "PlaywrightRunner",
    "AppiumRunner",
    "SeleniumRunner",
]
