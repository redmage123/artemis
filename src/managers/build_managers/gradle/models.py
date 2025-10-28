#!/usr/bin/env python3
"""
WHY: Data models for Gradle build system components.

RESPONSIBILITY:
- Define Gradle DSL types (Groovy/Kotlin)
- Model Gradle dependencies with configuration support
- Model Gradle plugins with version tracking
- Represent comprehensive project information
- Store build and test execution results

PATTERNS:
- Dataclasses for immutable data structures
- Enums for type safety
- Type hints for all fields
- Default factories for mutable collections
- String representations for debugging
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class GradleDSL(Enum):
    """
    WHY: Type-safe representation of Gradle build script formats.

    RESPONSIBILITY:
    - Distinguish between Groovy and Kotlin DSL
    - Enable DSL-specific parsing strategies
    """
    GROOVY = "groovy"  # build.gradle
    KOTLIN = "kotlin"  # build.gradle.kts


@dataclass
class GradleDependency:
    """
    WHY: Structured representation of Gradle dependencies.

    RESPONSIBILITY:
    - Store dependency coordinates (group:name:version)
    - Track configuration scope (implementation, testImplementation, etc.)
    - Provide readable string format

    PATTERNS:
    - Maven-style coordinate system
    - Configuration-based scoping
    """
    configuration: str  # implementation, testImplementation, etc.
    group: str
    name: str
    version: str

    def __str__(self) -> str:
        return f"{self.configuration} '{self.group}:{self.name}:{self.version}'"


@dataclass
class GradlePlugin:
    """
    WHY: Represent Gradle plugins with version and application status.

    RESPONSIBILITY:
    - Store plugin ID and optional version
    - Track whether plugin is applied
    - Support both plugins {} and apply plugin: syntax

    PATTERNS:
    - Optional versioning for compatibility
    - Apply flag for deferred application
    """
    plugin_id: str
    version: Optional[str] = None
    apply: bool = True

    def __str__(self) -> str:
        if self.version:
            return f"id '{self.plugin_id}' version '{self.version}'"
        return f"id '{self.plugin_id}'"


@dataclass
class GradleProjectInfo:
    """
    WHY: Comprehensive snapshot of Gradle project configuration.

    RESPONSIBILITY:
    - Aggregate all project metadata
    - Store plugins, dependencies, and subprojects
    - Track Java compatibility versions
    - Identify Android and multi-project builds

    PATTERNS:
    - Single source of truth for project state
    - Immutable snapshot approach
    - Guard clauses via Optional types
    """
    name: str
    version: str
    group: str
    dsl: GradleDSL
    plugins: List[GradlePlugin] = field(default_factory=list)
    dependencies: List[GradleDependency] = field(default_factory=list)
    subprojects: List[str] = field(default_factory=list)
    tasks: List[str] = field(default_factory=list)
    properties: Dict[str, str] = field(default_factory=dict)
    is_multi_project: bool = False
    is_android: bool = False
    source_compatibility: Optional[str] = None
    target_compatibility: Optional[str] = None


@dataclass
class GradleBuildResult:
    """
    WHY: Capture complete build/test execution outcome.

    RESPONSIBILITY:
    - Store success status and exit code
    - Track execution duration
    - Capture output and test metrics
    - Collect errors and warnings

    PATTERNS:
    - Result object pattern
    - Metrics collection
    - Error aggregation with limits
    """
    success: bool
    exit_code: int
    duration: float
    output: str
    task: str
    tests_run: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    tests_skipped: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
