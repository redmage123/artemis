#!/usr/bin/env python3
"""
WHY: Main facade orchestrating Java framework detection and analysis
RESPONSIBILITY: Coordinates all analyzer components and provides unified interface
PATTERNS: Facade Pattern, Strategy Pattern, Guard Clauses, Dependency Injection
"""

import logging
from pathlib import Path
from typing import Optional

from java_framework.analyzer.architecture_analyzer import ArchitectureAnalyzer
from java_framework.analyzer.build_system_detector import BuildSystemDetector
from java_framework.analyzer.dependency_parser import DependencyParser
from java_framework.analyzer.technology_detector import TechnologyDetector
from java_framework.analyzer.version_extractor import VersionExtractor
from java_framework.detector_registry import DetectorRegistry
from java_framework.models import JavaWebFrameworkAnalysis


class JavaWebFrameworkAnalyzer:
    """
    WHY: Orchestrates comprehensive Java web framework analysis
    RESPONSIBILITY: Manages build file parsing, framework detection, and technology analysis
    PATTERNS: Facade Pattern - provides simple interface to complex subsystem
    """

    def __init__(
        self,
        project_dir: Optional[Path] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize analyzer with project directory and logger

        Args:
            project_dir: Java project root directory
            logger: Optional logger
        """
        self.project_dir = Path(project_dir) if project_dir else Path.cwd()
        self.logger = logger or logging.getLogger(__name__)

        # Initialize all analyzer components (Dependency Injection)
        self._build_detector = BuildSystemDetector(self.project_dir)
        self._dependency_parser = DependencyParser(logger=self.logger)
        self._tech_detector = TechnologyDetector(self.project_dir)
        self._version_extractor = VersionExtractor()
        self._architecture_analyzer = ArchitectureAnalyzer(self.project_dir)
        self._detector_registry = DetectorRegistry()

    def analyze(self) -> JavaWebFrameworkAnalysis:
        """
        WHY: Performs comprehensive Java web framework analysis
        RESPONSIBILITY: Orchestrates all analysis steps and returns results

        Returns:
            JavaWebFrameworkAnalysis with detected technologies
        """
        # Step 1: Detect build system
        build_system = self._build_detector.detect()

        # Step 2: Parse dependencies
        dependencies = self._parse_dependencies_for_build_system(build_system)

        # Step 3: Detect primary framework using registry
        framework = self._detector_registry.detect_framework(dependencies)
        framework_version = self._version_extractor.get_framework_version(framework, dependencies)

        # Step 4: Detect web server
        web_server = self._tech_detector.detect_web_server(dependencies)
        web_server_version = self._version_extractor.get_web_server_version(web_server, dependencies)

        # Step 5: Detect template engines
        template_engines = self._tech_detector.detect_template_engines(dependencies)

        # Step 6: Detect database technologies
        db_techs = self._tech_detector.detect_database_technologies(dependencies)
        databases = self._tech_detector.detect_databases(dependencies)

        # Step 7: Detect API technologies
        has_rest, rest_framework = self._tech_detector.detect_rest_api(dependencies)
        has_graphql = self._tech_detector.detect_graphql(dependencies)
        has_soap = self._tech_detector.detect_soap(dependencies)

        # Step 8: Detect security frameworks
        security_frameworks = self._tech_detector.detect_security_frameworks(dependencies)
        has_oauth = self._tech_detector.detect_oauth(dependencies)
        has_jwt = self._tech_detector.detect_jwt(dependencies)

        # Step 9: Detect test frameworks
        test_frameworks = self._tech_detector.detect_test_frameworks(dependencies)

        # Step 10: Detect messaging and caching
        messaging = self._tech_detector.detect_messaging(dependencies)
        caching = self._tech_detector.detect_caching(dependencies)

        # Step 11: Detect configuration format
        config_format = self._tech_detector.detect_config_format()

        # Step 12: Analyze architecture
        is_microservices, is_monolith, modules = self._architecture_analyzer.analyze()

        # Return comprehensive analysis result
        return JavaWebFrameworkAnalysis(
            primary_framework=framework,
            framework_version=framework_version,
            web_server=web_server,
            web_server_version=web_server_version,
            build_system=build_system,
            template_engines=template_engines,
            database_technologies=db_techs,
            databases=databases,
            has_rest_api=has_rest,
            has_graphql=has_graphql,
            has_soap=has_soap,
            rest_framework=rest_framework,
            security_frameworks=security_frameworks,
            has_oauth=has_oauth,
            has_jwt=has_jwt,
            test_frameworks=test_frameworks,
            messaging=messaging,
            caching=caching,
            config_format=config_format,
            dependencies=dependencies,
            is_microservices=is_microservices,
            is_monolith=is_monolith,
            modules=modules
        )

    def _parse_dependencies_for_build_system(self, build_system: str) -> dict:
        """
        WHY: Parses dependencies from appropriate build file
        RESPONSIBILITY: Gets build file path and delegates to dependency parser

        Args:
            build_system: Build system name

        Returns:
            Dictionary of dependencies
        """
        # Guard clause: handle unknown build system
        if build_system == "Unknown":
            return {}

        # Get build file path based on build system
        if build_system == "Maven":
            build_file = self._build_detector.get_maven_path()
        elif build_system == "Gradle":
            build_file = self._build_detector.get_gradle_path()
        else:
            return {}

        # Guard clause: check if build file exists
        if not build_file:
            return {}

        return self._dependency_parser.parse(build_system, build_file)
