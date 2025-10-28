#!/usr/bin/env python3
"""
WHY: Orchestrate test execution across multiple testing frameworks
RESPONSIBILITY: Provide unified interface for running different test frameworks
PATTERNS: Strategy pattern via dispatch table, factory pattern for runners
"""

from pathlib import Path
from typing import Dict, Callable, Optional
from .models import TestResult
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


class TestExtensionRegistry:
    """
    WHY: Manage available test framework runners
    RESPONSIBILITY: Register and retrieve framework-specific runners
    PATTERNS: Registry pattern, dispatch table for framework selection
    """

    def __init__(self) -> None:
        """
        WHY: Initialize registry with supported frameworks
        RESPONSIBILITY: Create dispatch table of framework runners
        """
        self._runners: Dict[str, BaseTestRunner] = {
            "jest": JestRunner(),
            "robot": RobotRunner(),
            "hypothesis": HypothesisRunner(),
            "jmeter": JMeterRunner(),
            "playwright": PlaywrightRunner(),
            "appium": AppiumRunner(),
            "selenium": SeleniumRunner()
        }

    def get_runner(self, framework: str) -> Optional[BaseTestRunner]:
        """
        WHY: Retrieve runner for specified framework
        RESPONSIBILITY: Return runner or None if not supported
        """
        return self._runners.get(framework.lower())

    def is_supported(self, framework: str) -> bool:
        """
        WHY: Check if framework is supported
        RESPONSIBILITY: Validate framework availability
        """
        return framework.lower() in self._runners

    def list_frameworks(self) -> list[str]:
        """
        WHY: Get list of supported frameworks
        RESPONSIBILITY: Return available framework names
        """
        return list(self._runners.keys())

    def register_runner(self, framework: str, runner: BaseTestRunner) -> None:
        """
        WHY: Add custom runner to registry
        RESPONSIBILITY: Enable extension with custom frameworks
        """
        self._runners[framework.lower()] = runner


# Global registry instance
_registry = TestExtensionRegistry()


def run_test_extension(
    framework: str,
    test_path: Path,
    timeout: int = 120
) -> TestResult:
    """
    WHY: Execute tests using specified framework
    RESPONSIBILITY: Dispatch to appropriate runner and handle errors
    PATTERNS: Guard clauses for validation
    """
    # Validate framework support
    if not _registry.is_supported(framework):
        from .parsers import create_error_result
        return create_error_result(
            framework,
            ValueError(f"Unsupported framework: {framework}")
        )

    # Get and run framework runner
    runner = _registry.get_runner(framework)
    if runner is None:
        from .parsers import create_error_result
        return create_error_result(
            framework,
            RuntimeError(f"Failed to get runner for: {framework}")
        )

    return runner.run(test_path, timeout)


def get_supported_frameworks() -> list[str]:
    """
    WHY: Expose list of supported frameworks
    RESPONSIBILITY: Return available test frameworks
    """
    return _registry.list_frameworks()


def register_custom_runner(framework: str, runner: BaseTestRunner) -> None:
    """
    WHY: Allow registration of custom test runners
    RESPONSIBILITY: Enable extension with user-defined frameworks
    """
    _registry.register_runner(framework, runner)
