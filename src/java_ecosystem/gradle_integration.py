#!/usr/bin/env python3
"""
Gradle Build System Integration

WHY: Encapsulates Gradle-specific build operations, providing a clean abstraction
     for Gradle project interaction without exposing implementation details.

RESPONSIBILITY:
    - Initialize and manage Gradle build manager
    - Execute Gradle builds with customizable parameters
    - Run Gradle tests with filtering capabilities
    - Extract Gradle project information
    - Detect both build.gradle and build.gradle.kts formats

PATTERNS:
    - Facade pattern - simplifies GradleManager interface
    - Strategy pattern - implements BuildSystemStrategy protocol
    - Guard clauses - early returns to avoid nesting
"""

from pathlib import Path
from typing import Optional, Any
import logging

from gradle_manager import GradleManager, GradleBuildResult, GradleProjectInfo


class GradleIntegration:
    """
    Gradle build system integration.

    WHY: Provides simplified, consistent interface to Gradle operations
         while delegating complex Gradle logic to GradleManager.
    """

    def __init__(
        self,
        project_dir: Path,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize Gradle integration.

        Args:
            project_dir: Project root directory
            logger: Optional logger instance
        """
        self.project_dir = project_dir
        self.logger = logger or logging.getLogger(__name__)
        self.manager: Optional[GradleManager] = None

    def detect_and_initialize(self) -> bool:
        """
        Detect and initialize Gradle if build.gradle or build.gradle.kts exists.

        Returns:
            True if Gradle project detected and initialized

        WHY: Guard clause pattern - early return avoids nesting
        """
        gradle_path = self.project_dir / "build.gradle"
        gradle_kts_path = self.project_dir / "build.gradle.kts"

        if not (gradle_path.exists() or gradle_kts_path.exists()):
            return False

        return self._initialize_manager()

    def _initialize_manager(self) -> bool:
        """
        Initialize Gradle manager.

        Returns:
            True if initialization successful

        WHY: Separated from detection for Single Responsibility Principle
        """
        try:
            self.manager = GradleManager(
                project_dir=self.project_dir,
                logger=self.logger
            )
            self.logger.info("Detected Gradle project")
            return True

        except Exception as e:
            self.logger.warning(f"Gradle detection failed: {e}")
            return False

    def is_available(self) -> bool:
        """
        Check if Gradle manager is available.

        Returns:
            True if manager initialized
        """
        return self.manager is not None

    def get_project_info(self) -> Optional[GradleProjectInfo]:
        """
        Get Gradle project information.

        Returns:
            GradleProjectInfo or None if not available

        WHY: Guard clause avoids AttributeError
        """
        if not self.manager:
            return None

        return self.manager.get_project_info()

    def build(
        self,
        clean: bool = True,
        timeout: int = 600
    ) -> Any:
        """
        Execute Gradle build.

        Args:
            clean: Run clean before build
            timeout: Build timeout in seconds

        Returns:
            GradleBuildResult

        Raises:
            RuntimeError: If Gradle not initialized

        WHY: Guard clause validates preconditions early
        """
        if not self.manager:
            raise RuntimeError("Gradle manager not initialized")

        return self.manager.build(
            clean=clean,
            timeout=timeout
        )

    def run_tests(
        self,
        test_class: Optional[str] = None,
        test_method: Optional[str] = None,
        timeout: int = 300
    ) -> Any:
        """
        Run Gradle tests.

        Args:
            test_class: Specific test class to run
            test_method: Specific test method to run
            timeout: Test timeout in seconds

        Returns:
            Gradle test result

        Raises:
            RuntimeError: If Gradle not initialized

        WHY: Guard clause validates preconditions early
        """
        if not self.manager:
            raise RuntimeError("Gradle manager not initialized")

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
        Add dependency to Gradle project.

        Note: Gradle dependency addition requires build file parsing/manipulation
              which is complex and not yet implemented.

        Args:
            group_id: Dependency group ID
            artifact_id: Dependency artifact ID
            version: Dependency version
            scope: Dependency scope

        Returns:
            False (not yet supported)

        WHY: Placeholder for future implementation, maintains consistent interface
        """
        self.logger.warning("Dependency addition not yet supported for Gradle")
        return False


__all__ = ['GradleIntegration']
