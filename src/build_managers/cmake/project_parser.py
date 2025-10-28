#!/usr/bin/env python3
"""
WHY: Parse CMakeLists.txt for project metadata
RESPONSIBILITY: Extract project name, version, languages from CMakeLists.txt
PATTERNS: Parser (regex-based), Guard Clauses

Project parser extracts structured data from CMakeLists.txt without
executing CMake.
"""

import re
from pathlib import Path
from typing import Dict, Any
from artemis_exceptions import wrap_exception
from build_system_exceptions import ProjectConfigurationError
from build_managers.cmake.models import CMakeProjectInfo


class CMakeProjectParser:
    """
    Parses CMakeLists.txt for project information.

    WHY: Need project metadata before build (name, version, languages).
    PATTERNS: Parser (regex-based extraction).
    """

    @wrap_exception(ProjectConfigurationError, "Failed to parse CMakeLists.txt")
    def parse_project_info(
        self,
        cmakelists_path: Path,
        build_dir: Path,
        project_dir: Path
    ) -> Dict[str, Any]:
        """
        Parse CMakeLists.txt for project information.

        WHY: Extracts project metadata without running CMake configuration.

        Args:
            cmakelists_path: Path to CMakeLists.txt
            build_dir: Build directory
            project_dir: Source directory

        Returns:
            Dict with project information

        Raises:
            ProjectConfigurationError: If CMakeLists.txt malformed

        Example:
            >>> parser = CMakeProjectParser()
            >>> info = parser.parse_project_info(
            ...     Path("CMakeLists.txt"),
            ...     Path("build"),
            ...     Path(".")
            ... )
            >>> info["name"]
            'MyProject'
        """
        # Read CMakeLists.txt
        with open(cmakelists_path, 'r') as f:
            content = f.read()

        # Extract components
        project_name = self._extract_project_name(content)
        version = self._extract_version(content)
        languages = self._extract_languages(content)

        # Build project info
        info = CMakeProjectInfo(
            project_name=project_name,
            version=version,
            languages=languages,
            build_dir=build_dir,
            source_dir=project_dir,
            generator="Unix Makefiles",  # Default
            build_type="Release"  # Default
        )

        return info.to_dict()

    def _extract_project_name(self, content: str) -> str:
        """
        Extract project name from CMakeLists.txt.

        WHY: Project name is required metadata.

        Args:
            content: CMakeLists.txt content

        Returns:
            Project name or "Unknown"

        Example:
            >>> parser._extract_project_name("project(MyApp VERSION 1.0)")
            'MyApp'
        """
        project_match = re.search(r"project\s*\(\s*(\w+)", content, re.IGNORECASE)
        return project_match.group(1) if project_match else "Unknown"

    def _extract_version(self, content: str) -> str:
        """
        Extract version from CMakeLists.txt.

        WHY: Version information for build artifacts.

        Args:
            content: CMakeLists.txt content

        Returns:
            Version string or "0.0.0"

        Example:
            >>> parser._extract_version("project(MyApp VERSION 1.2.3)")
            '1.2.3'
        """
        version_match = re.search(r"VERSION\s+([\d.]+)", content, re.IGNORECASE)
        return version_match.group(1) if version_match else "0.0.0"

    def _extract_languages(self, content: str) -> list:
        """
        Extract languages from CMakeLists.txt.

        WHY: Languages determine which compilers are needed.

        Args:
            content: CMakeLists.txt content

        Returns:
            List of languages (default: ["C", "CXX"])

        Example:
            >>> parser._extract_languages("project(MyApp LANGUAGES C CXX)")
            ['C', 'CXX']
        """
        lang_match = re.search(r"LANGUAGES\s+([\w\s]+)", content, re.IGNORECASE)
        return lang_match.group(1).split() if lang_match else ["C", "CXX"]
