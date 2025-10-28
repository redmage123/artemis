#!/usr/bin/env python3
"""
Java Dependency Resolution

WHY: Provides unified dependency management across Maven and Gradle projects,
     abstracting away build-system-specific dependency formats.

RESPONSIBILITY:
    - Add dependencies to Java projects regardless of build system
    - Normalize dependency specifications across Maven/Gradle
    - Validate dependency parameters before addition
    - Provide feedback on dependency addition success/failure

PATTERNS:
    - Strategy pattern - delegates to appropriate build system
    - Guard clauses - validate inputs early
    - Single Responsibility - focuses only on dependency management
"""

from typing import Optional, Callable
import logging


class DependencyResolver:
    """
    Unified dependency resolution for Java projects.

    WHY: Centralizes dependency management logic, providing consistent
         interface regardless of underlying build system (Maven/Gradle).
    """

    def __init__(
        self,
        maven_add_dependency: Optional[Callable] = None,
        gradle_add_dependency: Optional[Callable] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize dependency resolver.

        Args:
            maven_add_dependency: Maven dependency addition function
            gradle_add_dependency: Gradle dependency addition function
            logger: Optional logger instance

        WHY: Dependency injection allows testing and flexibility
        """
        self.maven_add_dependency = maven_add_dependency
        self.gradle_add_dependency = gradle_add_dependency
        self.logger = logger or logging.getLogger(__name__)

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
            scope: Dependency scope (compile, test, provided, runtime)

        Returns:
            True if dependency added successfully

        WHY: Strategy pattern - delegates to appropriate build system handler
        """
        # Guard clause: validate inputs
        if not self._validate_dependency_params(group_id, artifact_id, version):
            return False

        # Try Maven first
        if self.maven_add_dependency:
            return self._add_maven_dependency(
                group_id, artifact_id, version, scope
            )

        # Fall back to Gradle
        if self.gradle_add_dependency:
            return self._add_gradle_dependency(
                group_id, artifact_id, version, scope
            )

        # No build system available
        self.logger.error("No build system available for dependency addition")
        return False

    def _validate_dependency_params(
        self,
        group_id: str,
        artifact_id: str,
        version: str
    ) -> bool:
        """
        Validate dependency parameters.

        Args:
            group_id: Dependency group ID
            artifact_id: Dependency artifact ID
            version: Dependency version

        Returns:
            True if parameters valid

        WHY: Guard clause - fail fast on invalid input
        """
        if not group_id or not group_id.strip():
            self.logger.error("Invalid group_id: cannot be empty")
            return False

        if not artifact_id or not artifact_id.strip():
            self.logger.error("Invalid artifact_id: cannot be empty")
            return False

        if not version or not version.strip():
            self.logger.error("Invalid version: cannot be empty")
            return False

        return True

    def _add_maven_dependency(
        self,
        group_id: str,
        artifact_id: str,
        version: str,
        scope: str
    ) -> bool:
        """
        Add dependency via Maven.

        Args:
            group_id: Dependency group ID
            artifact_id: Dependency artifact ID
            version: Dependency version
            scope: Dependency scope

        Returns:
            True if successful
        """
        try:
            result = self.maven_add_dependency(
                group_id, artifact_id, version, scope
            )
            if result:
                self.logger.info(
                    f"Added Maven dependency: {group_id}:{artifact_id}:{version}"
                )
            return result

        except Exception as e:
            self.logger.error(f"Maven dependency addition failed: {e}")
            return False

    def _add_gradle_dependency(
        self,
        group_id: str,
        artifact_id: str,
        version: str,
        scope: str
    ) -> bool:
        """
        Add dependency via Gradle.

        Args:
            group_id: Dependency group ID
            artifact_id: Dependency artifact ID
            version: Dependency version
            scope: Dependency scope

        Returns:
            True if successful

        WHY: Separated for consistency, even though Gradle not yet supported
        """
        try:
            result = self.gradle_add_dependency(
                group_id, artifact_id, version, scope
            )
            if result:
                self.logger.info(
                    f"Added Gradle dependency: {group_id}:{artifact_id}:{version}"
                )
            return result

        except Exception as e:
            self.logger.error(f"Gradle dependency addition failed: {e}")
            return False

    def is_available(self) -> bool:
        """
        Check if dependency resolution is available.

        Returns:
            True if at least one build system handler available
        """
        return (
            self.maven_add_dependency is not None or
            self.gradle_add_dependency is not None
        )


__all__ = ['DependencyResolver']
