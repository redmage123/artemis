#!/usr/bin/env python3
"""
Java Ecosystem Core Integration

WHY: Orchestrates all Java ecosystem components (Maven, Gradle, frameworks) to
     provide comprehensive Java project analysis and build management.

RESPONSIBILITY:
    - Initialize and coordinate Maven/Gradle integrations
    - Perform comprehensive Java project analysis
    - Detect web frameworks and Spring Boot
    - Recommend appropriate test frameworks
    - Coordinate build and test operations
    - Generate project summary reports

PATTERNS:
    - Facade pattern - provides simplified interface to complex subsystems
    - Strategy pattern - delegates to Maven/Gradle integrations
    - Guard clauses - early returns to avoid nesting
    - Single Responsibility - each method has one clear purpose
"""

from pathlib import Path
from typing import Dict, Optional
import logging

from java_ecosystem.models import JavaEcosystemAnalysis
from java_ecosystem.maven_integration import MavenIntegration
from java_ecosystem.gradle_integration import GradleIntegration
from java_ecosystem.dependency_resolver import DependencyResolver
from java_ecosystem.build_coordinator import BuildCoordinator

# Import framework detection modules
from java_web_framework_detector import JavaWebFrameworkDetector
from spring_boot_analyzer import SpringBootAnalyzer


