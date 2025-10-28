#!/usr/bin/env python3
"""
Java Ecosystem Models

WHY: Centralizes data structures for Java ecosystem analysis, providing
     type-safe representations of build systems, frameworks, and project metadata.

RESPONSIBILITY:
    - Define JavaEcosystemAnalysis dataclass for comprehensive analysis results
    - Provide structured data models for Maven, Gradle, and framework info
    - Support backward compatibility with existing code using these models

PATTERNS:
    - Dataclass pattern for immutable, type-safe data structures
    - Composition pattern - contains Maven/Gradle/framework analysis objects
    - Builder pattern (via field defaults) for incremental construction
"""

from dataclasses import dataclass, field
from typing import Dict, Optional

# Import external models
from maven_manager import MavenProjectInfo
from gradle_manager import GradleProjectInfo
from java_web_framework_detector import JavaWebFrameworkAnalysis
from spring_boot_analyzer import SpringBootAnalysis


@dataclass
class JavaEcosystemAnalysis:
    """
    Comprehensive Java ecosystem analysis results.

    WHY: Provides single data structure containing all Java project metadata,
         eliminating need for multiple return values or complex tuples.

    Attributes:
        build_system: Detected build system (Maven, Gradle, or Unknown)
        maven_info: Maven project information if Maven detected
        gradle_info: Gradle project information if Gradle detected
        web_framework_analysis: Web framework detection results
        spring_boot_analysis: Spring Boot-specific analysis
        is_java_project: Whether this is a valid Java project
        is_spring_boot: Whether project uses Spring Boot
        is_web_application: Whether project is a web application
        is_microservices: Whether project follows microservices architecture
        recommended_test_framework: Recommended testing framework (junit/testng)
        has_existing_tests: Whether project has existing test files
        summary: Quick facts dictionary for display
    """
    # Build system
    build_system: str  # Maven, Gradle, or Unknown
    maven_info: Optional[MavenProjectInfo] = None
    gradle_info: Optional[GradleProjectInfo] = None

    # Framework analysis
    web_framework_analysis: Optional[JavaWebFrameworkAnalysis] = None
    spring_boot_analysis: Optional[SpringBootAnalysis] = None

    # Project summary
    is_java_project: bool = False
    is_spring_boot: bool = False
    is_web_application: bool = False
    is_microservices: bool = False

    # Test configuration
    recommended_test_framework: str = "junit"
    has_existing_tests: bool = False

    # Quick facts
    summary: Dict[str, str] = field(default_factory=dict)

    def get_build_system_type(self) -> str:
        """
        Get normalized build system type.

        Returns:
            Build system type (Maven, Gradle, or Unknown)
        """
        return self.build_system

    def has_build_info(self) -> bool:
        """
        Check if build information is available.

        Returns:
            True if Maven or Gradle info available
        """
        return self.maven_info is not None or self.gradle_info is not None

    def get_project_name(self) -> Optional[str]:
        """
        Get project name from build system.

        Returns:
            Project artifact/name or None
        """
        if self.maven_info:
            return self.maven_info.artifact_id
        if self.gradle_info:
            return self.gradle_info.name
        return None

    def get_project_version(self) -> Optional[str]:
        """
        Get project version from build system.

        Returns:
            Project version or None
        """
        if self.maven_info:
            return self.maven_info.version
        if self.gradle_info:
            return self.gradle_info.version
        return None


__all__ = ['JavaEcosystemAnalysis']
