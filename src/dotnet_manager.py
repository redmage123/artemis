#!/usr/bin/env python3
"""
.NET Build Manager - Backward Compatibility Wrapper

WHY: Maintain backward compatibility with existing code using old import paths.
RESPONSIBILITY: Re-export all components from modularized package.
PATTERNS: Facade pattern, Adapter pattern.

DEPRECATED: This module exists only for backward compatibility.
New code should import from: managers.build_managers.dotnet

Migration guide:
    OLD: from dotnet_manager import DotNetManager
    NEW: from managers.build_managers.dotnet import DotNetManager

    OLD: from dotnet_manager import BuildConfiguration, TargetFramework
    NEW: from managers.build_managers.dotnet import BuildConfiguration, TargetFramework
"""

import warnings

# Issue deprecation warning
warnings.warn(
    "dotnet_manager module is deprecated. "
    "Use 'from managers.build_managers.dotnet import DotNetManager' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export all public components from modularized package
from managers.build_managers.dotnet import (
    # Main manager class
    DotNetManager,

    # Models and enums
    BuildConfiguration,
    TargetFramework,
    ProjectType,
    DotNetProjectInfo,

    # Components (for advanced usage)
    ProjectParser,
    NuGetManager,
    BuildOperations,
    FrameworkDetector,

    # CLI
    DotNetCLI,
)

__all__ = [
    # Main class
    "DotNetManager",

    # Models and enums
    "BuildConfiguration",
    "TargetFramework",
    "ProjectType",
    "DotNetProjectInfo",

    # Components
    "ProjectParser",
    "NuGetManager",
    "BuildOperations",
    "FrameworkDetector",

    # CLI
    "DotNetCLI",
]

# CLI entry point for backward compatibility
if __name__ == "__main__":
    cli = DotNetCLI()
    cli.run()
