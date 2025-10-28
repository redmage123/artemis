#!/usr/bin/env python3
"""
WHY: Analyze Gradle project structure and extract comprehensive information.

RESPONSIBILITY:
- Query Gradle for project properties
- Detect Android projects via plugins
- Determine multi-project structure
- Aggregate project metadata
- Coordinate parsing of build files

PATTERNS:
- Composition over inheritance (uses parser components)
- Guard clauses for validation
- Single Responsibility: project analysis only
- Delegation to specialized parsers
"""

import subprocess
from pathlib import Path
from typing import Dict, Optional
import logging

from managers.build_managers.gradle.models import (
    GradleDSL,
    GradlePlugin,
    GradleProjectInfo
)
from managers.build_managers.gradle.build_file_parser import BuildFileParser
from managers.build_managers.gradle.dependency_manager import DependencyManager


class ProjectAnalyzer:
    """
    WHY: Centralized project analysis and metadata extraction.

    RESPONSIBILITY:
    - Coordinate all parsing activities
    - Query Gradle for runtime properties
    - Aggregate information into GradleProjectInfo
    - Detect project type (Android, multi-project)

    PATTERNS:
    - Composition of specialized parsers
    - Guard clauses for file existence
    - Delegation pattern
    - Single source of truth (GradleProjectInfo)
    """

    def __init__(
        self,
        gradle_cmd: str,
        project_dir: Path,
        logger: Optional[logging.Logger] = None
    ):
        """
        WHY: Initialize analyzer with Gradle context.

        PATTERNS:
        - Dependency injection
        - Optional logger with fallback
        """
        self.gradle_cmd = gradle_cmd
        self.project_dir = project_dir
        self.logger = logger or logging.getLogger(__name__)

    def analyze_project(self) -> GradleProjectInfo:
        """
        WHY: Perform comprehensive project analysis.

        RESPONSIBILITY:
        - Validate project structure
        - Parse all build files
        - Query Gradle properties
        - Aggregate into GradleProjectInfo
        - Detect special project types

        PATTERNS:
        - Guard clause for validation
        - Delegation to specialized methods
        - Single return point (result object)
        """
        # Locate build files
        build_file = BuildFileParser.find_build_file(self.project_dir)
        if not build_file:
            raise FileNotFoundError(
                f"No Gradle build file found in {self.project_dir}"
            )

        settings_file = BuildFileParser.find_settings_file(self.project_dir)

        # Determine DSL type
        dsl = BuildFileParser.get_dsl_type(build_file)

        # Get project properties from Gradle
        props = self._get_gradle_properties()

        # Extract metadata
        name = props.get("name", self.project_dir.name)
        version = props.get("version", "unspecified")
        group = props.get("group", "")

        # Parse build file components
        plugins = BuildFileParser.parse_plugins(build_file)
        dependencies = DependencyManager.parse_dependencies(build_file)

        # Get subprojects if settings file exists
        subprojects = []
        if settings_file:
            subprojects = BuildFileParser.parse_subprojects(settings_file)

        # Get available tasks
        tasks = self._get_available_tasks()

        # Detect Android project
        is_android = self._is_android_project(plugins)

        # Get Java compatibility
        source_compat, target_compat = BuildFileParser.parse_java_compatibility(
            build_file
        )

        return GradleProjectInfo(
            name=name,
            version=version,
            group=group,
            dsl=dsl,
            plugins=plugins,
            dependencies=dependencies,
            subprojects=subprojects,
            tasks=tasks,
            properties=props,
            is_multi_project=len(subprojects) > 0,
            is_android=is_android,
            source_compatibility=source_compat,
            target_compatibility=target_compat
        )

    def _get_gradle_properties(self) -> Dict[str, str]:
        """
        WHY: Query Gradle for project properties at runtime.

        RESPONSIBILITY:
        - Execute 'gradle properties --quiet'
        - Parse key-value output
        - Return as dictionary

        PATTERNS:
        - Guard clause for exceptions
        - Exception handling with empty dict fallback
        - Line-by-line parsing
        """
        try:
            result = subprocess.run(
                [self.gradle_cmd, "properties", "--quiet"],
                cwd=str(self.project_dir),
                capture_output=True,
                text=True,
                timeout=30
            )

            props = {}
            for line in result.stdout.splitlines():
                if ": " not in line:
                    continue

                key, value = line.split(": ", 1)
                props[key.strip()] = value.strip()

            return props

        except Exception as e:
            self.logger.warning(f"Failed to get Gradle properties: {e}")
            return {}

    def _get_available_tasks(self) -> list[str]:
        """
        WHY: Query Gradle for available tasks.

        RESPONSIBILITY:
        - Execute 'gradle tasks --quiet'
        - Parse task names from output
        - Return task list

        PATTERNS:
        - Guard clause for exceptions
        - Exception handling with empty list fallback
        - Delegation to helper method
        """
        try:
            result = subprocess.run(
                [self.gradle_cmd, "tasks", "--quiet"],
                cwd=str(self.project_dir),
                capture_output=True,
                text=True,
                timeout=30
            )

            tasks = []
            for line in result.stdout.splitlines():
                task = self._extract_task_name(line)
                if task:
                    tasks.append(task)

            return tasks

        except Exception as e:
            self.logger.warning(f"Failed to get tasks: {e}")
            return []

    @staticmethod
    def _extract_task_name(line: str) -> Optional[str]:
        """
        WHY: Extract task name from 'gradle tasks' output line.

        PATTERNS:
        - Guard clauses for invalid lines
        - String parsing
        """
        # Tasks are listed as "taskName - description"
        if " - " not in line or line.startswith("-"):
            return None

        task = line.split(" - ")[0].strip()
        return task if task else None

    @staticmethod
    def _is_android_project(plugins: list[GradlePlugin]) -> bool:
        """
        WHY: Detect Android projects by plugin presence.

        PATTERNS:
        - Simple list comprehension with any()
        - Plugin ID pattern matching
        """
        return any("com.android" in p.plugin_id for p in plugins)
