#!/usr/bin/env python3
"""
WHY: Create build manager instances dynamically
RESPONSIBILITY: Factory with singleton and auto-detection
PATTERNS: Factory, Singleton, Registry

BuildManagerFactory enables dynamic creation of build managers.
"""

from typing import Optional
from pathlib import Path
import logging

from artemis_exceptions import wrap_exception
from build_system_exceptions import UnsupportedBuildSystemError
from build_manager_base import BuildManagerBase
from build_managers.factory.enums import BuildSystem
from build_managers.factory.registry import BuildManagerRegistry
from build_managers.factory.detector import BuildSystemDetector


class BuildManagerFactory:
    """
    Factory for creating build managers.

    WHY: Centralizes build manager creation with auto-detection.
    RESPONSIBILITY: Create managers, manage registry, detect build systems.
    PATTERNS: Factory, Singleton, Registry.

    Example:
        factory = BuildManagerFactory.get_instance()
        maven_mgr = factory.create(BuildSystem.MAVEN, project_dir="/path")
    """

    _instance: Optional['BuildManagerFactory'] = None

    def __new__(cls):
        """
        Singleton: Ensure only one factory instance.

        WHY: Single registry ensures consistent manager availability.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._registry = BuildManagerRegistry()
        return cls._instance

    @classmethod
    def get_instance(cls) -> 'BuildManagerFactory':
        """
        Get singleton factory instance.

        WHY: Singleton access pattern.

        Returns:
            BuildManagerFactory instance
        """
        if cls._instance is None:
            cls._instance = BuildManagerFactory()
        return cls._instance

    def register(
        self,
        build_system: BuildSystem,
        manager_class: type[BuildManagerBase]
    ) -> None:
        """
        Register a build manager class.

        WHY: Delegates to registry for separation of concerns.

        Args:
            build_system: Build system identifier
            manager_class: Build manager class

        Raises:
            ValueError: If manager_class doesn't extend BuildManagerBase
        """
        self._registry.register(build_system, manager_class)

    def unregister(self, build_system: BuildSystem) -> None:
        """Unregister a build manager"""
        self._registry.unregister(build_system)

    def is_registered(self, build_system: BuildSystem) -> bool:
        """Check if build system is registered"""
        return self._registry.is_registered(build_system)

    def get_registered_systems(self) -> list[BuildSystem]:
        """Get list of registered build systems"""
        return self._registry.get_registered_systems()

    @wrap_exception(UnsupportedBuildSystemError, "Failed to create build manager")
    def create(
        self,
        build_system: BuildSystem,
        project_dir: Optional[Path] = None,
        logger: Optional[logging.Logger] = None
    ) -> BuildManagerBase:
        """
        Create a build manager instance.

        WHY: Factory method for consistent manager creation.

        Args:
            build_system: Build system to use
            project_dir: Project directory
            logger: Logger instance (dependency injection)

        Returns:
            Build manager instance

        Raises:
            UnsupportedBuildSystemError: If build system not registered

        Example:
            factory = BuildManagerFactory.get_instance()
            maven = factory.create(BuildSystem.MAVEN, project_dir="/path")
        """
        # Guard clause - check registration
        if not self._registry.is_registered(build_system):
            registered = [bs.value for bs in self._registry.get_registered_systems()]
            raise UnsupportedBuildSystemError(
                f"Build system '{build_system.value}' not registered",
                {
                    "requested": build_system.value,
                    "registered": registered
                }
            )

        manager_class = self._registry.get(build_system)

        try:
            return manager_class(
                project_dir=project_dir,
                logger=logger
            )
        except Exception as e:
            raise UnsupportedBuildSystemError(
                f"Failed to create {build_system.value} manager: {e}",
                {
                    "build_system": build_system.value,
                    "manager_class": manager_class.__name__,
                    "error": str(e)
                },
                original_exception=e
            )

    def create_auto(
        self,
        project_dir: Optional[Path] = None,
        logger: Optional[logging.Logger] = None
    ) -> BuildManagerBase:
        """
        Auto-detect and create appropriate build manager.

        WHY: Zero-config usage improves developer experience.

        Args:
            project_dir: Project directory
            logger: Logger instance

        Returns:
            Build manager instance

        Raises:
            UnsupportedBuildSystemError: If no build system detected

        Example:
            factory = BuildManagerFactory.get_instance()
            manager = factory.create_auto(project_dir="/path/to/project")
        """
        project_path = Path(project_dir) if project_dir else Path.cwd()

        # Detect build system
        detected = BuildSystemDetector.detect(
            project_path,
            self._registry.get_registered_systems()
        )

        # Guard clause - no build system detected
        if not detected:
            raise UnsupportedBuildSystemError(
                "No build system detected in project",
                {
                    "project_dir": str(project_path),
                    "registered_systems": [bs.value for bs in self.get_registered_systems()]
                }
            )

        return self.create(detected, project_dir, logger)


def get_build_manager_factory() -> BuildManagerFactory:
    """
    Get the build manager factory instance.

    WHY: Convenience function for singleton access.

    Returns:
        BuildManagerFactory singleton

    Example:
        factory = get_build_manager_factory()
        maven = factory.create(BuildSystem.MAVEN)
    """
    return BuildManagerFactory.get_instance()
