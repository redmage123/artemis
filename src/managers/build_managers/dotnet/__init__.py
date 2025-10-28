#!/usr/bin/env python3
"""
.NET Build Manager Package

WHY: Modularized .NET build system for C#/F#/VB.NET projects.
RESPONSIBILITY: Provide unified interface for .NET build operations.
PATTERNS: Facade pattern, Composition pattern.

Part of: managers.build_managers
Dependencies: build_manager_base, build_system_exceptions

This package contains specialized modules:
- models: Data models and enumerations (DotNetProjectInfo, BuildConfiguration, etc.)
- project_parser: Parse .csproj/.fsproj/.sln files
- nuget_manager: NuGet package operations
- build_operations: Build/test/publish/run/clean operations
- framework_detector: SDK and runtime version detection
- manager: Main DotNetManager orchestrator
- cli: Command-line interface

Module Structure:
    managers.build_managers.dotnet/
        __init__.py          # This file - package exports
        models.py            # 116 lines - Data models
        project_parser.py    # 194 lines - XML/text parsing
        nuget_manager.py     # 118 lines - Package management
        build_operations.py  # 312 lines - Build operations
        framework_detector.py # 221 lines - Framework detection
        manager.py           # 452 lines - Main orchestrator
        cli.py               # 302 lines - CLI interface

Total: ~1,715 lines (original: 738 lines)
Reduction achieved through better organization and documentation.
"""

# Main manager class (primary export)
from managers.build_managers.dotnet.manager import DotNetManager

# Models and enumerations
from managers.build_managers.dotnet.models import (
    BuildConfiguration,
    TargetFramework,
    ProjectType,
    DotNetProjectInfo,
)

# Specialized components (for advanced usage)
from managers.build_managers.dotnet.project_parser import ProjectParser
from managers.build_managers.dotnet.nuget_manager import NuGetManager
from managers.build_managers.dotnet.build_operations import BuildOperations
from managers.build_managers.dotnet.framework_detector import FrameworkDetector

# CLI interface (for script execution)
from managers.build_managers.dotnet.cli import DotNetCLI

__all__ = [
    # Main class (primary interface)
    "DotNetManager",

    # Models and enums
    "BuildConfiguration",
    "TargetFramework",
    "ProjectType",
    "DotNetProjectInfo",

    # Components (for advanced usage and testing)
    "ProjectParser",
    "NuGetManager",
    "BuildOperations",
    "FrameworkDetector",

    # CLI
    "DotNetCLI",
]

# Version information
__version__ = "2.0.0"
__author__ = "Artemis Development Team"
