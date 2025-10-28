#!/usr/bin/env python3
"""
Testing Framework Selector - Project and Framework Detection

WHY: Automatic detection of project types and existing frameworks enables
intelligent framework selection without manual configuration. Analyzing
project structure and files provides context for recommendations.

RESPONSIBILITY: Detect project type (language, platform) and existing test
frameworks from file system analysis. Single responsibility - detection only,
no selection logic.

PATTERNS: Strategy pattern with dispatch tables for detection rules.
Guard clauses for early returns.

Used by selector_core to understand project context.
"""

from pathlib import Path
from typing import Optional, Dict, Callable, List
from testing.selector.models import ProjectType


class ProjectDetector:
    """
    Detects project type from directory structure.

    WHY: Different project types require different testing frameworks.
    Automatic detection eliminates need for manual configuration.

    RESPONSIBILITY: Analyze file system to determine project language
    and technology stack. Single responsibility - detection only.

    PATTERNS: Strategy pattern with dispatch tables for detection.
    """

    def __init__(self, project_dir: Optional[Path] = None):
        """
        Initialize detector with project directory.

        Args:
            project_dir: Project root directory for analysis
        """
        self.project_dir = Path(project_dir) if project_dir else None

    def detect_project_type(self) -> ProjectType:
        """
        Detect project type from directory structure.

        WHY: Automatic project type detection enables framework selection
        without manual configuration. Examines file extensions and project
        metadata to infer language and technology stack.

        PERFORMANCE: Uses glob patterns for efficient file system scanning.
        Early returns avoid unnecessary file system operations.

        Returns:
            ProjectType enum value indicating detected project type
        """
        # Guard clause: Early return for invalid directory
        if not self.project_dir or not self.project_dir.exists():
            return ProjectType.UNKNOWN

        # Strategy pattern: Dispatch table for detection functions
        # WHY: Easily extensible for new project types, testable independently
        detection_strategies: Dict[str, Callable[[], bool]] = {
            "python": self._is_python_project,
            "java": self._is_java_project,
            "cpp": self._is_cpp_project,
            "javascript": self._is_javascript_project
        }

        # Execute detection strategies in priority order
        for project_type_str, strategy in detection_strategies.items():
            if strategy():
                return ProjectType(project_type_str)

        return ProjectType.UNKNOWN

    def _is_python_project(self) -> bool:
        """
        Check if project is Python-based.

        WHY: Python is the most common Artemis project type, check first
        for performance.

        Returns:
            True if Python files found
        """
        return bool(list(self.project_dir.glob("**/*.py")))

    def _is_java_project(self) -> bool:
        """
        Check if project is Java-based.

        Returns:
            True if Java files found
        """
        return bool(list(self.project_dir.glob("**/*.java")))

    def _is_cpp_project(self) -> bool:
        """
        Check if project is C++-based.

        Returns:
            True if C++ files found
        """
        has_cpp = bool(list(self.project_dir.glob("**/*.cpp")))
        has_cc = bool(list(self.project_dir.glob("**/*.cc")))
        return has_cpp or has_cc

    def _is_javascript_project(self) -> bool:
        """
        Check if project is JavaScript/TypeScript-based.

        WHY: JavaScript projects identified by package.json presence.
        Further distinction between JS/TS handled by detect_js_project_type.

        Returns:
            True if package.json found
        """
        return (self.project_dir / "package.json").exists()

    def detect_js_project_type(self) -> ProjectType:
        """
        Detect if JavaScript project is TypeScript or JavaScript.

        WHY: TypeScript and JavaScript require different test configurations.
        TypeScript projects may need additional transpilation setup.

        Returns:
            ProjectType.TYPESCRIPT if .ts files found, else ProjectType.JAVASCRIPT
        """
        # Guard clause: Early return for TypeScript
        if list(self.project_dir.glob("**/*.ts")):
            return ProjectType.TYPESCRIPT
        return ProjectType.JAVASCRIPT

    def infer_language(self, project_type: ProjectType) -> str:
        """
        Infer programming language from project type.

        WHY: Language inference enables framework selection when language
        not explicitly specified in requirements. Uses Strategy pattern
        with dictionary mapping to avoid if/elif chains.

        PATTERNS: Strategy pattern - dictionary mapping for type-to-language conversion.

        Args:
            project_type: Detected project type

        Returns:
            String representation of programming language (default: "python")
        """
        # Strategy pattern: Dictionary mapping instead of if/elif chain
        # WHY: O(1) lookup, easily extensible for new languages
        type_to_lang: Dict[ProjectType, str] = {
            ProjectType.PYTHON: "python",
            ProjectType.JAVASCRIPT: "javascript",
            ProjectType.TYPESCRIPT: "typescript",
            ProjectType.JAVA: "java",
            ProjectType.CPP: "cpp"
        }
        return type_to_lang.get(project_type, "python")


