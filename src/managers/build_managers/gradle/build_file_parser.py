#!/usr/bin/env python3
"""
WHY: Parse Gradle build files (Groovy and Kotlin DSL) to extract configuration.

RESPONSIBILITY:
- Parse plugins from plugins {} block and apply plugin: syntax
- Extract Java compatibility settings
- Locate and read build.gradle or build.gradle.kts files
- Parse settings.gradle for subprojects

PATTERNS:
- Regex-based parsing for DSL-agnostic extraction
- Guard clauses for file existence
- Dispatch tables for pattern matching
- Single Responsibility: parsing only, no execution
"""

import re
from pathlib import Path
from typing import List, Optional, Tuple

from managers.build_managers.gradle.models import GradleDSL, GradlePlugin


class BuildFileParser:
    """
    WHY: Centralized parsing logic for Gradle build files.

    RESPONSIBILITY:
    - Detect build file type (Groovy vs Kotlin)
    - Parse plugin declarations
    - Extract Java compatibility versions
    - Parse subproject inclusions

    PATTERNS:
    - Static methods for stateless parsing
    - Guard clauses for early returns
    - Pattern-based extraction
    """

    @staticmethod
    def find_build_file(project_dir: Path) -> Optional[Path]:
        """
        WHY: Locate Gradle build file, preferring Kotlin DSL.

        PATTERNS:
        - Guard clause: check Kotlin first (modern preference)
        - Early return on first match
        """
        kotlin = project_dir / "build.gradle.kts"
        if kotlin.exists():
            return kotlin

        groovy = project_dir / "build.gradle"
        if groovy.exists():
            return groovy

        return None

    @staticmethod
    def find_settings_file(project_dir: Path) -> Optional[Path]:
        """
        WHY: Locate Gradle settings file for multi-project builds.

        PATTERNS:
        - Same preference logic as build files
        - Guard clause pattern
        """
        kotlin_settings = project_dir / "settings.gradle.kts"
        if kotlin_settings.exists():
            return kotlin_settings

        groovy_settings = project_dir / "settings.gradle"
        if groovy_settings.exists():
            return groovy_settings

        return None

    @staticmethod
    def get_dsl_type(build_file: Path) -> GradleDSL:
        """
        WHY: Determine DSL type from file extension.

        PATTERNS:
        - Simple suffix check
        - Type-safe enum return
        """
        return GradleDSL.KOTLIN if build_file.suffix == ".kts" else GradleDSL.GROOVY

    @staticmethod
    def parse_plugins(build_file: Path) -> List[GradlePlugin]:
        """
        WHY: Extract all plugin declarations from build file.

        RESPONSIBILITY:
        - Parse plugins {} block syntax
        - Parse legacy apply plugin: syntax
        - Deduplicate plugin IDs

        PATTERNS:
        - Multi-pattern matching
        - Guard clause for file existence
        - Deduplication via set comprehension
        """
        if not build_file.exists():
            return []

        content = build_file.read_text()
        plugins = []

        # Parse plugins {} block
        # Match: id 'plugin-id' version 'x.y.z' or id("plugin-id") version "x.y.z"
        plugin_pattern = r"id\s*[\(\[]?['\"]([^'\"]+)['\"][\)\]]?\s*(?:version\s*[\(\[]?['\"]([^'\"]+)['\"][\)\]]?)?"

        for match in re.finditer(plugin_pattern, content):
            plugin_id = match.group(1)
            version = match.group(2)

            plugins.append(GradlePlugin(
                plugin_id=plugin_id,
                version=version
            ))

        # Parse legacy apply plugin syntax
        # Match: apply plugin: 'plugin-id'
        apply_pattern = r"apply\s+plugin:\s*['\"]([^'\"]+)['\"]"

        for match in re.finditer(apply_pattern, content):
            plugin_id = match.group(1)
            # Only add if not already in list
            if not any(p.plugin_id == plugin_id for p in plugins):
                plugins.append(GradlePlugin(plugin_id=plugin_id))

        return plugins

    @staticmethod
    def parse_java_compatibility(build_file: Path) -> Tuple[Optional[str], Optional[str]]:
        """
        WHY: Extract Java source and target compatibility versions.

        RESPONSIBILITY:
        - Parse sourceCompatibility setting
        - Parse targetCompatibility setting
        - Handle both quoted and unquoted values

        PATTERNS:
        - Regex with optional quotes
        - Guard clause for file existence
        - Tuple return for paired values
        """
        if not build_file.exists():
            return None, None

        content = build_file.read_text()

        source_match = re.search(
            r"sourceCompatibility\s*=\s*['\"]?([^'\"\\s]+)",
            content
        )
        target_match = re.search(
            r"targetCompatibility\s*=\s*['\"]?([^'\"\\s]+)",
            content
        )

        source = source_match.group(1) if source_match else None
        target = target_match.group(1) if target_match else None

        return source, target

    @staticmethod
    def parse_subprojects(settings_file: Path) -> List[str]:
        """
        WHY: Extract subproject declarations from settings file.

        RESPONSIBILITY:
        - Parse include statements
        - Strip leading colons from project paths
        - Handle both Groovy and Kotlin syntax

        PATTERNS:
        - Guard clause for file existence
        - Regex pattern matching
        - String normalization (strip :)
        """
        if not settings_file.exists():
            return []

        content = settings_file.read_text()
        subprojects = []

        # Match: include ':subproject' or include(":subproject")
        pattern = r"include\s*[\(\[]?['\"]([^'\"]+)['\"][\)\]]?"

        for match in re.finditer(pattern, content):
            subproject = match.group(1).lstrip(":")
            subprojects.append(subproject)

        return subprojects
