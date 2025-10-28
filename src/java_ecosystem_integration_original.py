#!/usr/bin/env python3
"""
Java Ecosystem Integration for Artemis

Unified integration module that combines:
- Maven/Gradle build systems
- Java web framework detection
- Spring Boot analysis
- Test framework selection
- Automated build and test execution

This module provides a single entry point for Artemis to understand
and work with Java projects.

Usage:
    from java_ecosystem_integration import JavaEcosystemManager

    manager = JavaEcosystemManager(project_dir="/path/to/java-project")

    # Comprehensive analysis
    analysis = manager.analyze_project()

    # Build project
    build_result = manager.build()

    # Run tests
    test_result = manager.run_tests()
"""

from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass, field
import logging

# Import our Java ecosystem modules
from maven_manager import MavenManager, MavenBuildResult, MavenProjectInfo
from gradle_manager import GradleManager, GradleBuildResult, GradleProjectInfo
from java_web_framework_detector import JavaWebFrameworkDetector, JavaWebFrameworkAnalysis
from spring_boot_analyzer import SpringBootAnalyzer, SpringBootAnalysis


@dataclass
class JavaEcosystemAnalysis:
    """Comprehensive Java ecosystem analysis"""
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


class JavaEcosystemManager:
    """
    Unified Java ecosystem manager for Artemis.

    Why this exists: Provides single entry point for Java project analysis and
    build automation, abstracting away differences between Maven and Gradle.

    Provides comprehensive Java project understanding including:
    - Build system (Maven/Gradle)
    - Web frameworks (Spring Boot, Jakarta EE, etc.)
    - Project structure and dependencies
    - Automated building and testing

    What it does:
    - Auto-detects Maven (pom.xml) or Gradle (build.gradle)
    - Analyzes web framework and dependencies
    - Provides unified build() and run_tests() methods
    - Recommends appropriate test frameworks
    - Detects microservices vs monolith architecture
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
        """
        self.project_dir = Path(project_dir) if project_dir else Path.cwd()
        self.logger = logger or logging.getLogger(__name__)

        # Initialize component managers
        self.maven_manager = None
        self.gradle_manager = None

        # Detect build system
        self._detect_and_init_build_system()

    def _detect_and_init_build_system(self):
        """Detect and initialize appropriate build system manager"""
        pom_path = self.project_dir / "pom.xml"
        gradle_path = self.project_dir / "build.gradle"
        gradle_kts_path = self.project_dir / "build.gradle.kts"

        if pom_path.exists():
            self._init_maven_manager()
            return

        if gradle_path.exists() or gradle_kts_path.exists():
            self._init_gradle_manager()

    def _init_maven_manager(self):
        """Initialize Maven manager"""
        try:
            self.maven_manager = MavenManager(
                project_dir=self.project_dir,
                logger=self.logger
            )
            self.logger.info("Detected Maven project")
        except Exception as e:
            self.logger.warning(f"Maven detection failed: {e}")

    def _init_gradle_manager(self):
        """Initialize Gradle manager"""
        try:
            self.gradle_manager = GradleManager(
                project_dir=self.project_dir,
                logger=self.logger
            )
            self.logger.info("Detected Gradle project")
        except Exception as e:
            self.logger.warning(f"Gradle detection failed: {e}")

    def is_java_project(self) -> bool:
        """Check if this is a Java project"""
        return self.maven_manager is not None or self.gradle_manager is not None

    def analyze_project(self) -> JavaEcosystemAnalysis:
        """
        Perform comprehensive Java project analysis.

        Returns:
            JavaEcosystemAnalysis with complete project understanding
        """
        analysis = JavaEcosystemAnalysis(
            build_system="Unknown",
            is_java_project=self.is_java_project()
        )

        if not analysis.is_java_project:
            self.logger.warning("Not a Java project")
            return analysis

        # Analyze build system
        if self.maven_manager:
            analysis.build_system = "Maven"
            analysis.maven_info = self.maven_manager.get_project_info()

        elif self.gradle_manager:
            analysis.build_system = "Gradle"
            analysis.gradle_info = self.gradle_manager.get_project_info()

        # Detect web framework
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
            analysis.is_microservices = analysis.web_framework_analysis.is_microservices

        except Exception as e:
            self.logger.warning(f"Web framework detection failed: {e}")

        # Analyze Spring Boot if detected
        if analysis.is_spring_boot:
            try:
                spring_analyzer = SpringBootAnalyzer(
                    project_dir=self.project_dir,
                    logger=self.logger
                )
                analysis.spring_boot_analysis = spring_analyzer.analyze()

            except Exception as e:
                self.logger.warning(f"Spring Boot analysis failed: {e}")

        # Determine recommended test framework
        analysis.recommended_test_framework = self._recommend_test_framework(analysis)

        # Check for existing tests
        analysis.has_existing_tests = self._check_existing_tests()

        # Build summary
        analysis.summary = self._build_summary(analysis)

        return analysis

    def _recommend_test_framework(self, analysis: JavaEcosystemAnalysis) -> str:
        """Recommend appropriate test framework based on project"""
        # For Java projects, JUnit is the standard
        if not analysis.web_framework_analysis:
            return "junit"

        if "JUnit" in analysis.web_framework_analysis.dependencies:
            return "junit"

        if "TestNG" in analysis.web_framework_analysis.dependencies:
            return "testng"

        # Default to JUnit
        return "junit"

    def _check_existing_tests(self) -> bool:
        """Check if project has existing tests"""
        test_dir = self.project_dir / "src" / "test" / "java"
        if test_dir.exists():
            test_files = list(test_dir.glob("**/*Test.java"))
            return len(test_files) > 0
        return False

    def _build_summary(self, analysis: JavaEcosystemAnalysis) -> Dict[str, str]:
        """Build quick summary of project"""
        summary = {
            "build_system": analysis.build_system,
            "is_java_project": str(analysis.is_java_project),
        }

        self._add_build_info_to_summary(summary, analysis)
        self._add_web_framework_to_summary(summary, analysis)
        self._add_spring_boot_to_summary(summary, analysis)

        summary["recommended_test_framework"] = analysis.recommended_test_framework

        return summary

    def _add_build_info_to_summary(self, summary: Dict[str, str], analysis: JavaEcosystemAnalysis):
        """Add build system info to summary"""
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

    def _add_web_framework_to_summary(self, summary: Dict[str, str], analysis: JavaEcosystemAnalysis):
        """Add web framework info to summary"""
        if not analysis.web_framework_analysis:
            return

        fw = analysis.web_framework_analysis
        summary["framework"] = fw.primary_framework.value
        summary["web_server"] = fw.web_server.value
        summary["has_rest_api"] = str(fw.has_rest_api)

        if fw.databases:
            summary["databases"] = ", ".join(fw.databases)

    def _add_spring_boot_to_summary(self, summary: Dict[str, str], analysis: JavaEcosystemAnalysis):
        """Add Spring Boot info to summary"""
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
        """
        if self.maven_manager:
            return self.maven_manager.build(
                clean=clean,
                skip_tests=skip_tests,
                timeout=timeout
            )

        elif self.gradle_manager:
            return self.gradle_manager.build(
                clean=clean,
                timeout=timeout
            )

        else:
            raise RuntimeError("No build system detected")

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
        """
        if self.maven_manager:
            return self.maven_manager.run_tests(
                test_class=test_class,
                test_method=test_method,
                timeout=timeout
            )

        elif self.gradle_manager:
            return self.gradle_manager.run_tests(
                test_class=test_class,
                test_method=test_method,
                timeout=timeout
            )

        else:
            raise RuntimeError("No build system detected")

    def get_build_system_name(self) -> str:
        """Get build system name"""
        if self.maven_manager:
            return "Maven"
        elif self.gradle_manager:
            return "Gradle"
        return "Unknown"

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
        """
        if self.maven_manager:
            return self.maven_manager.add_dependency(
                group_id, artifact_id, version, scope
            )

        # Gradle dependency addition would require build file parsing/manipulation
        # which is complex. For now, return False for Gradle projects.
        self.logger.warning("Dependency addition not yet supported for Gradle")
        return False


# ============================================================================
# COMMAND-LINE INTERFACE
# ============================================================================

if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(
        description="Java Ecosystem Manager for Artemis"
    )
    parser.add_argument(
        "--project-dir",
        default=".",
        help="Java project directory"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze Java project")
    analyze_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # Build command
    build_parser = subparsers.add_parser("build", help="Build project")
    build_parser.add_argument("--skip-tests", action="store_true", help="Skip tests")
    build_parser.add_argument("--no-clean", action="store_true", help="Don't clean")

    # Test command
    test_parser = subparsers.add_parser("test", help="Run tests")
    test_parser.add_argument("--class", dest="test_class", help="Test class")
    test_parser.add_argument("--method", dest="test_method", help="Test method")

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    # Create manager
    manager = JavaEcosystemManager(project_dir=args.project_dir)

    if not manager.is_java_project():
        print("Error: Not a Java project")
        exit(1)

    # Execute command using dictionary dispatch (Strategy pattern)
    _execute_command(manager, args, parser)


def _execute_command(manager, args, parser):
    """
    Execute CLI command using dictionary dispatch.

    WHY: Avoids if/elif chain by using Strategy pattern with dictionary mapping.
    This follows the Open/Closed principle - new commands can be added by
    registering them in the dispatch table without modifying this function.

    Args:
        manager: JavaEcosystemManager instance
        args: Parsed command-line arguments
        parser: ArgumentParser for help display
    """
    # Command dispatch table (Strategy pattern - avoid if/elif chain)
    COMMAND_HANDLERS = {
        'analyze': _handle_analyze_command,
        'build': _handle_build_command,
        'test': _handle_test_command
    }

    handler = COMMAND_HANDLERS.get(args.command)
    if handler:
        handler(manager, args)
        return

    parser.print_help()


def _handle_analyze_command(manager, args):
    """
    Handle analyze command.

    WHY: Displays comprehensive Java project analysis. Uses early return
    pattern to avoid nesting.

    Args:
        manager: JavaEcosystemManager instance
        args: Command arguments with json flag
    """
    analysis = manager.analyze_project()

    # Early return for JSON output (avoid nesting)
    if args.json:
        print(json.dumps(analysis.summary, indent=2))
        return

    # Default formatted output
    _print_analysis_table(analysis)


def _print_analysis_table(analysis):
    """
    Print formatted analysis table.

    WHY: Extracted to helper method to reduce complexity in command handler.
    Follows Single Responsibility Principle.

    Args:
        analysis: JavaEcosystemAnalysis to display
    """
    print(f"\n{'='*60}")
    print(f"Java Ecosystem Analysis")
    print(f"{'='*60}")

    for key, value in analysis.summary.items():
        print(f"{key:25} {value}")

    print(f"{'='*60}\n")


def _handle_build_command(manager, args):
    """
    Handle build command.

    WHY: Executes project build and displays results. Extracted test
    display logic to helper method to avoid nesting.

    Args:
        manager: JavaEcosystemManager instance
        args: Command arguments with no_clean and skip_tests flags
    """
    result = manager.build(
        clean=not args.no_clean,
        skip_tests=args.skip_tests
    )

    _print_build_result(result, args.skip_tests)


def _print_build_result(result, skip_tests):
    """
    Print build result details.

    WHY: Extracted to helper method to avoid nested if in command handler.
    Follows Single Responsibility Principle.

    Args:
        result: Build result object
        skip_tests: Whether tests were skipped
    """
    print(f"\n{'='*60}")
    print(f"Build Result: {'SUCCESS' if result.success else 'FAILURE'}")
    print(f"{'='*60}")
    print(f"Duration:  {result.duration:.2f}s")
    print(f"Exit Code: {result.exit_code}")

    # Early return if tests were skipped (avoid nesting)
    if skip_tests:
        print(f"{'='*60}\n")
        return

    # Display test results if available
    if hasattr(result, 'tests_run'):
        print(f"Tests:     {result.tests_passed}/{result.tests_run} passed")

    print(f"{'='*60}\n")


def _handle_test_command(manager, args):
    """
    Handle test command.

    WHY: Executes project tests and displays results.

    Args:
        manager: JavaEcosystemManager instance
        args: Command arguments with test_class and test_method
    """
    result = manager.run_tests(
        test_class=args.test_class,
        test_method=args.test_method
    )

    _print_test_result(result)


def _print_test_result(result):
    """
    Print test result details.

    WHY: Extracted to helper method for consistency with other command handlers.
    Follows Single Responsibility Principle.

    Args:
        result: Test result object
    """
    print(f"\n{'='*60}")
    print(f"Test Result: {'SUCCESS' if result.success else 'FAILURE'}")
    print(f"{'='*60}")
    print(f"Tests Run:  {result.tests_run}")
    print(f"Passed:     {result.tests_passed}")
    print(f"Failed:     {result.tests_failed}")
    print(f"Duration:   {result.duration:.2f}s")
    print(f"{'='*60}\n")
