#!/usr/bin/env python3
"""
WHY: Orchestrate Spring Boot project analysis using specialized modules
RESPONSIBILITY: Coordinate analysis components and produce comprehensive results
PATTERNS: Facade Pattern, Strategy Pattern, Dependency Injection, Guard Clauses

This module provides the main analyzer orchestration:
- SpringBootAnalyzer: Main facade for analysis
- Coordinates annotation scanning, dependency analysis, config parsing
- Produces comprehensive SpringBootAnalysis results
"""

from pathlib import Path
from typing import Optional
import logging

from .models import SpringBootAnalysis, SecurityConfig
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
from .architecture_detector import PackageExtractor


class SpringBootAnalyzer:
    """
    Facade for comprehensive Spring Boot project analysis.

    Coordinates specialized analyzers to produce complete
    analysis results with minimal coupling.
    """

    def __init__(
        self,
        project_dir: Optional[Path] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize Spring Boot analyzer.

        Args:
            project_dir: Spring Boot project root directory
            logger: Optional logger for diagnostic messages
        """
        self.project_dir = Path(project_dir) if project_dir else Path.cwd()
        self.logger = logger or logging.getLogger(__name__)

        # Standard Spring Boot paths
        self.src_main = self.project_dir / "src" / "main" / "java"
        self.src_test = self.project_dir / "src" / "test" / "java"
        self.resources = self.project_dir / "src" / "main" / "resources"

        # Initialize specialized analyzers
        self._init_analyzers()

    def _init_analyzers(self) -> None:
        """Initialize all specialized analyzer components."""
        # Annotation scanning
        self.annotation_scanner = AnnotationScanner(self.logger)
        self.rest_scanner = RestEndpointScanner(self.logger)

        # Dependency analysis
        self.dependency_analyzer = DependencyAnalyzer(self.project_dir, self.logger)
        self.db_dep_detector = DatabaseDependencyDetector(self.dependency_analyzer)
        self.cache_dep_detector = CacheDependencyDetector(self.dependency_analyzer)
        self.security_dep_detector = SecurityDependencyDetector(self.dependency_analyzer)
        self.feature_dep_detector = FeatureDependencyDetector(self.dependency_analyzer)

        # Configuration parsing
        self.config_parser = ConfigParser(self.resources, self.logger)
        self.db_config_extractor = DatabaseConfigExtractor(self.logger)
        self.actuator_config_extractor = ActuatorConfigExtractor(self.logger)
        self.security_config_extractor = SecurityConfigExtractor(self.src_main, self.logger)

    def analyze(self) -> SpringBootAnalysis:
        """
        Perform comprehensive Spring Boot analysis.

        Returns:
            SpringBootAnalysis with all detected information
        """
        analysis = SpringBootAnalysis()

        # Application structure
        self._analyze_application_structure(analysis)

        # Layers
        self._analyze_layers(analysis)

        # REST API
        self._analyze_rest_api(analysis)

        # Configuration
        self._analyze_configuration(analysis)

        # Database
        self._analyze_database(analysis)

        # Security
        self._analyze_security(analysis)

        # Features
        self._analyze_features(analysis)

        # Testing
        self._analyze_testing(analysis)

        # Version
        self._analyze_version(analysis)

        return analysis

    def _analyze_application_structure(self, analysis: SpringBootAnalysis) -> None:
        """
        Analyze application structure and main class.

        Args:
            analysis: SpringBootAnalysis to populate
        """
        analysis.main_application_class = self.annotation_scanner.find_main_application_class(
            self.src_main
        )

        if not analysis.main_application_class:
            return

        analysis.base_package = PackageExtractor.extract_base_package(
            analysis.main_application_class
        )

    def _analyze_layers(self, analysis: SpringBootAnalysis) -> None:
        """
        Analyze application layers (controllers, services, repositories).

        Args:
            analysis: SpringBootAnalysis to populate
        """
        analysis.controllers = self.annotation_scanner.find_annotated_classes(
            self.src_main,
            "@RestController",
            "@Controller"
        )

        analysis.services = self.annotation_scanner.find_annotated_classes(
            self.src_main,
            "@Service"
        )

        analysis.repositories = self.annotation_scanner.find_annotated_classes(
            self.src_main,
            "@Repository"
        )

        analysis.entities = self.annotation_scanner.find_annotated_classes(
            self.src_main,
            "@Entity"
        )

        analysis.configurations = self.annotation_scanner.find_annotated_classes(
            self.src_main,
            "@Configuration"
        )

    def _analyze_rest_api(self, analysis: SpringBootAnalysis) -> None:
        """
        Analyze REST API endpoints.

        Args:
            analysis: SpringBootAnalysis to populate
        """
        analysis.rest_endpoints = self.rest_scanner.scan_rest_endpoints(self.src_main)

    def _analyze_configuration(self, analysis: SpringBootAnalysis) -> None:
        """
        Analyze application configuration files.

        Args:
            analysis: SpringBootAnalysis to populate
        """
        analysis.application_properties = self.config_parser.load_properties()
        analysis.active_profiles = self.config_parser.get_active_profiles()

    def _analyze_database(self, analysis: SpringBootAnalysis) -> None:
        """
        Analyze database configuration and usage.

        Args:
            analysis: SpringBootAnalysis to populate
        """
        # Extract database config from properties
        analysis.database_config = self.db_config_extractor.extract_database_config(
            analysis.application_properties,
            self.db_dep_detector.detect_database_type
        )

        # Check JPA and migration tools
        analysis.uses_jpa = self.db_dep_detector.check_jpa_usage(analysis.entities)
        analysis.uses_liquibase = self.db_dep_detector.check_liquibase_usage()
        analysis.uses_flyway = self.db_dep_detector.check_flyway_usage()

    def _analyze_security(self, analysis: SpringBootAnalysis) -> None:
        """
        Analyze security configuration.

        Args:
            analysis: SpringBootAnalysis to populate
        """
        config = SecurityConfig()

        # Check security dependencies
        config.enabled = self.security_dep_detector.check_security_enabled()
        config.oauth_enabled = self.security_dep_detector.check_oauth_enabled()
        config.jwt_enabled = self.security_dep_detector.check_jwt_enabled()

        # Detect security features from configuration files
        security_features = self.security_config_extractor.detect_security_features()
        config.basic_auth = security_features['basic_auth']
        config.form_login = security_features['form_login']
        config.cors_enabled = security_features['cors_enabled']
        config.csrf_enabled = security_features['csrf_enabled']

        analysis.security_config = config

    def _analyze_features(self, analysis: SpringBootAnalysis) -> None:
        """
        Analyze Spring Boot features (actuator, async, caching).

        Args:
            analysis: SpringBootAnalysis to populate
        """
        # Actuator
        analysis.actuator_enabled = self.feature_dep_detector.check_actuator_enabled()
        if analysis.actuator_enabled:
            analysis.actuator_endpoints = self.actuator_config_extractor.get_exposed_endpoints(
                analysis.application_properties
            )

        # DevTools
        analysis.devtools_enabled = self.feature_dep_detector.check_devtools_enabled()

        # Async/Scheduling
        analysis.has_async_methods = self.annotation_scanner.check_annotation_usage(
            self.src_main,
            "@Async"
        )
        analysis.has_scheduled_tasks = self.annotation_scanner.check_annotation_usage(
            self.src_main,
            "@Scheduled"
        )

        # Caching
        analysis.caching_enabled = self.annotation_scanner.check_annotation_usage(
            self.src_main,
            "@EnableCaching"
        )
        analysis.cache_provider = self.cache_dep_detector.detect_cache_provider()

    def _analyze_testing(self, analysis: SpringBootAnalysis) -> None:
        """
        Analyze testing setup.

        Args:
            analysis: SpringBootAnalysis to populate
        """
        # Import here to avoid circular dependency
        from .architecture_detector import TestArchitectureDetector

        test_detector = TestArchitectureDetector(self.src_test, self.logger)
        analysis.test_classes = test_detector.find_test_classes()
        analysis.uses_testcontainers = self.feature_dep_detector.check_testcontainers_enabled()

    def _analyze_version(self, analysis: SpringBootAnalysis) -> None:
        """
        Analyze Spring Boot version.

        Args:
            analysis: SpringBootAnalysis to populate
        """
        analysis.spring_boot_version = self.dependency_analyzer.get_spring_boot_version()
