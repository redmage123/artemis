#!/usr/bin/env python3
"""
WHY: Facade orchestrator for Gradle build system operations.

RESPONSIBILITY:
- Provide unified interface to all Gradle operations
- Coordinate wrapper detection, parsing, and execution
- Simplify API for consumers
- Delegate to specialized components

PATTERNS:
- Facade pattern (unified interface)
- Composition over inheritance
- Delegation to specialized managers
- Single entry point for Gradle operations
"""

from pathlib import Path
from typing import List, Optional
import logging

from managers.build_managers.gradle.models import (
    GradleBuildResult,
    GradleProjectInfo
)
from managers.build_managers.gradle.gradle_wrapper import GradleWrapper
from managers.build_managers.gradle.project_analyzer import ProjectAnalyzer
from managers.build_managers.gradle.task_executor import TaskExecutor
from managers.build_managers.gradle.build_file_parser import BuildFileParser


class GradleManager:
    """
    WHY: Unified facade for comprehensive Gradle integration.

    RESPONSIBILITY:
    - Initialize and coordinate all Gradle components
    - Provide simple API for project analysis
    - Execute builds and tests
    - Handle wrapper detection automatically

    PATTERNS:
    - Facade pattern
    - Lazy initialization of components
    - Delegation to specialists
    - Guard clauses for validation
    """

    def __init__(
        self,
        project_dir: Optional[Path] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        WHY: Initialize Gradle manager with project context.

        RESPONSIBILITY:
        - Set project directory
        - Initialize logger
        - Detect and validate Gradle wrapper
        - Prepare components for delegation

        PATTERNS:
        - Dependency injection (logger)
        - Eager wrapper validation
        - Lazy component initialization
        """
        self.project_dir = Path(project_dir) if project_dir else Path.cwd()
        self.logger = logger or logging.getLogger(__name__)

        # Detect and validate Gradle wrapper/installation
        self.wrapper = GradleWrapper(self.project_dir, self.logger)

        # Initialize components (lazy)
        self._analyzer: Optional[ProjectAnalyzer] = None
        self._executor: Optional[TaskExecutor] = None

    @property
    def analyzer(self) -> ProjectAnalyzer:
        """
        WHY: Lazy initialization of project analyzer.

        PATTERNS:
        - Lazy initialization
        - Property pattern
        - Guard clause for None check
        """
        if self._analyzer is None:
            self._analyzer = ProjectAnalyzer(
                gradle_cmd=self.wrapper.get_command(),
                project_dir=self.project_dir,
                logger=self.logger
            )
        return self._analyzer

    @property
    def executor(self) -> TaskExecutor:
        """
        WHY: Lazy initialization of task executor.

        PATTERNS:
        - Lazy initialization
        - Property pattern
        - Guard clause for None check
        """
        if self._executor is None:
            self._executor = TaskExecutor(
                gradle_cmd=self.wrapper.get_command(),
                project_dir=self.project_dir,
                logger=self.logger
            )
        return self._executor

    def is_gradle_project(self) -> bool:
        """
        WHY: Quick check if directory contains Gradle project.

        RESPONSIBILITY:
        - Check for build.gradle or build.gradle.kts
        - Check for settings file

        PATTERNS:
        - Guard clause pattern
        - Delegation to parser
        """
        build_file = BuildFileParser.find_build_file(self.project_dir)
        settings_file = BuildFileParser.find_settings_file(self.project_dir)

        return build_file is not None or settings_file is not None

    def get_project_info(self) -> GradleProjectInfo:
        """
        WHY: Analyze project and return comprehensive information.

        RESPONSIBILITY:
        - Delegate to ProjectAnalyzer
        - Return structured project info

        PATTERNS:
        - Delegation pattern
        - Single method call for consumers
        """
        return self.analyzer.analyze_project()

    def build(
        self,
        task: str = "build",
        clean: bool = True,
        offline: bool = False,
        extra_args: Optional[List[str]] = None,
        timeout: int = 600
    ) -> GradleBuildResult:
        """
        WHY: Execute Gradle build with configurable options.

        RESPONSIBILITY:
        - Delegate to TaskExecutor
        - Provide sensible defaults
        - Return structured build result

        PATTERNS:
        - Delegation pattern
        - Default parameters for common use cases
        """
        return self.executor.execute_build(
            task=task,
            clean=clean,
            offline=offline,
            extra_args=extra_args,
            timeout=timeout
        )

    def run_tests(
        self,
        test_class: Optional[str] = None,
        test_method: Optional[str] = None,
        timeout: int = 300
    ) -> GradleBuildResult:
        """
        WHY: Execute Gradle tests with optional filtering.

        RESPONSIBILITY:
        - Delegate to TaskExecutor
        - Support class/method filtering
        - Return structured test results

        PATTERNS:
        - Delegation pattern
        - Optional filtering via parameters
        """
        return self.executor.execute_tests(
            test_class=test_class,
            test_method=test_method,
            timeout=timeout
        )

    def get_available_tasks(self) -> List[str]:
        """
        WHY: Query available Gradle tasks.

        RESPONSIBILITY:
        - Delegate to TaskExecutor
        - Return task list

        PATTERNS:
        - Delegation pattern
        - Simple passthrough
        """
        return self.executor.get_available_tasks()
