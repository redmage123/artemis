#!/usr/bin/env python3
"""
Maven Build System Integration

WHY: Encapsulates Maven-specific build operations, providing a clean abstraction
     for Maven project interaction without exposing implementation details.

RESPONSIBILITY:
    - Initialize and manage Maven build manager
    - Execute Maven builds with customizable parameters
    - Run Maven tests with filtering capabilities
    - Add dependencies to Maven projects
    - Extract Maven project information

PATTERNS:
    - Facade pattern - simplifies MavenManager interface
    - Strategy pattern - implements BuildSystemStrategy protocol
    - Guard clauses - early returns to avoid nesting
"""

from pathlib import Path
from typing import Optional, Any
import logging

from maven_manager import MavenManager, MavenBuildResult, MavenProjectInfo


class MavenIntegration:
    """
    Maven build system integration.

    WHY: Provides simplified, consistent interface to Maven operations
         while delegating complex Maven logic to MavenManager.
    """

    def __init__(
        self,
        project_dir: Path,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize Maven integration.

        Args:
            project_dir: Project root directory
            logger: Optional logger instance
        """
        self.project_dir = project_dir
        self.logger = logger or logging.getLogger(__name__)
        self.manager: Optional[MavenManager] = None

    def detect_and_initialize(self) -> bool:
        """
        Detect and initialize Maven if pom.xml exists.

        Returns:
            True if Maven project detected and initialized

        WHY: Guard clause pattern - early return avoids nesting
        """
        pom_path = self.project_dir / "pom.xml"
        if not pom_path.exists():
            return False

        return self._initialize_manager()

    def _initialize_manager(self) -> bool:
        """
        Initialize Maven manager.

        Returns:
            True if initialization successful

        WHY: Separated from detection for Single Responsibility Principle
        """
        try:
            self.manager = MavenManager(
                project_dir=self.project_dir,
                logger=self.logger
            )
            self.logger.info("Detected Maven project")
            return True

        except Exception as e:
            self.logger.warning(f"Maven detection failed: {e}")
            return False

    def is_available(self) -> bool:
        """
        Check if Maven manager is available.

        Returns:
            True if manager initialized
        """
        return self.manager is not None

    def get_project_info(self) -> Optional[MavenProjectInfo]:
        """
        Get Maven project information.

        Returns:
            MavenProjectInfo or None if not available

        WHY: Guard clause avoids AttributeError
        """
        if not self.manager:
            return None

        return self.manager.get_project_info()

    def build(
        self,
        clean: bool = True,
        skip_tests: bool = False,
        timeout: int = 600
    ) -> Any:
        """
        Execute Maven build.

        Args:
            clean: Run clean before build
            skip_tests: Skip test execution
            timeout: Build timeout in seconds

        Returns:
            MavenBuildResult

        Raises:
            RuntimeError: If Maven not initialized

        WHY: Guard clause validates preconditions early
        """
        if not self.manager:
            raise RuntimeError("Maven manager not initialized")

        return self.manager.build(
            clean=clean,
            skip_tests=skip_tests,
            timeout=timeout
        )

    def run_tests(
        self,
        test_class: Optional[str] = None,
        test_method: Optional[str] = None,
        timeout: int = 300
    ) -> Any:
        """
        Run Maven tests.

        Args:
            test_class: Specific test class to run
            test_method: Specific test method to run
            timeout: Test timeout in seconds

        Returns:
            Maven test result

        Raises:
            RuntimeError: If Maven not initialized

        WHY: Guard clause validates preconditions early
        """
        if not self.manager:
            raise RuntimeError("Maven manager not initialized")

        return self.manager.run_tests(
            test_class=test_class,
            test_method=test_method,
            timeout=timeout
        )

    def add_dependency(
        self,
        group_id: str,
        artifact_id: str,
        version: str,
        scope: str = "compile"
    ) -> bool:
        """
        Add dependency to Maven project.

        Args:
            group_id: Dependency group ID
            artifact_id: Dependency artifact ID
            version: Dependency version
            scope: Dependency scope

        Returns:
            True if dependency added successfully

        WHY: Guard clause ensures manager available before operation
        """
        if not self.manager:
            self.logger.warning("Maven manager not initialized")
            return False

        return self.manager.add_dependency(
            group_id, artifact_id, version, scope
        )


__all__ = ['MavenIntegration']
