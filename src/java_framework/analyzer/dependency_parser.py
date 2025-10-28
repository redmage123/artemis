#!/usr/bin/env python3
"""
WHY: Parses Java build files to extract dependencies
RESPONSIBILITY: Extracts dependencies from Maven POM and Gradle build files
PATTERNS: Strategy Pattern (parser dispatch), Guard Clauses, Functional Programming
"""

import logging
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Callable, Dict, Optional


class DependencyParser:
    """
    WHY: Extracts dependencies from Java build files
    RESPONSIBILITY: Parses Maven and Gradle build files to extract dependency information
    PATTERNS: Strategy Pattern with dispatch table for different build systems
    """

    def __init__(
        self,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize dependency parser

        Args:
            logger: Optional logger for error reporting
        """
        self.logger = logger or logging.getLogger(__name__)

        # Strategy Pattern: dispatch table for build system parsers
        self._parser_dispatch: Dict[str, Callable[[Path], Dict[str, str]]] = {
            "Maven": self._parse_maven_dependencies,
            "Gradle": self._parse_gradle_dependencies,
        }

    def parse(self, build_system: str, build_file: Path) -> Dict[str, str]:
        """
        WHY: Parses dependencies from build file using dispatch table
        RESPONSIBILITY: Routes to appropriate parser based on build system

        Args:
            build_system: Build system name (Maven or Gradle)
            build_file: Path to build file

        Returns:
            Dictionary mapping dependency keys to versions
        """
        # Guard clause: check for valid build system
        parser = self._parser_dispatch.get(build_system)
        if not parser:
            return {}

        return parser(build_file)

    def _parse_maven_dependencies(self, pom_path: Path) -> Dict[str, str]:
        """
        WHY: Extracts dependencies from Maven pom.xml
        RESPONSIBILITY: Parses XML and returns dependency map

        Args:
            pom_path: Path to pom.xml file

        Returns:
            Dictionary of dependencies (group:artifact -> version)
        """
        # Guard clause: check file exists
        if not pom_path.exists():
            return {}

        try:
            tree = ET.parse(pom_path)
            root = tree.getroot()
            ns = {"mvn": "http://maven.apache.org/POM/4.0.0"}

            dependencies = {}

            for dep in root.findall(".//mvn:dependency", ns):
                group_id = dep.find("mvn:groupId", ns)
                artifact_id = dep.find("mvn:artifactId", ns)
                version = dep.find("mvn:version", ns)

                # Guard clause: skip if missing required elements
                if group_id is None or artifact_id is None:
                    continue

                key = f"{group_id.text}:{artifact_id.text}"
                dependencies[key] = version.text if version is not None else "unknown"

            return dependencies

        except Exception as e:
            self.logger.error(f"Failed to parse Maven dependencies: {e}")
            return {}

    def _parse_gradle_dependencies(self, gradle_path: Path) -> Dict[str, str]:
        """
        WHY: Extracts dependencies from Gradle build file
        RESPONSIBILITY: Parses Gradle syntax and returns dependency map

        Args:
            gradle_path: Path to build.gradle or build.gradle.kts

        Returns:
            Dictionary of dependencies (group:artifact -> version)
        """
        # Guard clause: check file exists
        if not gradle_path.exists():
            return {}

        try:
            content = gradle_path.read_text()
            dependencies = {}

            # Match: implementation 'group:artifact:version'
            pattern = r"(?:implementation|api|compile|testImplementation)\s+['\"]([^:'\"]+):([^:'\"]+):([^'\"]+)['\"]"

            for match in re.finditer(pattern, content):
                group = match.group(1)
                artifact = match.group(2)
                version = match.group(3)
                key = f"{group}:{artifact}"
                dependencies[key] = version

            return dependencies

        except Exception as e:
            self.logger.error(f"Failed to parse Gradle dependencies: {e}")
            return {}
