#!/usr/bin/env python3
"""
Java Ecosystem Integration Package

WHY: Provides modular, maintainable Java ecosystem integration for Artemis,
     separating concerns across focused modules while maintaining clean API.

RESPONSIBILITY:
    - Export public API for Java ecosystem integration
    - Provide backward compatibility with monolithic module
    - Support both Maven and Gradle build systems
    - Enable comprehensive Java project analysis

PATTERNS:
    - Package initialization pattern - centralized exports
    - Facade pattern - simplified public API
    - Backward compatibility - maintains existing interface

PUBLIC API:
    - JavaEcosystemManager: Main entry point for Java project management
    - JavaEcosystemAnalysis: Comprehensive analysis results
    - MavenIntegration: Maven-specific integration
    - GradleIntegration: Gradle-specific integration
    - DependencyResolver: Unified dependency management
    - BuildCoordinator: Coordinated build/test execution

USAGE:
    from java_ecosystem import JavaEcosystemManager

    manager = JavaEcosystemManager(project_dir="/path/to/java-project")
    analysis = manager.analyze_project()
    build_result = manager.build()
    test_result = manager.run_tests()
"""

from java_ecosystem.models import JavaEcosystemAnalysis
from java_ecosystem.maven_integration import MavenIntegration
from java_ecosystem.gradle_integration import GradleIntegration
from java_ecosystem.dependency_resolver import DependencyResolver
from java_ecosystem.build_coordinator import BuildCoordinator
from java_ecosystem.ecosystem_core import JavaEcosystemManager

__version__ = "1.0.0"

__all__ = [
    'JavaEcosystemManager',
    'JavaEcosystemAnalysis',
    'MavenIntegration',
    'GradleIntegration',
    'DependencyResolver',
    'BuildCoordinator',
]
