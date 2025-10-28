#!/usr/bin/env python3
"""
WHY: Analyzes Java project architecture patterns
RESPONSIBILITY: Determines if project is microservices or monolithic architecture
PATTERNS: Strategy Pattern, Guard Clauses, Functional Programming
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Tuple


class ArchitectureAnalyzer:
    """
    WHY: Identifies architectural patterns in Java projects
    RESPONSIBILITY: Detects microservices vs monolithic patterns and multi-module structure
    PATTERNS: Strategy Pattern for extensible architecture detection
    """

    def __init__(self, project_dir: Path):
        """
        Initialize architecture analyzer

        Args:
            project_dir: Java project root directory
        """
        self.project_dir = project_dir
        self.pom_path = self.project_dir / "pom.xml"

    def analyze(self) -> Tuple[bool, bool, List[str]]:
        """
        WHY: Determines project architecture
        RESPONSIBILITY: Detects microservices vs monolith based on structure

        Returns:
            Tuple of (is_microservices, is_monolith, modules)
        """
        # Extract Maven modules
        modules = self._extract_maven_modules()

        # Check for microservices indicators
        is_microservices = (
            len(modules) > 1 or
            (self.project_dir / "docker-compose.yml").exists() or
            (self.project_dir / "kubernetes").exists() or
            bool(list(self.project_dir.glob("**/Dockerfile")))
        )

        is_monolith = not is_microservices

        return is_microservices, is_monolith, modules

    def _extract_maven_modules(self) -> List[str]:
        """
        WHY: Extracts module list from Maven pom.xml
        RESPONSIBILITY: Parses pom.xml for multi-module configuration

        Returns:
            List of module names
        """
        # Guard clause: check file exists
        if not self.pom_path.exists():
            return []

        try:
            tree = ET.parse(self.pom_path)
            root = tree.getroot()
            ns = {"mvn": "http://maven.apache.org/POM/4.0.0"}

            modules = []
            for module in root.findall(".//mvn:modules/mvn:module", ns):
                if module.text:
                    modules.append(module.text)
            return modules
        except Exception:
            return []
