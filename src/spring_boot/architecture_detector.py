#!/usr/bin/env python3
"""
WHY: Detect architectural patterns in Spring Boot applications
RESPONSIBILITY: Identify MVC, REST, WebFlux, and other architectural patterns
PATTERNS: Strategy Pattern (different pattern detectors), Guard Clauses

This module provides architectural pattern detection:
- Layered architecture (Controller, Service, Repository)
- REST API architecture detection
- Test architecture analysis
- Package structure analysis
"""

from pathlib import Path
from typing import List, Optional
import logging


class PackageExtractor:
    """
    Extractor for package information from fully qualified class names.

    Provides utilities to extract package names and base packages.
    """

    @staticmethod
    def extract_package(fully_qualified_class: str) -> str:
        """
        Extract package from fully qualified class name.

        Args:
            fully_qualified_class: Full class name like 'com.example.MyClass'

        Returns:
            Package name or empty string
        """
        parts = fully_qualified_class.rsplit(".", 1)
        return parts[0] if len(parts) > 1 else ""

    @staticmethod
    def extract_base_package(main_class: Optional[str]) -> Optional[str]:
        """
        Extract base package from main application class.

        Args:
            main_class: Fully qualified main application class name

        Returns:
            Base package name or None
        """
        if not main_class:
            return None

        return PackageExtractor.extract_package(main_class)


class LayeredArchitectureDetector:
    """
    Detector for layered architecture pattern.

    Identifies Controller, Service, and Repository layers
    to determine if the application follows layered architecture.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize layered architecture detector.

        Args:
            logger: Optional logger for diagnostic messages
        """
        self.logger = logger or logging.getLogger(__name__)

    def has_layered_architecture(
        self,
        controllers: List[str],
        services: List[str],
        repositories: List[str]
    ) -> bool:
        """
        Check if application follows layered architecture.

        Args:
            controllers: List of controller classes
            services: List of service classes
            repositories: List of repository classes

        Returns:
            True if layered architecture is detected
        """
        # Application has layered architecture if it has all three layers
        return bool(controllers and services and repositories)

    def get_layer_counts(
        self,
        controllers: List[str],
        services: List[str],
        repositories: List[str],
        entities: List[str]
    ) -> dict:
        """
        Get counts for each architectural layer.

        Args:
            controllers: List of controller classes
            services: List of service classes
            repositories: List of repository classes
            entities: List of entity classes

        Returns:
            Dictionary with layer counts
        """
        return {
            'controllers': len(controllers),
            'services': len(services),
            'repositories': len(repositories),
            'entities': len(entities)
        }


class RestArchitectureDetector:
    """
    Detector for REST API architecture.

    Analyzes REST endpoints to determine API characteristics
    and architectural patterns.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize REST architecture detector.

        Args:
            logger: Optional logger for diagnostic messages
        """
        self.logger = logger or logging.getLogger(__name__)

    def is_rest_api(self, rest_endpoints: List) -> bool:
        """
        Check if application is primarily a REST API.

        Args:
            rest_endpoints: List of REST endpoints

        Returns:
            True if REST API detected
        """
        return len(rest_endpoints) > 0

    def get_endpoint_statistics(self, rest_endpoints: List) -> dict:
        """
        Get statistics about REST endpoints.

        Args:
            rest_endpoints: List of RestEndpoint objects

        Returns:
            Dictionary with endpoint statistics
        """
        if not rest_endpoints:
            return {
                'total': 0,
                'by_method': {},
                'controllers': []
            }

        # Count by HTTP method
        by_method = {}
        controllers = set()

        for endpoint in rest_endpoints:
            for method in endpoint.methods:
                by_method[method] = by_method.get(method, 0) + 1
            controllers.add(endpoint.controller_class)

        return {
            'total': len(rest_endpoints),
            'by_method': by_method,
            'controllers': list(controllers)
        }


