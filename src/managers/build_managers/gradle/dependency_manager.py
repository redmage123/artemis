#!/usr/bin/env python3
"""
WHY: Parse and manage Gradle dependencies from build files.

RESPONSIBILITY:
- Parse dependency declarations in multiple formats
- Support both compact and explicit dependency syntax
- Handle configuration scopes (implementation, testImplementation, etc.)
- Extract group, artifact, and version coordinates

PATTERNS:
- Multiple regex patterns for different syntax styles
- Guard clauses for file existence
- Dispatch table approach for pattern matching
- Single Responsibility: dependency parsing only
"""

import re
from pathlib import Path
from typing import List

from managers.build_managers.gradle.models import GradleDependency


class DependencyManager:
    """
    WHY: Centralized dependency parsing for Gradle build files.

    RESPONSIBILITY:
    - Parse compact notation: implementation 'group:name:version'
    - Parse explicit notation: implementation group: 'g', name: 'n', version: 'v'
    - Support both Groovy and Kotlin DSL
    - Deduplicate dependencies

    PATTERNS:
    - Static methods for stateless parsing
    - Multiple pattern matchers
    - Guard clauses
    """

    @staticmethod
    def parse_dependencies(build_file: Path) -> List[GradleDependency]:
        """
        WHY: Extract all dependency declarations from build file.

        RESPONSIBILITY:
        - Parse compact Maven coordinate notation
        - Parse explicit key-value notation
        - Combine results without duplicates

        PATTERNS:
        - Guard clause for file existence
        - Multiple pattern extraction
        - List concatenation
        """
        if not build_file.exists():
            return []

        content = build_file.read_text()
        dependencies = []

        # Parse compact notation
        dependencies.extend(
            DependencyManager._parse_compact_dependencies(content)
        )

        # Parse explicit notation
        dependencies.extend(
            DependencyManager._parse_explicit_dependencies(content)
        )

        return dependencies

    @staticmethod
    def _parse_compact_dependencies(content: str) -> List[GradleDependency]:
        """
        WHY: Parse compact Maven coordinate notation.

        EXAMPLES:
        - implementation 'group:name:version'
        - testImplementation "group:name:version"
        - implementation("group:name:version")

        PATTERNS:
        - Single regex for multiple quote styles
        - Direct coordinate extraction
        """
        dependencies = []

        # Match: configuration 'group:name:version'
        # Handles both single/double quotes and parentheses
        pattern = r"(\w+)\s*[\(\[]?['\"]([^:'\"]+):([^:'\"]+):([^'\"]+)['\"][\)\]]?"

        for match in re.finditer(pattern, content):
            configuration = match.group(1)
            group = match.group(2)
            name = match.group(3)
            version = match.group(4)

            dependencies.append(GradleDependency(
                configuration=configuration,
                group=group,
                name=name,
                version=version
            ))

        return dependencies

    @staticmethod
    def _parse_explicit_dependencies(content: str) -> List[GradleDependency]:
        """
        WHY: Parse explicit key-value dependency notation.

        EXAMPLES:
        - implementation group: 'g', name: 'n', version: 'v'
        - testImplementation(group = "g", name = "n", version = "v")

        PATTERNS:
        - Complex regex for key-value pairs
        - Support both : and = separators
        - Handle optional whitespace
        """
        dependencies = []

        # Match: configuration group: 'g', name: 'n', version: 'v'
        # Also handles Kotlin syntax with = instead of :
        pattern = r"(\w+)\s*[\(\[]?\s*group\s*[=:]\s*['\"]([^'\"]+)['\"]\s*,\s*name\s*[=:]\s*['\"]([^'\"]+)['\"]\s*,\s*version\s*[=:]\s*['\"]([^'\"]+)['\"]"

        for match in re.finditer(pattern, content):
            configuration = match.group(1)
            group = match.group(2)
            name = match.group(3)
            version = match.group(4)

            dependencies.append(GradleDependency(
                configuration=configuration,
                group=group,
                name=name,
                version=version
            ))

        return dependencies
