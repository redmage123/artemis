#!/usr/bin/env python3
"""
Module: POM Parser

WHY: Specialized XML parsing for Maven Project Object Model (pom.xml) files.
RESPONSIBILITY: Extract project information, dependencies, plugins, and properties from POM.
PATTERNS: Parser pattern, Facade pattern (simplifies XML parsing complexity).

Dependencies: maven_models (for data structures)
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional
import logging

from .maven_models import (
    MavenProjectInfo,
    MavenDependency,
    MavenPlugin
)


class PomParser:
    """
    Maven POM.xml parser.

    WHY: Parsing Maven's XML format requires namespace handling and understanding
         of POM inheritance, property interpolation, and multi-module structure.
    RESPONSIBILITY: Parse pom.xml and extract all relevant project metadata.

    PATTERNS:
    - Parser pattern: Specialized parsing logic for Maven POM format
    - Facade pattern: Simplifies complex XML parsing behind clean interface
    - Strategy pattern: Different extraction strategies for various POM elements

    Maven XML Namespace: http://maven.apache.org/POM/4.0.0
    """

    # Maven XML namespace
    MAVEN_NS = {"mvn": "http://maven.apache.org/POM/4.0.0"}

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize POM parser.

        Args:
            logger: Optional logger for diagnostics
        """
        self.logger = logger or logging.getLogger(__name__)

    def parse(self, pom_path: Path) -> MavenProjectInfo:
        """
        Parse pom.xml and extract comprehensive project information.

        WHY: Central entry point for POM parsing.
        RESPONSIBILITY: Orchestrate all parsing sub-tasks.

        Args:
            pom_path: Path to pom.xml file

        Returns:
            MavenProjectInfo with all project details

        Raises:
            FileNotFoundError: If pom.xml doesn't exist
            ET.ParseError: If pom.xml is malformed
        """
        if not pom_path.exists():
            raise FileNotFoundError(f"No pom.xml found at {pom_path}")

        tree = ET.parse(pom_path)
        root = tree.getroot()

        # Register namespace for cleaner XML generation
        ET.register_namespace('', 'http://maven.apache.org/POM/4.0.0')

        # Parse all sections using dispatch pattern
        basic_info = self._parse_basic_info(root)
        parent_info = self._parse_parent(root)
        modules = self._parse_modules(root)
        properties = self._parse_properties(root)
        dependencies = self._parse_dependencies(root)
        plugins = self._parse_plugins(root)

        return MavenProjectInfo(
            group_id=basic_info["group_id"],
            artifact_id=basic_info["artifact_id"],
            version=basic_info["version"],
            name=basic_info["name"],
            packaging=basic_info["packaging"],
            description=basic_info["description"],
            parent=parent_info,
            modules=modules,
            dependencies=dependencies,
            plugins=plugins,
            properties=properties,
            is_multi_module=len(modules) > 0
        )

    def _parse_basic_info(self, root: ET.Element) -> dict:
        """
        Parse basic project information.

        WHY: Guard clause - extract fundamental coordinates first.
        RESPONSIBILITY: Extract groupId, artifactId, version, name, packaging, description.

        Returns:
            Dictionary with basic project fields
        """
        return {
            "group_id": self._get_text(root, ".//mvn:groupId"),
            "artifact_id": self._get_text(root, ".//mvn:artifactId"),
            "version": self._get_text(root, ".//mvn:version"),
            "name": self._get_text(root, ".//mvn:name", self._get_text(root, ".//mvn:artifactId")),
            "packaging": self._get_text(root, ".//mvn:packaging", "jar"),
            "description": self._get_text(root, ".//mvn:description")
        }

    def _parse_parent(self, root: ET.Element) -> Optional[dict]:
        """
        Parse parent POM information.

        WHY: Maven supports POM inheritance - child POMs inherit from parent.
        RESPONSIBILITY: Extract parent coordinates if present.

        Returns:
            Dictionary with parent coordinates or None
        """
        parent_elem = root.find(".//mvn:parent", self.MAVEN_NS)
        if parent_elem is None:
            return None

        return {
            "groupId": self._get_text(parent_elem, ".//mvn:groupId"),
            "artifactId": self._get_text(parent_elem, ".//mvn:artifactId"),
            "version": self._get_text(parent_elem, ".//mvn:version")
        }

    def _parse_modules(self, root: ET.Element) -> list:
        """
        Parse module list for multi-module projects.

        WHY: Maven supports aggregator POMs that build multiple modules together.
        RESPONSIBILITY: Extract module directory names.

        Returns:
            List of module names (directory paths relative to parent)
        """
        modules = []
        for module in root.findall(".//mvn:modules/mvn:module", self.MAVEN_NS):
            if module.text:
                modules.append(module.text.strip())
        return modules

    def _parse_properties(self, root: ET.Element) -> dict:
        """
        Parse Maven properties.

        WHY: Maven uses ${property.name} substitution throughout POM.
        RESPONSIBILITY: Extract all custom properties defined in <properties>.

        Common properties:
        - maven.compiler.source, maven.compiler.target: Java version
        - project.build.sourceEncoding: File encoding (UTF-8)
        - Custom version properties for dependency management

        Returns:
            Dictionary of property name to value
        """
        properties = {}
        props_elem = root.find(".//mvn:properties", self.MAVEN_NS)

        if props_elem is None:
            return properties

        for prop in props_elem:
            # Remove namespace from tag name
            tag = prop.tag.replace("{http://maven.apache.org/POM/4.0.0}", "")
            properties[tag] = prop.text or ""

        return properties

    def _parse_dependencies(self, root: ET.Element) -> list:
        """
        Parse project dependencies.

        WHY: Dependencies are core to Maven's dependency management.
        RESPONSIBILITY: Extract all <dependency> elements with full coordinates.

        Returns:
            List of MavenDependency objects
        """
        dependencies = []

        for dep in root.findall(".//mvn:dependencies/mvn:dependency", self.MAVEN_NS):
            dependencies.append(MavenDependency(
                group_id=self._get_text(dep, ".//mvn:groupId", ""),
                artifact_id=self._get_text(dep, ".//mvn:artifactId", ""),
                version=self._get_text(dep, ".//mvn:version", ""),
                scope=self._get_text(dep, ".//mvn:scope", "compile"),
                type=self._get_text(dep, ".//mvn:type", "jar"),
                classifier=self._get_text(dep, ".//mvn:classifier"),
                optional=self._get_text(dep, ".//mvn:optional", "false") == "true"
            ))

        return dependencies

    def _parse_plugins(self, root: ET.Element) -> list:
        """
        Parse build plugins.

        WHY: Plugins execute goals during build lifecycle (compile, test, package).
        RESPONSIBILITY: Extract plugin coordinates from <build><plugins>.

        Common plugins:
        - maven-compiler-plugin: Compiles Java source
        - maven-surefire-plugin: Runs unit tests
        - maven-jar-plugin: Creates JAR file

        Returns:
            List of MavenPlugin objects
        """
        plugins = []

        for plugin in root.findall(".//mvn:build/mvn:plugins/mvn:plugin", self.MAVEN_NS):
            plugins.append(MavenPlugin(
                group_id=self._get_text(plugin, ".//mvn:groupId", "org.apache.maven.plugins"),
                artifact_id=self._get_text(plugin, ".//mvn:artifactId", ""),
                version=self._get_text(plugin, ".//mvn:version", "")
            ))

        return plugins

    def _get_text(
        self,
        element: ET.Element,
        xpath: str,
        default: str = ""
    ) -> str:
        """
        Extract text from XML element with namespace support.

        WHY: Guard clause - handles missing elements and empty text gracefully.
        RESPONSIBILITY: Safe text extraction with default fallback.

        Args:
            element: XML element to search within
            xpath: XPath expression (with mvn: namespace prefix)
            default: Default value if element not found or empty

        Returns:
            Element text or default value
        """
        found = element.find(xpath, self.MAVEN_NS)
        if found is None:
            return default

        if found.text is None:
            return default

        return found.text.strip()
