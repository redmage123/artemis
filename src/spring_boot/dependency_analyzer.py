#!/usr/bin/env python3
"""
WHY: Analyze project dependencies from build files (Maven/Gradle)
RESPONSIBILITY: Parse build files and detect Spring Boot dependencies
PATTERNS: Strategy Pattern (different build tools), Guard Clauses, Dispatch Tables

This module analyzes build files to extract:
- Spring Boot version
- Dependency artifacts (starters, libraries)
- Build tool configuration (Maven, Gradle)
"""

from pathlib import Path
from typing import Optional, Dict, Callable
import xml.etree.ElementTree as ET
import logging


class DependencyAnalyzer:
    """
    Analyzer for project dependencies from build files.

    Supports Maven (pom.xml) and Gradle (build.gradle, build.gradle.kts).
    """

    def __init__(self, project_dir: Path, logger: Optional[logging.Logger] = None):
        """
        Initialize dependency analyzer.

        Args:
            project_dir: Spring Boot project root directory
            logger: Optional logger for diagnostic messages
        """
        self.project_dir = project_dir
        self.logger = logger or logging.getLogger(__name__)
        self._maven_cache: Optional[str] = None

    def check_dependency(self, artifact_id: str) -> bool:
        """
        Check if dependency exists in any build file.

        Args:
            artifact_id: Artifact ID to search for

        Returns:
            True if dependency is found
        """
        build_files = [
            self.project_dir / "pom.xml",
            self.project_dir / "build.gradle",
            self.project_dir / "build.gradle.kts"
        ]

        for build_file in build_files:
            if not build_file.exists():
                continue

            content = build_file.read_text()
            if artifact_id in content:
                return True

        return False

    def get_spring_boot_version(self) -> Optional[str]:
        """
        Get Spring Boot version from build file.

        Returns:
            Spring Boot version string or None
        """
        pom = self.project_dir / "pom.xml"

        if not pom.exists():
            return None

        return self._extract_spring_boot_version_from_pom(pom)

    def _extract_spring_boot_version_from_pom(self, pom: Path) -> Optional[str]:
        """
        Extract Spring Boot version from Maven POM file.

        Args:
            pom: Path to pom.xml

        Returns:
            Spring Boot version or None
        """
        try:
            tree = ET.parse(pom)
            root = tree.getroot()
            ns = {"mvn": "http://maven.apache.org/POM/4.0.0"}

            # Strategy 1: Check parent for Spring Boot version
            version = self._extract_version_from_parent(root, ns)
            if version:
                return version

            # Strategy 2: Check dependencies for Spring Boot version
            version = self._extract_version_from_dependencies(root, ns)
            if version:
                return version

        except Exception as e:
            self.logger.warning(f"Failed to parse pom.xml: {e}")

        return None

    def _extract_version_from_parent(
        self,
        root: ET.Element,
        ns: Dict[str, str]
    ) -> Optional[str]:
        """
        Extract Spring Boot version from parent POM.

        Args:
            root: XML root element
            ns: XML namespace dictionary

        Returns:
            Spring Boot version or None
        """
        parent = root.find(".//mvn:parent", ns)
        if not parent:
            return None

        artifact = parent.find("mvn:artifactId", ns)
        if not artifact or "spring-boot" not in artifact.text:
            return None

        version = parent.find("mvn:version", ns)
        return version.text if version is not None else None

    def _extract_version_from_dependencies(
        self,
        root: ET.Element,
        ns: Dict[str, str]
    ) -> Optional[str]:
        """
        Extract Spring Boot version from dependencies.

        Args:
            root: XML root element
            ns: XML namespace dictionary

        Returns:
            Spring Boot version or None
        """
        for dep in root.findall(".//mvn:dependency", ns):
            artifact = dep.find("mvn:artifactId", ns)
            if not artifact or "spring-boot-starter" not in artifact.text:
                continue

            version = dep.find("mvn:version", ns)
            if version is not None:
                return version.text

        return None


