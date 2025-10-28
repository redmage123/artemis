#!/usr/bin/env python3
"""
WHY: Auto-detect test framework from project structure
RESPONSIBILITY: Analyze project files to identify test framework
PATTERNS: Strategy Pattern, Guard Clauses

This module implements framework detection logic that examines project
files and test code to automatically determine the appropriate test
framework to use.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Callable

from artemis_exceptions import wrap_exception
from stages.testing.models import TestFramework
from stages.testing.exceptions import TestRunnerError


class FrameworkDetector:
    """
    WHY: Automatic framework detection from project structure
    RESPONSIBILITY: Identify test framework without user input
    PATTERNS: Strategy Pattern, Dispatch Table

    Detection strategy:
    1. File extension-based detection (.jmx, .robot)
    2. Configuration file detection (package.json, pytest.ini)
    3. Import-based detection (analyze test file imports)
    4. Fallback to pytest

    Guard Clauses: Max 1 level nesting throughout
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        WHY: Dependency injection for logging
        RESPONSIBILITY: Initialize detector with optional logger

        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger("FrameworkDetector")
        self._detection_strategies = self._build_detection_strategies()

    def _build_detection_strategies(self) -> Dict[str, Callable[[Path], Optional[str]]]:
        """
        WHY: Dispatch table for detection strategies
        RESPONSIBILITY: Map detection methods to strategies
        PATTERNS: Dispatch Table Pattern

        Returns:
            Dictionary mapping strategy names to detection methods
        """
        return {
            'jmeter_files': self._detect_jmeter,
            'robot_files': self._detect_robot,
            'jest_project': self._detect_jest,
            'pytest_markers': self._detect_pytest_markers,
            'python_imports': self._detect_from_python_files,
            'cpp_files': self._detect_gtest,
            'java_files': self._detect_junit,
        }

    @wrap_exception(TestRunnerError, "Framework detection failed")
    def detect_framework(self, test_path: Path) -> str:
        """
        WHY: Identify test framework from project structure
        RESPONSIBILITY: Run detection strategies in priority order

        Args:
            test_path: Path to test directory or file

        Returns:
            Framework name string
        """
        for strategy_name, strategy_fn in self._detection_strategies.items():
            framework = strategy_fn(test_path)
            if framework:
                self.logger.info(f"Detected framework via {strategy_name}: {framework}")
                return framework

        self.logger.warning("Could not detect framework, defaulting to pytest")
        return TestFramework.PYTEST.value

    def _detect_jmeter(self, test_path: Path) -> Optional[str]:
        """
        WHY: Detect JMeter test plans
        RESPONSIBILITY: Check for .jmx files

        Args:
            test_path: Path to check

        Returns:
            Framework name or None
        """
        if list(test_path.glob("**/*.jmx")):
            return TestFramework.JMETER.value
        return None

    def _detect_robot(self, test_path: Path) -> Optional[str]:
        """
        WHY: Detect Robot Framework tests
        RESPONSIBILITY: Check for .robot files

        Args:
            test_path: Path to check

        Returns:
            Framework name or None
        """
        if list(test_path.glob("**/*.robot")):
            return TestFramework.ROBOT.value
        return None

    def _detect_jest(self, test_path: Path) -> Optional[str]:
        """
        WHY: Detect Jest (JavaScript) project
        RESPONSIBILITY: Check for Jest configuration and test files

        Args:
            test_path: Path to check

        Returns:
            Framework name or None
        """
        if not self._is_jest_project(test_path):
            return None

        js_test_files = list(test_path.glob("**/*.test.js")) + list(test_path.glob("**/*.test.ts"))
        if js_test_files:
            return TestFramework.JEST.value

        return None

    def _is_jest_project(self, test_path: Path) -> bool:
        """
        WHY: Check for Jest project markers
        RESPONSIBILITY: Verify Jest configuration exists

        Args:
            test_path: Path to check

        Returns:
            True if Jest project detected
        """
        has_package_json = (test_path / "package.json").exists()
        has_jest_config = (test_path / "jest.config.js").exists()

        return has_package_json or has_jest_config

    def _detect_pytest_markers(self, test_path: Path) -> Optional[str]:
        """
        WHY: Detect pytest via configuration files
        RESPONSIBILITY: Check for pytest markers (conftest.py, pytest.ini)

        Args:
            test_path: Path to check

        Returns:
            Framework name or None
        """
        has_conftest = bool(list(test_path.glob("**/conftest.py")))
        has_pytest_ini = bool(list(test_path.glob("**/pytest.ini")))

        if has_conftest or has_pytest_ini:
            return TestFramework.PYTEST.value

        return None

    @wrap_exception(TestRunnerError, "Failed to detect framework from Python files")
    def _detect_from_python_files(self, test_path: Path) -> Optional[str]:
        """
        WHY: Detect framework from Python test file imports
        RESPONSIBILITY: Analyze import statements in test files

        Args:
            test_path: Path to check

        Returns:
            Framework name or None
        """
        python_files = list(test_path.glob("**/test_*.py")) + list(test_path.glob("**/*_test.py"))

        if not python_files:
            return None

        python_files = sorted(python_files, key=lambda p: p.stat().st_mtime, reverse=True)

        try:
            with open(python_files[0], 'r') as f:
                content = f.read()
                return self._detect_framework_from_imports(content)
        except (IOError, OSError) as e:
            self.logger.warning(f"Could not read test file: {e}")
            return None

    def _detect_framework_from_imports(self, content: str) -> Optional[str]:
        """
        WHY: Identify framework from import statements
        RESPONSIBILITY: Map imports to frameworks
        PATTERNS: Guard Clauses

        Args:
            content: File content to analyze

        Returns:
            Framework name or None
        """
        import_checks = {
            TestFramework.PLAYWRIGHT.value: ["from playwright", "import playwright"],
            TestFramework.SELENIUM.value: ["from selenium", "import selenium"],
            TestFramework.APPIUM.value: ["from appium", "import appium"],
            TestFramework.HYPOTHESIS.value: ["from hypothesis", "@given"],
            TestFramework.UNITTEST.value: ["import unittest"],
            TestFramework.PYTEST.value: ["import pytest"],
        }

        for framework, patterns in import_checks.items():
            if any(pattern in content for pattern in patterns):
                return framework

        return None

    def _detect_gtest(self, test_path: Path) -> Optional[str]:
        """
        WHY: Detect Google Test (C++)
        RESPONSIBILITY: Check for C++ test files

        Args:
            test_path: Path to check

        Returns:
            Framework name or None
        """
        cpp_tests = list(test_path.glob("**/*_test.cpp")) + list(test_path.glob("**/*_test.cc"))
        if cpp_tests:
            return TestFramework.GTEST.value
        return None

    def _detect_junit(self, test_path: Path) -> Optional[str]:
        """
        WHY: Detect JUnit (Java)
        RESPONSIBILITY: Check for Java test files

        Args:
            test_path: Path to check

        Returns:
            Framework name or None
        """
        java_tests = list(test_path.glob("**/*Test.java"))
        if java_tests:
            return TestFramework.JUNIT.value
        return None
