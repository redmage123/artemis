#!/usr/bin/env python3
"""
BACKWARD COMPATIBILITY WRAPPER for maven_manager.py

WHY: Maintains backward compatibility while code migrates to modular structure.
RESPONSIBILITY: Re-export all components from new modular location.
PATTERNS: Facade pattern, Deprecation pattern.

MIGRATION PATH:
    Old: from maven_manager import MavenManager
    New: from managers.build_managers.maven import MavenManager

This wrapper allows existing code to continue working while gradually
migrating to the new modular structure.

Original file: /home/bbrelin/src/repos/artemis/src/maven_manager.py (717 lines)
Refactored to: /home/bbrelin/src/repos/artemis/src/managers/build_managers/maven/
    - maven_enums.py (72 lines)
    - maven_models.py (155 lines)
    - pom_parser.py (237 lines)
    - dependency_manager.py (172 lines)
    - build_executor.py (280 lines)
    - maven_detector.py (159 lines)
    - maven_manager.py (218 lines)
    - maven_cli.py (202 lines)
    - __init__.py (60 lines)

Total refactored: ~1,555 lines (expanded from 717 due to documentation)
Core logic: ~800 lines (100 line increase for better separation)
"""

import warnings
from pathlib import Path

# Re-export everything from new location
from managers.build_managers.maven import (
    MavenManager,
    MavenPhase,
    MavenScope,
    MavenProjectInfo,
    MavenDependency,
    MavenPlugin,
    MavenBuildResult,
    PomParser,
    DependencyManager,
    BuildExecutor,
    MavenDetector,
)

# Issue deprecation warning
warnings.warn(
    "Importing from 'maven_manager' is deprecated. "
    "Use 'from managers.build_managers.maven import MavenManager' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Export all for backward compatibility
__all__ = [
    "MavenManager",
    "MavenPhase",
    "MavenScope",
    "MavenProjectInfo",
    "MavenDependency",
    "MavenPlugin",
    "MavenBuildResult",
    "PomParser",
    "DependencyManager",
    "BuildExecutor",
    "MavenDetector",
]

# CLI support for backward compatibility
if __name__ == "__main__":
    from managers.build_managers.maven.maven_cli import main
    main()
