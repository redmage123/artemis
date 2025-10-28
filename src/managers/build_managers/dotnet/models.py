#!/usr/bin/env python3
"""
.NET Build Manager - Models and Enumerations

WHY: Centralize all data models, enums, and type definitions for .NET build system.
RESPONSIBILITY: Define project structures, configuration types, and framework versions.
PATTERNS: Value Object pattern, Enum pattern for type safety.

Part of: managers.build_managers.dotnet
Dependencies: None (pure data structures)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any


class BuildConfiguration(Enum):
    """
    Build configuration types for .NET projects.

    WHY: Type-safe enumeration of build configurations.
    """
    DEBUG = "Debug"
    RELEASE = "Release"


class TargetFramework(Enum):
    """
    Common .NET target framework monikers (TFMs).

    WHY: Standardize framework version references across the codebase.
    RESPONSIBILITY: Define supported .NET framework versions.
    """
    NET8 = "net8.0"
    NET7 = "net7.0"
    NET6 = "net6.0"
    NET_STANDARD_2_1 = "netstandard2.1"
    NET_STANDARD_2_0 = "netstandard2.0"
    NET_FRAMEWORK_4_8 = "net48"


class ProjectType(Enum):
    """
    .NET project template types.

    WHY: Identify project purpose and structure.
    RESPONSIBILITY: Define available project templates.
    """
    CONSOLE = "console"
    CLASSLIB = "classlib"
    WEB = "web"
    WEBAPI = "webapi"
    MVC = "mvc"
    BLAZOR = "blazorserver"
    WORKER = "worker"


@dataclass
class DotNetProjectInfo:
    """
    Value object representing parsed .NET project/solution information.

    WHY: Encapsulate all project metadata in a single, immutable structure.
    RESPONSIBILITY: Store and serialize project configuration details.
    PATTERNS: Value Object pattern, Data Transfer Object (DTO).

    Attributes:
        project_name: Name of the project or solution
        target_framework: Target framework moniker (e.g., "net8.0")
        project_type: Type of project (console, web, etc.)
        sdk: MSBuild SDK reference (default: Microsoft.NET.Sdk)
        output_type: Compilation output type (Exe, Library, etc.)
        package_references: NuGet packages with versions
        project_references: Referenced project paths
        is_solution: Whether this is a solution file
        solution_projects: Projects within solution (if is_solution=True)
    """
    project_name: str
    target_framework: str
    project_type: Optional[str] = None
    sdk: str = "Microsoft.NET.Sdk"
    output_type: Optional[str] = None
    package_references: Dict[str, str] = field(default_factory=dict)
    project_references: List[str] = field(default_factory=list)
    is_solution: bool = False
    solution_projects: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert project info to dictionary format.

        WHY: Enable JSON serialization and API compatibility.

        Returns:
            Dictionary representation of project information
        """
        return {
            "projectName": self.project_name,
            "targetFramework": self.target_framework,
            "projectType": self.project_type,
            "sdk": self.sdk,
            "outputType": self.output_type,
            "packageReferences": self.package_references,
            "projectReferences": self.project_references,
            "isSolution": self.is_solution,
            "solutionProjects": self.solution_projects
        }


__all__ = [
    "BuildConfiguration",
    "TargetFramework",
    "ProjectType",
    "DotNetProjectInfo",
]
