#!/usr/bin/env python3
"""
Module: Maven Dependency Manager

WHY: Specialized handling for Maven dependency operations (add, resolve, tree analysis).
RESPONSIBILITY: Manage dependencies in pom.xml and query dependency information.
PATTERNS: Manager pattern, Command pattern (dependency operations as commands).

Dependencies: maven_models, subprocess for Maven CLI commands
"""

import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional
import logging


class DependencyManager:
    """
    Maven dependency management operations.

    WHY: Separates dependency concerns from general Maven operations.
    RESPONSIBILITY:
    - Add dependencies to pom.xml
    - Query dependency tree
    - Get effective POM (resolved dependencies)

    PATTERNS:
    - Manager pattern: Encapsulates dependency-specific operations
    - Command pattern: Each operation is a discrete command
    """

    # Maven XML namespace
    MAVEN_NS = {"mvn": "http://maven.apache.org/POM/4.0.0"}

    def __init__(
        self,
        project_dir: Path,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize dependency manager.

        Args:
            project_dir: Maven project root directory
            logger: Optional logger for output
        """
        self.project_dir = project_dir
        self.pom_path = project_dir / "pom.xml"
        self.logger = logger or logging.getLogger(__name__)

    def add_dependency(
        self,
        group_id: str,
        artifact_id: str,
        version: str,
        scope: str = "compile"
    ) -> bool:
        """
        Add dependency to pom.xml.

        WHY: Programmatic dependency addition without manual XML editing.
        RESPONSIBILITY: Insert new <dependency> element with proper namespace.

        Args:
            group_id: Dependency group ID (e.g., org.springframework.boot)
            artifact_id: Dependency artifact ID (e.g., spring-boot-starter-web)
            version: Dependency version (e.g., 3.2.0)
            scope: Dependency scope (compile/test/runtime/provided)

        Returns:
            True if added successfully, False on error
        """
        if not self.pom_path.exists():
            self.logger.error(f"pom.xml not found at {self.pom_path}")
            return False

        try:
            tree = ET.parse(self.pom_path)
            root = tree.getroot()

            # Find or create dependencies section
            deps = self._get_or_create_dependencies_section(root)

            # Create new dependency element
            self._create_dependency_element(deps, group_id, artifact_id, version, scope)

            # Write back to file
            tree.write(self.pom_path, encoding="UTF-8", xml_declaration=True)

            self.logger.info(f"Added dependency: {group_id}:{artifact_id}:{version}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to add dependency: {e}")
            return False

    def _get_or_create_dependencies_section(self, root: ET.Element) -> ET.Element:
        """
        Find existing <dependencies> or create new one.

        WHY: Guard clause - ensure dependencies section exists before adding.
        RESPONSIBILITY: Return dependencies element, creating if necessary.

        Args:
            root: POM root element

        Returns:
            Dependencies element
        """
        deps = root.find(".//mvn:dependencies", self.MAVEN_NS)
        if deps is not None:
            return deps

        # Create new dependencies section with proper namespace
        return ET.SubElement(root, "{http://maven.apache.org/POM/4.0.0}dependencies")

    def _create_dependency_element(
        self,
        deps: ET.Element,
        group_id: str,
        artifact_id: str,
        version: str,
        scope: str
    ) -> None:
        """
        Create dependency XML element.

        WHY: Extracted to reduce complexity of add_dependency.
        RESPONSIBILITY: Build properly namespaced dependency XML structure.

        Args:
            deps: Parent dependencies element
            group_id: Dependency group ID
            artifact_id: Dependency artifact ID
            version: Dependency version
            scope: Dependency scope
        """
        # Maven namespace for all elements
        ns = "{http://maven.apache.org/POM/4.0.0}"

        dep = ET.SubElement(deps, f"{ns}dependency")

        gid = ET.SubElement(dep, f"{ns}groupId")
        gid.text = group_id

        aid = ET.SubElement(dep, f"{ns}artifactId")
        aid.text = artifact_id

        ver = ET.SubElement(dep, f"{ns}version")
        ver.text = version

        # Only add scope if not default (compile)
        if scope != "compile":
            scp = ET.SubElement(dep, f"{ns}scope")
            scp.text = scope

    def get_dependency_tree(self, timeout: int = 60) -> str:
        """
        Get Maven dependency tree.

        WHY: Visualize transitive dependencies and detect conflicts.
        RESPONSIBILITY: Execute 'mvn dependency:tree' and return output.

        The dependency tree shows:
        - Direct dependencies
        - Transitive dependencies (pulled in by direct dependencies)
        - Version conflicts and which version Maven selected
        - Dependency scopes

        Args:
            timeout: Command timeout in seconds

        Returns:
            Dependency tree output or empty string on error
        """
        try:
            result = subprocess.run(
                ["mvn", "dependency:tree"],
                cwd=str(self.project_dir),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.stdout

        except subprocess.TimeoutExpired:
            self.logger.error(f"Dependency tree command timed out after {timeout}s")
            return ""
        except Exception as e:
            self.logger.error(f"Failed to get dependency tree: {e}")
            return ""

    def get_effective_pom(self, timeout: int = 60) -> str:
        """
        Get effective POM with all inheritance and interpolation resolved.

        WHY: Maven POMs use inheritance and property substitution. The effective POM
             shows the final, fully-resolved configuration after all processing.
        RESPONSIBILITY: Execute 'mvn help:effective-pom' and return output.

        Effective POM includes:
        - Parent POM inheritance applied
        - Properties interpolated (${property.name} replaced with values)
        - Default values filled in
        - Dependency management applied

        Args:
            timeout: Command timeout in seconds

        Returns:
            Effective POM XML or empty string on error
        """
        try:
            result = subprocess.run(
                ["mvn", "help:effective-pom"],
                cwd=str(self.project_dir),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.stdout

        except subprocess.TimeoutExpired:
            self.logger.error(f"Effective POM command timed out after {timeout}s")
            return ""
        except Exception as e:
            self.logger.error(f"Failed to get effective POM: {e}")
            return ""
