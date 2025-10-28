"""
WHY: Gradle build system integration package.

RESPONSIBILITY:
- Export main GradleManager facade
- Export data models for type hints
- Export specialized components for advanced usage
- Provide backward compatibility

PATTERNS:
- Explicit __all__ for controlled exports
- Main facade as primary export
- Models for consumer type hints
- Optional component access

Part of: managers.build_managers

This package provides comprehensive Gradle integration:
- Groovy and Kotlin DSL support (build.gradle / build.gradle.kts)
- Project structure analysis and metadata extraction
- Dependency and plugin management
- Task execution (build, test, custom tasks)
- Multi-project builds support
- Android project detection
- Gradle wrapper integration

Architecture:
- gradle_manager: Main facade orchestrator
- models: Data classes and enums
- gradle_wrapper: Wrapper detection and validation
- build_file_parser: Build file parsing (plugins, settings, compatibility)
- dependency_manager: Dependency extraction
- project_analyzer: Project metadata aggregation
- task_executor: Build and test execution

Usage:
    from managers.build_managers.gradle import GradleManager

    gradle = GradleManager(project_dir="/path/to/project")
    info = gradle.get_project_info()
    result = gradle.build()
    test_result = gradle.run_tests()
"""

# Main facade (primary export)
from managers.build_managers.gradle.gradle_manager import GradleManager

# Models (for type hints and data structures)
from managers.build_managers.gradle.models import (
    GradleDSL,
    GradleDependency,
    GradlePlugin,
    GradleProjectInfo,
    GradleBuildResult
)

# Specialized components (for advanced usage)
from managers.build_managers.gradle.gradle_wrapper import GradleWrapper
from managers.build_managers.gradle.build_file_parser import BuildFileParser
from managers.build_managers.gradle.dependency_manager import DependencyManager
from managers.build_managers.gradle.project_analyzer import ProjectAnalyzer
from managers.build_managers.gradle.task_executor import TaskExecutor

__all__ = [
    # Main facade
    "GradleManager",

    # Models
    "GradleDSL",
    "GradleDependency",
    "GradlePlugin",
    "GradleProjectInfo",
    "GradleBuildResult",

    # Components (advanced usage)
    "GradleWrapper",
    "BuildFileParser",
    "DependencyManager",
    "ProjectAnalyzer",
    "TaskExecutor",
]
