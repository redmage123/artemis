#!/usr/bin/env python3
"""
Maven Build System Manager Package

WHY: Modular Maven integration with clean separation of concerns.
RESPONSIBILITY: Export public API for Maven operations.
PATTERNS: Facade pattern (MavenManager), Module pattern.

Public API:
- MavenManager: Primary facade for all Maven operations
- MavenPhase, MavenScope: Type-safe enumerations
- MavenProjectInfo, MavenDependency, MavenBuildResult: Data models
- PomParser, DependencyManager, BuildExecutor: Specialized components

Architecture:
    maven_manager.py      -> Orchestrator (Facade)
    maven_enums.py        -> Enumerations (Phase, Scope)
    maven_models.py       -> Data models (DTOs)
    pom_parser.py         -> POM.xml parsing
    dependency_manager.py -> Dependency operations
    build_executor.py     -> Build lifecycle execution
    maven_detector.py     -> Installation detection
    maven_cli.py          -> Command-line interface

Dependencies: None (self-contained package)
"""

# Primary API - Most users only need MavenManager
from .maven_manager import MavenManager

# Enumerations for type-safe API
from .maven_enums import MavenPhase, MavenScope

# Data models for type hints and returns
from .maven_models import (
    MavenProjectInfo,
    MavenDependency,
    MavenPlugin,
    MavenBuildResult
)

# Specialized components (advanced usage)
from .pom_parser import PomParser
from .dependency_manager import DependencyManager
from .build_executor import BuildExecutor
from .maven_detector import MavenDetector

__all__ = [
    # Primary API
    "MavenManager",

    # Enumerations
    "MavenPhase",
    "MavenScope",

    # Data Models
    "MavenProjectInfo",
    "MavenDependency",
    "MavenPlugin",
    "MavenBuildResult",

    # Specialized Components
    "PomParser",
    "DependencyManager",
    "BuildExecutor",
    "MavenDetector",
]