class DatabaseDependencyDetector:
    """
    Detector for database-related dependencies.

    Identifies JPA, migration tools, and database drivers.
    """

    # Dispatch table for database type detection from JDBC URL
    DATABASE_TYPE_PATTERNS = {
        'postgresql': 'PostgreSQL',
        'mysql': 'MySQL',
        'h2': 'H2',
        'oracle': 'Oracle',
        'sqlserver': 'SQL Server',
    }

    def __init__(self, dependency_analyzer: DependencyAnalyzer):
        """
        Initialize database dependency detector.

        Args:
            dependency_analyzer: DependencyAnalyzer instance
        """
        self.dependency_analyzer = dependency_analyzer

    def check_jpa_usage(self, entities: list) -> bool:
        """
        Check if JPA is used in the project.

        Args:
            entities: List of entity classes found

        Returns:
            True if JPA entities exist
        """
        return len(entities) > 0

    def check_liquibase_usage(self) -> bool:
        """
        Check if Liquibase is used.

        Returns:
            True if Liquibase dependency exists
        """
        return self.dependency_analyzer.check_dependency("liquibase")

    def check_flyway_usage(self) -> bool:
        """
        Check if Flyway is used.

        Returns:
            True if Flyway dependency exists
        """
        return self.dependency_analyzer.check_dependency("flyway")

    def detect_database_type(self, jdbc_url: Optional[str]) -> Optional[str]:
        """
        Detect database type from JDBC URL.

        Args:
            jdbc_url: JDBC connection URL

        Returns:
            Database type name or None
        """
        if not jdbc_url:
            return None

        url_lower = jdbc_url.lower()
        for pattern, db_type in self.DATABASE_TYPE_PATTERNS.items():
            if pattern in url_lower:
                return db_type

        return None


class CacheDependencyDetector:
    """
    Detector for caching dependencies.

    Identifies cache providers like Caffeine, EhCache, Redis, etc.
    """

    # Dispatch table for cache provider detection
    CACHE_PROVIDERS = {
        'caffeine': 'Caffeine',
        'ehcache': 'EhCache',
        'hazelcast': 'Hazelcast',
        'redis': 'Redis',
    }

    def __init__(self, dependency_analyzer: DependencyAnalyzer):
        """
        Initialize cache dependency detector.

        Args:
            dependency_analyzer: DependencyAnalyzer instance
        """
        self.dependency_analyzer = dependency_analyzer

    def detect_cache_provider(self) -> Optional[str]:
        """
        Detect caching provider from dependencies.

        Returns:
            Cache provider name or None
        """
        if not self.dependency_analyzer.check_dependency("spring-boot-starter-cache"):
            return None

        for artifact_id, provider_name in self.CACHE_PROVIDERS.items():
            if self.dependency_analyzer.check_dependency(artifact_id):
                return provider_name

        return "Simple (in-memory)"


class SecurityDependencyDetector:
    """
    Detector for security-related dependencies.

    Identifies Spring Security, OAuth2, and JWT dependencies.
    """

    def __init__(self, dependency_analyzer: DependencyAnalyzer):
        """
        Initialize security dependency detector.

        Args:
            dependency_analyzer: DependencyAnalyzer instance
        """
        self.dependency_analyzer = dependency_analyzer

    def check_security_enabled(self) -> bool:
        """
        Check if Spring Security is enabled.

        Returns:
            True if Spring Security dependency exists
        """
        return self.dependency_analyzer.check_dependency("spring-boot-starter-security")

    def check_oauth_enabled(self) -> bool:
        """
        Check if OAuth2 is enabled.

        Returns:
            True if OAuth2 dependency exists
        """
        return self.dependency_analyzer.check_dependency("spring-security-oauth2")

    def check_jwt_enabled(self) -> bool:
        """
        Check if JWT is enabled.

        Returns:
            True if JJWT dependency exists
        """
        return self.dependency_analyzer.check_dependency("jjwt")


class FeatureDependencyDetector:
    """
    Detector for Spring Boot feature dependencies.

    Identifies Actuator, DevTools, Testcontainers, etc.
    """

    def __init__(self, dependency_analyzer: DependencyAnalyzer):
        """
        Initialize feature dependency detector.

        Args:
            dependency_analyzer: DependencyAnalyzer instance
        """
        self.dependency_analyzer = dependency_analyzer

    def check_actuator_enabled(self) -> bool:
        """
        Check if Spring Boot Actuator is enabled.

        Returns:
            True if Actuator dependency exists
        """
        return self.dependency_analyzer.check_dependency("spring-boot-starter-actuator")

    def check_devtools_enabled(self) -> bool:
        """
        Check if Spring Boot DevTools is enabled.

        Returns:
            True if DevTools dependency exists
        """
        return self.dependency_analyzer.check_dependency("spring-boot-devtools")

    def check_testcontainers_enabled(self) -> bool:
        """
        Check if Testcontainers is used.

        Returns:
            True if Testcontainers dependency exists
        """
        return self.dependency_analyzer.check_dependency("testcontainers")