class JavaEcosystemManager:
    """
    Unified Java ecosystem manager for Artemis.

    WHY: Provides single entry point for Java project analysis and
         build automation, abstracting away differences between Maven and Gradle.

    Provides comprehensive Java project understanding including:
    - Build system (Maven/Gradle)
    - Web frameworks (Spring Boot, Jakarta EE, etc.)
    - Project structure and dependencies
    - Automated building and testing
    """

    def __init__(
        self,
        project_dir: Optional[Path] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize Java ecosystem manager.

        Args:
            project_dir: Java project root directory
            logger: Optional logger

        WHY: Minimal initialization - defer expensive operations until needed
        """
        self.project_dir = Path(project_dir) if project_dir else Path.cwd()
        self.logger = logger or logging.getLogger(__name__)

        # Initialize integrations
        self.maven = MavenIntegration(self.project_dir, self.logger)
        self.gradle = GradleIntegration(self.project_dir, self.logger)

        # Detect build system
        self._detect_build_system()

        # Initialize coordinators
        self._init_build_coordinator()
        self._init_dependency_resolver()

    def _detect_build_system(self) -> None:
        """
        Detect and initialize appropriate build system.

        WHY: Guard clause pattern - try Maven first, then Gradle
        """
        if self.maven.detect_and_initialize():
            return

        self.gradle.detect_and_initialize()

    def _init_build_coordinator(self) -> None:
        """
        Initialize build coordinator with detected build system.

        WHY: Separated initialization for Single Responsibility Principle
        """
        maven_build = self.maven.build if self.maven.is_available() else None
        maven_test = self.maven.run_tests if self.maven.is_available() else None
        gradle_build = self.gradle.build if self.gradle.is_available() else None
        gradle_test = self.gradle.run_tests if self.gradle.is_available() else None

        self.build_coordinator = BuildCoordinator(
            maven_build=maven_build,
            maven_test=maven_test,
            gradle_build=gradle_build,
            gradle_test=gradle_test,
            logger=self.logger
        )

    def _init_dependency_resolver(self) -> None:
        """
        Initialize dependency resolver with detected build system.

        WHY: Separated initialization for Single Responsibility Principle
        """
        maven_add_dep = (
            self.maven.add_dependency if self.maven.is_available() else None
        )
        gradle_add_dep = (
            self.gradle.add_dependency if self.gradle.is_available() else None
        )

        self.dependency_resolver = DependencyResolver(
            maven_add_dependency=maven_add_dep,
            gradle_add_dependency=gradle_add_dep,
            logger=self.logger
        )

    def is_java_project(self) -> bool:
        """
        Check if this is a Java project.

        Returns:
            True if Maven or Gradle detected
        """
        return self.maven.is_available() or self.gradle.is_available()

    def analyze_project(self) -> JavaEcosystemAnalysis:
        """
        Perform comprehensive Java project analysis.

        Returns:
            JavaEcosystemAnalysis with complete project understanding

        WHY: Guard clause pattern - early return if not Java project
        """
        analysis = JavaEcosystemAnalysis(
            build_system="Unknown",
            is_java_project=self.is_java_project()
        )

        # Guard clause: early return if not Java project
        if not analysis.is_java_project:
            self.logger.warning("Not a Java project")
            return analysis

        self._analyze_build_system(analysis)
        self._analyze_web_framework(analysis)
        self._analyze_spring_boot(analysis)
        self._determine_test_framework(analysis)
        self._check_existing_tests(analysis)
        self._build_summary(analysis)

        return analysis

    def _analyze_build_system(self, analysis: JavaEcosystemAnalysis) -> None:
        """
        Analyze build system and populate analysis.

        Args:
            analysis: Analysis object to populate

        WHY: Guard clause pattern - check Maven first, then Gradle
        """
        if self.maven.is_available():
            analysis.build_system = "Maven"
            analysis.maven_info = self.maven.get_project_info()
            return

        if self.gradle.is_available():
            analysis.build_system = "Gradle"
            analysis.gradle_info = self.gradle.get_project_info()

    def _analyze_web_framework(self, analysis: JavaEcosystemAnalysis) -> None:
        """
        Analyze web framework and populate analysis.

        Args:
            analysis: Analysis object to populate

        WHY: Guard clause pattern - early return on exception
        """
        try:
            detector = JavaWebFrameworkDetector(
                project_dir=self.project_dir,
                logger=self.logger
            )
            analysis.web_framework_analysis = detector.analyze()
            analysis.is_web_application = (
                analysis.web_framework_analysis.has_rest_api or
                len(analysis.web_framework_analysis.template_engines) > 0
            )
            analysis.is_spring_boot = (
                analysis.web_framework_analysis.primary_framework.value == "Spring Boot"
            )
            analysis.is_microservices = (
                analysis.web_framework_analysis.is_microservices
            )

        except Exception as e:
            self.logger.warning(f"Web framework detection failed: {e}")

    def _analyze_spring_boot(self, analysis: JavaEcosystemAnalysis) -> None:
        """
        Analyze Spring Boot if detected.

        Args:
            analysis: Analysis object to populate

        WHY: Guard clause - early return if not Spring Boot
        """
        if not analysis.is_spring_boot:
            return

        try:
            spring_analyzer = SpringBootAnalyzer(
                project_dir=self.project_dir,
                logger=self.logger
            )
            analysis.spring_boot_analysis = spring_analyzer.analyze()

        except Exception as e:
            self.logger.warning(f"Spring Boot analysis failed: {e}")

    def _determine_test_framework(self, analysis: JavaEcosystemAnalysis) -> None:
        """
        Determine recommended test framework.

        Args:
            analysis: Analysis object to populate

        WHY: Dispatch table pattern - map dependencies to frameworks
        """
        # Guard clause: default to junit if no framework analysis
        if not analysis.web_framework_analysis:
            analysis.recommended_test_framework = "junit"
            return

        dependencies = analysis.web_framework_analysis.dependencies

        # Dispatch table for test framework detection
        framework_detectors = {
            "JUnit": "junit",
            "TestNG": "testng"
        }

        for dep_name, framework in framework_detectors.items():
            if dep_name in dependencies:
                analysis.recommended_test_framework = framework
                return

        # Default to JUnit
        analysis.recommended_test_framework = "junit"

    def _check_existing_tests(self, analysis: JavaEcosystemAnalysis) -> None:
        """
        Check if project has existing tests.

        Args:
            analysis: Analysis object to populate

        WHY: Guard clause - early return if no test directory
        """
        test_dir = self.project_dir / "src" / "test" / "java"
        if not test_dir.exists():
            analysis.has_existing_tests = False
            return

        test_files = list(test_dir.glob("**/*Test.java"))
        analysis.has_existing_tests = len(test_files) > 0

    def _build_summary(self, analysis: JavaEcosystemAnalysis) -> None:
        """
        Build quick summary of project.

        Args:
            analysis: Analysis object to populate

        WHY: Separated summary building for Single Responsibility Principle
        """
        summary = {
            "build_system": analysis.build_system,
            "is_java_project": str(analysis.is_java_project),
        }

        self._add_build_info_to_summary(summary, analysis)
        self._add_web_framework_to_summary(summary, analysis)
        self._add_spring_boot_to_summary(summary, analysis)

        summary["recommended_test_framework"] = analysis.recommended_test_framework

        analysis.summary = summary

    def _add_build_info_to_summary(
        self,
        summary: Dict[str, str],
        analysis: JavaEcosystemAnalysis
    ) -> None:
        """
        Add build system info to summary.

        Args:
            summary: Summary dictionary to populate
            analysis: Analysis object with build info

        WHY: Guard clause - early return after Maven
        """
        if analysis.maven_info:
            summary["group_id"] = analysis.maven_info.group_id
            summary["artifact_id"] = analysis.maven_info.artifact_id
            summary["version"] = analysis.maven_info.version
            summary["packaging"] = analysis.maven_info.packaging
            return

        if analysis.gradle_info:
            summary["group"] = analysis.gradle_info.group
            summary["name"] = analysis.gradle_info.name
            summary["version"] = analysis.gradle_info.version

    def _add_web_framework_to_summary(
        self,
        summary: Dict[str, str],
        analysis: JavaEcosystemAnalysis
    ) -> None:
        """
        Add web framework info to summary.

        Args:
            summary: Summary dictionary to populate
            analysis: Analysis object with framework info

        WHY: Guard clause - early return if no framework analysis
        """
        if not analysis.web_framework_analysis:
            return

        fw = analysis.web_framework_analysis
        summary["framework"] = fw.primary_framework.value
        summary["web_server"] = fw.web_server.value
        summary["has_rest_api"] = str(fw.has_rest_api)

        if fw.databases:
            summary["databases"] = ", ".join(fw.databases)

    def _add_spring_boot_to_summary(
        self,
        summary: Dict[str, str],
        analysis: JavaEcosystemAnalysis
    ) -> None:
        """
        Add Spring Boot info to summary.

        Args:
            summary: Summary dictionary to populate
            analysis: Analysis object with Spring Boot info

        WHY: Guard clause - early return if no Spring Boot analysis
        """
        if not analysis.spring_boot_analysis:
            return

        sb = analysis.spring_boot_analysis
        summary["spring_boot_version"] = sb.spring_boot_version or "unknown"
        summary["controllers"] = str(len(sb.controllers))
        summary["rest_endpoints"] = str(len(sb.rest_endpoints))

    def build(
        self,
        clean: bool = True,
        skip_tests: bool = False,
        timeout: int = 600
    ):
        """
        Build the Java project.

        Args:
            clean: Run clean before build
            skip_tests: Skip test execution
            timeout: Build timeout in seconds

        Returns:
            Build result (Maven or Gradle)

        WHY: Delegates to build coordinator
        """
        return self.build_coordinator.build(
            clean=clean,
            skip_tests=skip_tests,
            timeout=timeout
        )

    def run_tests(
        self,
        test_class: Optional[str] = None,
        test_method: Optional[str] = None,
        timeout: int = 300
    ):
        """
        Run tests in the Java project.

        Args:
            test_class: Specific test class to run
            test_method: Specific test method to run
            timeout: Test timeout in seconds

        Returns:
            Test result (Maven or Gradle)

        WHY: Delegates to build coordinator
        """
        return self.build_coordinator.run_tests(
            test_class=test_class,
            test_method=test_method,
            timeout=timeout
        )

    def get_build_system_name(self) -> str:
        """
        Get build system name.

        Returns:
            Build system name (Maven, Gradle, or Unknown)

        WHY: Delegates to build coordinator
        """
        return self.build_coordinator.get_build_system_name()

    def add_dependency(
        self,
        group_id: str,
        artifact_id: str,
        version: str,
        scope: str = "compile"
    ) -> bool:
        """
        Add dependency to project.

        Args:
            group_id: Dependency group ID
            artifact_id: Dependency artifact ID
            version: Dependency version
            scope: Dependency scope

        Returns:
            True if added successfully

        WHY: Delegates to dependency resolver
        """
        return self.dependency_resolver.add_dependency(
            group_id, artifact_id, version, scope
        )


__all__ = ['JavaEcosystemManager']
