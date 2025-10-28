#!/usr/bin/env python3
"""
WHY: Provide clean public API for spring_boot package
RESPONSIBILITY: Export public classes and maintain backward compatibility
PATTERNS: Facade Pattern, Explicit Exports

Spring Boot Analyzer Package
=============================

A modular analyzer for Spring Boot applications that provides:
- Annotation scanning for Spring Framework annotations
- REST endpoint detection and analysis
- Dependency analysis from Maven/Gradle build files
- Configuration parsing from properties and YAML files
- Architecture pattern detection
- Security, caching, and feature detection

Usage:
    from spring_boot import SpringBootAnalyzer

    analyzer = SpringBootAnalyzer(project_dir="/path/to/spring-boot-app")
    analysis = analyzer.analyze()

    print(f"Main Application: {analysis.main_application_class}")
    print(f"REST Endpoints: {len(analysis.rest_endpoints)}")
"""

# Core analyzer
from .analyzer_core import SpringBootAnalyzer

# Data models
from .models import (
    RestEndpoint,
    DatabaseConfig,
    SecurityConfig,
    SpringBootAnalysis
)

# Specialized scanners (optional advanced usage)
from .annotation_scanner import AnnotationScanner, RestEndpointScanner
from .dependency_analyzer import (
    DependencyAnalyzer,
    DatabaseDependencyDetector,
    CacheDependencyDetector,
    SecurityDependencyDetector,
    FeatureDependencyDetector
)
from .config_parser import (
    ConfigParser,
    DatabaseConfigExtractor,
    ActuatorConfigExtractor,
    SecurityConfigExtractor
)
from .architecture_detector import (
    PackageExtractor,
    LayeredArchitectureDetector,
    RestArchitectureDetector,
    TestArchitectureDetector,
    FeatureDetector
)

# Public API
__all__ = [
    # Main analyzer (primary interface)
    'SpringBootAnalyzer',

    # Data models
    'RestEndpoint',
    'DatabaseConfig',
    'SecurityConfig',
    'SpringBootAnalysis',

    # Advanced components (optional)
    'AnnotationScanner',
    'RestEndpointScanner',
    'DependencyAnalyzer',
    'DatabaseDependencyDetector',
    'CacheDependencyDetector',
    'SecurityDependencyDetector',
    'FeatureDependencyDetector',
    'ConfigParser',
    'DatabaseConfigExtractor',
    'ActuatorConfigExtractor',
    'SecurityConfigExtractor',
    'PackageExtractor',
    'LayeredArchitectureDetector',
    'RestArchitectureDetector',
    'TestArchitectureDetector',
    'FeatureDetector',
]

__version__ = '2.0.0'
__author__ = 'Artemis Development Team'
