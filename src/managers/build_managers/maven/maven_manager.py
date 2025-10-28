#!/usr/bin/env python3
"""
Module: Maven Manager (Orchestrator)

WHY: Central facade for all Maven operations - delegates to specialized components.
RESPONSIBILITY: Coordinate POM parsing, dependency management, and build execution.
PATTERNS: Facade pattern, Dependency Injection, Composition over Inheritance.

Dependencies: All maven submodules (detector, parser, dependency_manager, build_executor)
"""

from pathlib import Path
from typing import Optional, List
import logging

from .maven_enums import MavenPhase
from .maven_models import MavenProjectInfo, MavenBuildResult
from .maven_detector import MavenDetector
from .pom_parser import PomParser
from .dependency_manager import DependencyManager
from .build_executor import BuildExecutor


class MavenManager:
    """
    Comprehensive Maven build system manager.

    WHY: Provides unified interface to all Maven operations while delegating
         to specialized components for single responsibility.
    RESPONSIBILITY: Coordinate Maven subsystems - detect, parse, build, manage dependencies.

    PATTERNS:
    - Facade pattern: Simplifies complex subsystem (Maven) behind clean interface
    - Composition: Delegates to specialized managers rather than inheritance
    - Dependency Injection: Components injected in constructor

    Architecture:
    - MavenDetector: Installation validation, wrapper detection
    - PomParser: POM.xml parsing and project info extraction
    - DependencyManager: Dependency operations (add, tree, effective POM)
    - BuildExecutor: Build lifecycle execution and test running

    Usage:
        maven = MavenManager(project_dir="/path/to/project")
        info = maven.get_project_info()
        result = maven.build(skip_tests=False)
        maven.add_dependency("org.junit.jupiter", "junit-jupiter", "5.10.0", "test")
    """

    def __init__(
        self,
        project_dir: Optional[Path] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize Maven manager.

        WHY: Set up all components with dependency injection.
        RESPONSIBILITY: Initialize and validate Maven environment.

        Args:
            project_dir: Maven project root directory (defaults to cwd)
            logger: Optional logger for output

        Raises:
            RuntimeError: If Maven is not installed
        """
        self.project_dir = Path(project_dir) if project_dir else Path.cwd()
        self.logger = logger or logging.getLogger(__name__)
        self.pom_path = self.project_dir / "pom.xml"

        # Initialize components (Dependency Injection pattern)
        self.detector = MavenDetector(logger=self.logger)
        self.parser = PomParser(logger=self.logger)
        self.dependency_manager = DependencyManager(
            project_dir=self.project_dir,
            logger=self.logger
        )
        self.build_executor = BuildExecutor(
            project_dir=self.project_dir,
            logger=self.logger
        )

        # Validate Maven installation (fail fast)
        self.detector.validate_maven_installation()
        self.maven_version = self.detector.maven_version

    # ========================================================================
    # PROJECT INFORMATION
    # ========================================================================

    def is_maven_project(self) -> bool:
        """
        Check if directory is a Maven project.

        WHY: Guard clause before Maven operations.
        RESPONSIBILITY: Delegate to detector.

        Returns:
            True if pom.xml exists
        """
        return self.detector.is_maven_project(self.project_dir)

    def get_project_info(self) -> MavenProjectInfo:
        """
        Parse POM and extract comprehensive project information.

        WHY: Central access point for project metadata.
        RESPONSIBILITY: Delegate to POM parser.

        Returns:
            MavenProjectInfo with all project details

        Raises:
            FileNotFoundError: If pom.xml doesn't exist
        """
        return self.parser.parse(self.pom_path)

    # ========================================================================
    # BUILD OPERATIONS
    # ========================================================================

    def build(
        self,
        phase: MavenPhase = MavenPhase.PACKAGE,
        skip_tests: bool = False,
        clean: bool = True,
        offline: bool = False,
        profiles: Optional[List[str]] = None,
        extra_args: Optional[List[str]] = None,
        timeout: int = 600
    ) -> MavenBuildResult:
        """
        Execute Maven build.

        WHY: Primary build interface with flexible configuration.
        RESPONSIBILITY: Delegate to build executor.

        Args:
            phase: Maven lifecycle phase to execute
            skip_tests: Skip test execution
            clean: Run clean before build
            offline: Work offline (use local repository only)
            profiles: Maven profiles to activate
            extra_args: Additional Maven arguments
            timeout: Build timeout in seconds

        Returns:
            MavenBuildResult with build outcome
        """
        return self.build_executor.build(
            phase=phase,
            skip_tests=skip_tests,
            clean=clean,
            offline=offline,
            profiles=profiles,
            extra_args=extra_args,
            timeout=timeout
        )

    def run_tests(
        self,
        test_class: Optional[str] = None,
        test_method: Optional[str] = None,
        timeout: int = 300
    ) -> MavenBuildResult:
        """
        Run Maven tests.

        WHY: Specialized test execution interface.
        RESPONSIBILITY: Delegate to build executor.

        Args:
            test_class: Specific test class to run
            test_method: Specific test method to run
            timeout: Test timeout in seconds

        Returns:
            MavenBuildResult with test results
        """
        return self.build_executor.run_tests(
            test_class=test_class,
            test_method=test_method,
            timeout=timeout
        )

    # ========================================================================
    # DEPENDENCY OPERATIONS
    # ========================================================================

    def add_dependency(
        self,
        group_id: str,
        artifact_id: str,
        version: str,
        scope: str = "compile"
    ) -> bool:
        """
        Add dependency to pom.xml.

        WHY: Programmatic dependency management.
        RESPONSIBILITY: Delegate to dependency manager.

        Args:
            group_id: Dependency group ID
            artifact_id: Dependency artifact ID
            version: Dependency version
            scope: Dependency scope

        Returns:
            True if added successfully
        """
        return self.dependency_manager.add_dependency(
            group_id=group_id,
            artifact_id=artifact_id,
            version=version,
            scope=scope
        )

    def get_dependency_tree(self) -> str:
        """
        Get Maven dependency tree.

        WHY: Visualize and analyze dependencies.
        RESPONSIBILITY: Delegate to dependency manager.

        Returns:
            Dependency tree output
        """
        return self.dependency_manager.get_dependency_tree()

    def get_effective_pom(self) -> str:
        """
        Get effective POM with all inheritance and interpolation resolved.

        WHY: Debug POM inheritance and property substitution.
        RESPONSIBILITY: Delegate to dependency manager.

        Returns:
            Effective POM XML
        """
        return self.dependency_manager.get_effective_pom()
