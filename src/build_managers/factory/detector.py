#!/usr/bin/env python3
"""
WHY: Auto-detect build system from project files
RESPONSIBILITY: Scan project directory for build markers
PATTERNS: Strategy (detection strategies), Dispatch Table (marker map)

Build system detection enables zero-config build manager creation.
"""

from pathlib import Path
from typing import Dict, List, Optional
from build_managers.factory.enums import BuildSystem


# Dispatch table: Build system → marker files
DETECTION_MAP: Dict[BuildSystem, List[str]] = {
    BuildSystem.MAVEN: ["pom.xml"],
    BuildSystem.GRADLE: ["build.gradle", "build.gradle.kts"],
    BuildSystem.NPM: ["package-lock.json"],
    BuildSystem.YARN: ["yarn.lock"],
    BuildSystem.PNPM: ["pnpm-lock.yaml"],
    BuildSystem.CARGO: ["Cargo.toml"],
    BuildSystem.CMAKE: ["CMakeLists.txt"],
    BuildSystem.GO_MOD: ["go.mod"],
    BuildSystem.POETRY: ["poetry.lock"],
    BuildSystem.PIPENV: ["Pipfile.lock"],
    BuildSystem.COMPOSER: ["composer.json"],
    BuildSystem.BUNDLER: ["Gemfile.lock"],
    BuildSystem.DOTNET: ["*.csproj", "*.sln"],
    BuildSystem.LUA: ["*.rockspec", ".busted", "init.lua"]
}


class BuildSystemDetector:
    """
    Detects build system from project files.

    WHY: Auto-detection enables zero-configuration usage.
    RESPONSIBILITY: Scan project for build system markers.
    PATTERNS: Strategy (detection logic), Dispatch table (marker mapping).
    """

    @staticmethod
    def detect(
        project_dir: Path,
        registered_systems: List[BuildSystem]
    ) -> Optional[BuildSystem]:
        """
        Detect build system in project directory.

        WHY: Automatic detection improves user experience.

        Args:
            project_dir: Project directory to scan
            registered_systems: List of registered build systems to consider

        Returns:
            Detected BuildSystem or None

        Example:
            >>> detector = BuildSystemDetector()
            >>> system = detector.detect(Path("/my/project"), [BuildSystem.MAVEN, BuildSystem.NPM])
            >>> system
            BuildSystem.MAVEN
        """
        # Guard clause - directory must exist
        if not project_dir.exists():
            return None

        # Check each build system in order (most specific first)
        for build_system, markers in DETECTION_MAP.items():
            # Skip unregistered systems
            if build_system not in registered_systems:
                continue

            # Check if any marker files exist
            if BuildSystemDetector._has_markers(project_dir, markers):
                return build_system

        return None

    @staticmethod
    def _has_markers(project_dir: Path, markers: List[str]) -> bool:
        """
        Check if any marker files exist in project directory.

        WHY: Different markers may indicate the same build system.

        Args:
            project_dir: Project directory
            markers: List of marker patterns

        Returns:
            True if any marker found
        """
        for marker in markers:
            # Handle glob patterns
            if "*" in marker:
                if list(project_dir.glob(marker)):
                    return True
            else:
                # Exact file match
                if (project_dir / marker).exists():
                    return True

        return False
