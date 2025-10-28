#!/usr/bin/env python3
"""
WHY: Detects and identifies Java build systems
RESPONSIBILITY: Determines whether project uses Maven, Gradle, or other build systems
PATTERNS: Strategy Pattern (build system detection), Guard Clauses
"""

from pathlib import Path
from typing import Optional


class BuildSystemDetector:
    """
    WHY: Identifies the build system used by Java projects
    RESPONSIBILITY: Checks for Maven and Gradle build files
    PATTERNS: Strategy Pattern for extensible build system detection
    """

    def __init__(self, project_dir: Path):
        """
        Initialize build system detector

        Args:
            project_dir: Java project root directory
        """
        self.project_dir = project_dir
        self.pom_path = self.project_dir / "pom.xml"
        self.gradle_path = self.project_dir / "build.gradle"
        self.gradle_kts_path = self.project_dir / "build.gradle.kts"

    def detect(self) -> str:
        """
        WHY: Identifies the build system used by the project
        RESPONSIBILITY: Checks for Maven or Gradle build files

        Returns:
            Build system name (Maven, Gradle, or Unknown)
        """
        if self.pom_path.exists():
            return "Maven"

        if self.gradle_path.exists() or self.gradle_kts_path.exists():
            return "Gradle"

        return "Unknown"

    def get_maven_path(self) -> Optional[Path]:
        """
        WHY: Provides access to Maven POM file path
        RESPONSIBILITY: Returns Maven build file path if exists

        Returns:
            Path to pom.xml if exists, None otherwise
        """
        return self.pom_path if self.pom_path.exists() else None

    def get_gradle_path(self) -> Optional[Path]:
        """
        WHY: Provides access to Gradle build file path
        RESPONSIBILITY: Returns Gradle build file path if exists

        Returns:
            Path to build.gradle or build.gradle.kts if exists, None otherwise
        """
        if self.gradle_path.exists():
            return self.gradle_path
        if self.gradle_kts_path.exists():
            return self.gradle_kts_path
        return None
