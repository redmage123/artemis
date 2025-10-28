#!/usr/bin/env python3
"""
WHY: Manage build manager registration
RESPONSIBILITY: Store and validate build manager classes
PATTERNS: Registry (extensible registration)

Registry enables dynamic build manager registration.
"""

from typing import Dict, Type, List
from build_managers.factory.enums import BuildSystem
from build_manager_base import BuildManagerBase


class BuildManagerRegistry:
    """
    Registry for build manager classes.

    WHY: Centralized registration enables extensibility.
    RESPONSIBILITY: Store, validate, and retrieve build manager classes.
    PATTERNS: Registry pattern.
    """

    def __init__(self):
        """Initialize empty registry"""
        self._registry: Dict[BuildSystem, Type[BuildManagerBase]] = {}

    def register(
        self,
        build_system: BuildSystem,
        manager_class: Type[BuildManagerBase]
    ) -> None:
        """
        Register a build manager class.

        WHY: Dynamic registration enables plugin architecture.

        Args:
            build_system: Build system identifier
            manager_class: Build manager class (must extend BuildManagerBase)

        Raises:
            ValueError: If manager_class doesn't extend BuildManagerBase

        Example:
            >>> registry = BuildManagerRegistry()
            >>> registry.register(BuildSystem.MAVEN, MavenManager)
        """
        # Guard clause - validate inheritance
        if not issubclass(manager_class, BuildManagerBase):
            raise ValueError(
                f"{manager_class.__name__} must extend BuildManagerBase"
            )

        self._registry[build_system] = manager_class

    def unregister(self, build_system: BuildSystem) -> None:
        """
        Unregister a build manager.

        WHY: Enables dynamic unloading of build managers.

        Args:
            build_system: Build system to unregister
        """
        # Guard clause - check exists before deleting
        if build_system in self._registry:
            del self._registry[build_system]

    def is_registered(self, build_system: BuildSystem) -> bool:
        """
        Check if build system is registered.

        WHY: Allows caller to check availability before creating.

        Args:
            build_system: Build system to check

        Returns:
            True if registered
        """
        return build_system in self._registry

    def get(self, build_system: BuildSystem) -> Type[BuildManagerBase]:
        """
        Get registered build manager class.

        WHY: Retrieves class for instantiation.

        Args:
            build_system: Build system identifier

        Returns:
            Build manager class

        Raises:
            KeyError: If build system not registered
        """
        return self._registry[build_system]

    def get_registered_systems(self) -> List[BuildSystem]:
        """
        Get list of registered build systems.

        WHY: Enables introspection of available managers.

        Returns:
            List of BuildSystem enums
        """
        return list(self._registry.keys())
