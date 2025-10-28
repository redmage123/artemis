#!/usr/bin/env python3
"""
WHY: Java framework detection package
RESPONSIBILITY: Provides modular framework detection for Java web applications
PATTERNS: Package exports for clean API surface

This package provides a comprehensive framework detection system for Java web
applications, supporting Spring Boot, Micronaut, Quarkus, Jakarta EE, and many others.

Usage:
    from java_framework import JavaWebFrameworkAnalyzer
    from java_framework.models import JavaWebFramework

    analyzer = JavaWebFrameworkAnalyzer(project_dir="/path/to/project")
    analysis = analyzer.analyze()

    print(f"Framework: {analysis.primary_framework.value}")
    print(f"Version: {analysis.framework_version}")
"""

from java_framework.analyzer import JavaWebFrameworkAnalyzer
from java_framework.models import (
    DetectionResult,
    JavaWebFramework,
    JavaWebFrameworkAnalysis,
    TemplateEngine,
    WebServer,
)

__all__ = [
    "JavaWebFrameworkAnalyzer",
    "JavaWebFramework",
    "JavaWebFrameworkAnalysis",
    "WebServer",
    "TemplateEngine",
    "DetectionResult",
]

__version__ = "2.0.0"
