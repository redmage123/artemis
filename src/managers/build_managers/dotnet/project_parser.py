#!/usr/bin/env python3
"""
.NET Project File Parser

WHY: Dedicated module for parsing .csproj, .fsproj, .vbproj, and .sln files.
RESPONSIBILITY: Extract project metadata, dependencies, and configuration from XML/text files.
PATTERNS: Single Responsibility Principle, Guard clauses for validation.

Part of: managers.build_managers.dotnet
Dependencies: models
"""

import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional

from managers.build_managers.dotnet.models import DotNetProjectInfo


class ProjectParser:
    """
    Parser for .NET project and solution files.

    WHY: Centralize all file parsing logic to maintain consistency.
    RESPONSIBILITY: Parse XML project files and text-based solution files.
    PATTERNS: Single Responsibility Principle.
    """

    @staticmethod
    def parse_solution(solution_path: Path) -> DotNetProjectInfo:
        """
        Parse .sln (solution) file.

        WHY: Extract project references from solution file.
        RESPONSIBILITY: Parse text-based solution format.

        Args:
            solution_path: Path to .sln file

        Returns:
            DotNetProjectInfo with solution metadata

        Guards:
            - File must exist
            - File must be readable
        """
        if not solution_path.exists():
            raise FileNotFoundError(f"Solution file not found: {solution_path}")

        solution_projects = []

        with open(solution_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()

        # Parse project lines: Project("{GUID}") = "ProjectName", "Path/To/Project.csproj", "{GUID}"
        project_pattern = r'Project\("[^"]+"\)\s*=\s*"([^"]+)",\s*"([^"]+)"'

        for match in re.finditer(project_pattern, content):
            project_name = match.group(1)
            project_path = match.group(2)

            if project_path.endswith(('.csproj', '.fsproj', '.vbproj')):
                solution_projects.append(project_path)

        return DotNetProjectInfo(
            project_name=solution_path.stem,
            target_framework="",  # Solution doesn't have target framework
            is_solution=True,
            solution_projects=solution_projects
        )

    @staticmethod
    def parse_project(project_path: Path) -> DotNetProjectInfo:
        """
        Parse .csproj/.fsproj/.vbproj (project) file.

        WHY: Extract project configuration from XML format.
        RESPONSIBILITY: Parse MSBuild project file structure.

        Args:
            project_path: Path to project file

        Returns:
            DotNetProjectInfo with project metadata

        Guards:
            - File must exist
            - File must be valid XML
        """
        if not project_path.exists():
            raise FileNotFoundError(f"Project file not found: {project_path}")

        tree = ET.parse(project_path)
        root = tree.getroot()

        # Get SDK attribute
        sdk = root.get('Sdk', 'Microsoft.NET.Sdk')

        # Extract elements using specialized methods
        target_framework = ProjectParser._extract_target_framework(root)
        output_type = ProjectParser._extract_output_type(root)
        package_references = ProjectParser._extract_package_references(root)
        project_references = ProjectParser._extract_project_references(root)

        return DotNetProjectInfo(
            project_name=project_path.stem,
            target_framework=target_framework,
            sdk=sdk,
            output_type=output_type,
            package_references=package_references,
            project_references=project_references,
            is_solution=False
        )

    @staticmethod
    def _extract_target_framework(root: ET.Element) -> str:
        """
        Extract TargetFramework from PropertyGroup.

        WHY: Determine which .NET runtime version is targeted.

        Args:
            root: XML root element

        Returns:
            Target framework moniker (e.g., "net8.0")
        """
        for prop_group in root.findall('.//PropertyGroup'):
            tf_elem = prop_group.find('TargetFramework')

            if tf_elem is None:
                continue

            return tf_elem.text or ""

        return ""

    @staticmethod
    def _extract_output_type(root: ET.Element) -> Optional[str]:
        """
        Extract OutputType from PropertyGroup.

        WHY: Determine if project produces Exe, Library, etc.

        Args:
            root: XML root element

        Returns:
            Output type (Exe, Library, WinExe, etc.) or None
        """
        for prop_group in root.findall('.//PropertyGroup'):
            ot_elem = prop_group.find('OutputType')

            if ot_elem is None:
                continue

            return ot_elem.text

        return None

    @staticmethod
    def _extract_package_references(root: ET.Element) -> Dict[str, str]:
        """
        Extract PackageReference elements from ItemGroups.

        WHY: Identify NuGet package dependencies.

        Args:
            root: XML root element

        Returns:
            Dictionary mapping package name to version
        """
        package_references = {}

        for item_group in root.findall('.//ItemGroup'):
            for package_ref in item_group.findall('PackageReference'):
                package_name = package_ref.get('Include')

                if not package_name:
                    continue

                version = package_ref.get('Version', '')
                package_references[package_name] = version

        return package_references

    @staticmethod
    def _extract_project_references(root: ET.Element) -> List[str]:
        """
        Extract ProjectReference elements from ItemGroups.

        WHY: Identify project-to-project dependencies.

        Args:
            root: XML root element

        Returns:
            List of project reference paths
        """
        project_references = []

        for item_group in root.findall('.//ItemGroup'):
            for proj_ref in item_group.findall('ProjectReference'):
                proj_path = proj_ref.get('Include')

                if not proj_path:
                    continue

                project_references.append(proj_path)

        return project_references


__all__ = ["ProjectParser"]
