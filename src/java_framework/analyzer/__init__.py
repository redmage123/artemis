#!/usr/bin/env python3
"""
WHY: Clean public API for Java framework analyzer package
RESPONSIBILITY: Exports main analyzer and component classes for modular usage
PATTERNS: Package exports for encapsulation and clean API surface

This package provides a modular Java framework analysis system broken down into:
- BuildSystemDetector: Detects Maven/Gradle build systems
- DependencyParser: Parses dependencies from build files
- TechnologyDetector: Detects web servers, databases, APIs, security, etc.
- ArchitectureAnalyzer: Detects microservices vs monolithic architecture
- VersionExtractor: Extracts version information for frameworks and servers
- JavaWebFrameworkAnalyzer: Main facade orchestrating all analysis

Usage:
    # Standard usage (facade pattern)
    from java_framework.analyzer import JavaWebFrameworkAnalyzer
    analyzer = JavaWebFrameworkAnalyzer(project_dir="/path/to/project")
    analysis = analyzer.analyze()

    # Modular usage (individual components)
    from java_framework.analyzer import BuildSystemDetector, DependencyParser
    build_detector = BuildSystemDetector(project_dir)
    build_system = build_detector.detect()
"""

from java_framework.analyzer.architecture_analyzer import ArchitectureAnalyzer
from java_framework.analyzer.build_system_detector import BuildSystemDetector
from java_framework.analyzer.dependency_parser import DependencyParser
from java_framework.analyzer.main_analyzer import JavaWebFrameworkAnalyzer
from java_framework.analyzer.technology_detector import TechnologyDetector
from java_framework.analyzer.version_extractor import VersionExtractor

__all__ = [
    "JavaWebFrameworkAnalyzer",
    "BuildSystemDetector",
    "DependencyParser",
    "TechnologyDetector",
    "ArchitectureAnalyzer",
    "VersionExtractor",
]
