#!/usr/bin/env python3
"""
WHY: Provide decorator for auto-registration
RESPONSIBILITY: Simplify build manager registration
PATTERNS: Decorator (class modification)

Registration decorator enables declarative manager registration.
"""

from typing import Type
from build_managers.factory.enums import BuildSystem
from build_manager_base import BuildManagerBase


def register_build_manager(build_system: BuildSystem):
    """
    Decorator to auto-register build managers.

    WHY: Declarative registration at class definition time.
    PATTERNS: Decorator pattern.

    Args:
        build_system: Build system identifier

    Returns:
        Decorator function

    Example:
        @register_build_manager(BuildSystem.MAVEN)
        class MavenManager(BuildManagerBase):
            ...
    """
    def decorator(cls: Type[BuildManagerBase]):
        """Inner decorator function"""
        from build_managers.factory.factory import BuildManagerFactory

        # Register class with factory
        BuildManagerFactory.get_instance().register(build_system, cls)
        return cls

    return decorator