class TestArchitectureDetector:
    """
    Detector for test architecture and testing strategies.

    Analyzes test classes and testing frameworks.
    """

    def __init__(self, src_test: Path, logger: Optional[logging.Logger] = None):
        """
        Initialize test architecture detector.

        Args:
            src_test: Path to src/test/java directory
            logger: Optional logger for diagnostic messages
        """
        self.src_test = src_test
        self.logger = logger or logging.getLogger(__name__)

    def find_test_classes(self) -> List[str]:
        """
        Find all test classes in the project.

        Returns:
            List of fully qualified test class names
        """
        if not self.src_test.exists():
            return []

        test_classes = []

        for java_file in self.src_test.glob("**/*Test.java"):
            package = self._extract_package_from_file(java_file)
            class_name = java_file.stem
            test_classes.append(f"{package}.{class_name}")

        return test_classes

    def get_test_statistics(self, test_classes: List[str]) -> dict:
        """
        Get statistics about test classes.

        Args:
            test_classes: List of test class names

        Returns:
            Dictionary with test statistics
        """
        return {
            'total': len(test_classes),
            'unit_tests': self._count_unit_tests(test_classes),
            'integration_tests': self._count_integration_tests(test_classes)
        }

    def _extract_package_from_file(self, java_file: Path) -> str:
        """
        Extract package declaration from Java file.

        Args:
            java_file: Path to Java source file

        Returns:
            Package name or empty string
        """
        import re
        content = java_file.read_text()
        match = re.search(r'package\s+([\w.]+);', content)
        return match.group(1) if match else ""

    def _count_unit_tests(self, test_classes: List[str]) -> int:
        """
        Count unit test classes.

        Args:
            test_classes: List of test class names

        Returns:
            Count of unit tests
        """
        # Simple heuristic: tests not in 'integration' package
        return sum(1 for tc in test_classes if 'integration' not in tc.lower())

    def _count_integration_tests(self, test_classes: List[str]) -> int:
        """
        Count integration test classes.

        Args:
            test_classes: List of test class names

        Returns:
            Count of integration tests
        """
        # Simple heuristic: tests in 'integration' package or with 'IT' suffix
        return sum(
            1 for tc in test_classes
            if 'integration' in tc.lower() or tc.endswith('IT')
        )


class FeatureDetector:
    """
    Detector for Spring Boot features and capabilities.

    Identifies async processing, scheduling, caching, and other features.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize feature detector.

        Args:
            logger: Optional logger for diagnostic messages
        """
        self.logger = logger or logging.getLogger(__name__)

    def detect_async_features(self, has_async: bool, has_scheduled: bool) -> dict:
        """
        Detect async and scheduling features.

        Args:
            has_async: Whether @Async is used
            has_scheduled: Whether @Scheduled is used

        Returns:
            Dictionary with async feature flags
        """
        return {
            'async_enabled': has_async,
            'scheduling_enabled': has_scheduled,
            'concurrent_processing': has_async or has_scheduled
        }

    def detect_caching_features(
        self,
        caching_enabled: bool,
        cache_provider: Optional[str]
    ) -> dict:
        """
        Detect caching features.

        Args:
            caching_enabled: Whether @EnableCaching is used
            cache_provider: Cache provider name

        Returns:
            Dictionary with caching feature details
        """
        return {
            'enabled': caching_enabled,
            'provider': cache_provider,
            'distributed': cache_provider in ['Redis', 'Hazelcast']
        }

    def detect_monitoring_features(
        self,
        actuator_enabled: bool,
        actuator_endpoints: List[str]
    ) -> dict:
        """
        Detect monitoring and observability features.

        Args:
            actuator_enabled: Whether Actuator is enabled
            actuator_endpoints: List of exposed endpoints

        Returns:
            Dictionary with monitoring feature details
        """
        has_metrics = 'metrics' in actuator_endpoints
        has_health = 'health' in actuator_endpoints

        return {
            'actuator_enabled': actuator_enabled,
            'metrics_exposed': has_metrics,
            'health_checks': has_health,
            'production_ready': actuator_enabled and has_metrics and has_health
        }