class FrameworkDetector:
    """
    Detects existing test frameworks in project.

    WHY: Consistency is important - if a project already uses a test
    framework, we should recommend continuing with it rather than
    introducing a new framework.

    RESPONSIBILITY: Analyze project files to identify existing testing
    frameworks. Single responsibility - detection only.

    PATTERNS: Strategy pattern with dispatch tables for framework detection.
    """

    def __init__(self, project_dir: Optional[Path] = None):
        """
        Initialize detector with project directory.

        Args:
            project_dir: Project root directory for analysis
        """
        self.project_dir = Path(project_dir) if project_dir else None

    def detect_existing_framework(self) -> Optional[str]:
        """
        Detect existing test framework from project.

        WHY: Prefer consistency - use existing framework if tests already exist.

        PERFORMANCE: Uses file system checks with early returns for efficiency.
        Checks most common frameworks first.

        Returns:
            Framework name if detected, None otherwise
        """
        # Guard clause: Early return if no project directory
        if not self.project_dir:
            return None

        # Strategy pattern: Dispatch table for framework detection
        # WHY: O(1) lookup, easily extensible, testable independently
        detection_strategies: Dict[str, Callable[[], bool]] = {
            "pytest": self._has_pytest,
            "jest": self._has_jest,
            "robot": self._has_robot,
            "jmeter": self._has_jmeter
        }

        # Check each framework in priority order
        for framework_name, strategy in detection_strategies.items():
            if strategy():
                return framework_name

        # Fallback: Check test file imports
        return self._detect_framework_from_test_files()

    def _has_pytest(self) -> bool:
        """
        Check if project uses pytest.

        WHY: pytest is the most common Python testing framework.
        Check via conftest.py or pytest.ini presence.

        Returns:
            True if pytest artifacts found
        """
        has_conftest = bool(list(self.project_dir.glob("**/conftest.py")))
        has_config = bool(list(self.project_dir.glob("**/pytest.ini")))
        return has_conftest or has_config

    def _has_jest(self) -> bool:
        """
        Check if project uses Jest.

        Returns:
            True if Jest config found
        """
        return (self.project_dir / "jest.config.js").exists()

    def _has_robot(self) -> bool:
        """
        Check if project uses Robot Framework.

        Returns:
            True if .robot files found
        """
        return bool(list(self.project_dir.glob("**/*.robot")))

    def _has_jmeter(self) -> bool:
        """
        Check if project uses JMeter.

        Returns:
            True if .jmx files found
        """
        return bool(list(self.project_dir.glob("**/*.jmx")))

    def _detect_framework_from_test_files(self) -> Optional[str]:
        """
        Detect framework by analyzing test file imports.

        WHY: When framework config files are absent, import statements
        in test files can reveal which framework is being used.

        PATTERNS: Strategy pattern with dictionary mapping for import detection.

        PERFORMANCE: Only reads first test file found (avoid scanning all files).

        Returns:
            Framework name if detected from imports, None otherwise
        """
        # Guard clause: Early return if no project directory
        if not self.project_dir:
            return None

        # Find test files
        test_files = self._find_test_files()

        # Guard clause: Early return if no test files found
        if not test_files:
            return None

        # Strategy pattern: Dictionary mapping for import patterns
        # WHY: Avoid sequential ifs, easily extensible for new frameworks
        import_patterns: Dict[str, str] = {
            "import pytest": "pytest",
            "import unittest": "unittest",
            "from playwright": "playwright",
            "from selenium": "selenium",
            "from appium": "appium",
            "from hypothesis": "hypothesis"
        }

        try:
            # Read first test file only (performance optimization)
            with open(test_files[0], 'r', encoding='utf-8') as f:
                content = f.read()

                # Check all patterns using dictionary mapping
                for pattern, framework in import_patterns.items():
                    if pattern in content:
                        return framework

        except (IOError, OSError, UnicodeDecodeError):
            # Guard clause: Silently handle file read errors
            # WHY: Framework detection is optional, shouldn't fail entire process
            return None

        return None

    def _find_test_files(self) -> List[Path]:
        """
        Find test files in project.

        WHY: Encapsulates test file discovery logic for reuse.

        Returns:
            List of test file paths
        """
        test_files = (
            list(self.project_dir.glob("**/test_*.py")) +
            list(self.project_dir.glob("**/*_test.py"))
        )
        return test_files
