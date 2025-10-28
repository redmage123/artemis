"""
NPM Build Manager - Data Models

WHY: Encapsulate NPM project configuration and package manager types
RESPONSIBILITY: Define data structures for NPM projects and package managers
PATTERNS: Data Transfer Object, Enum pattern for type safety

This module provides type-safe data structures for NPM project metadata
and package manager identification.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, Any
from enum import Enum


class PackageManager(Enum):
    """
    JavaScript package managers.

    WHY: Type-safe identification of package manager
    PATTERNS: Enum for finite set of valid options
    """
    NPM = "npm"
    YARN = "yarn"
    PNPM = "pnpm"


@dataclass
class NpmProjectInfo:
    """
    NPM/package.json project information.

    WHY: Strongly-typed representation of package.json metadata
    RESPONSIBILITY: Hold and serialize project configuration data
    PATTERNS: Data Transfer Object, Immutable by convention

    This class represents the essential metadata from a package.json file,
    providing type-safe access to project configuration.

    Attributes:
        name: Project name
        version: Project version (semver)
        description: Project description
        dependencies: Production dependencies
        dev_dependencies: Development dependencies
        scripts: NPM scripts (build, test, etc.)
        package_manager: Detected package manager
        engines: Node/NPM version requirements
        license: Project license
        repository: Repository URL
    """
    name: str
    version: str
    description: Optional[str] = None
    dependencies: Dict[str, str] = field(default_factory=dict)
    dev_dependencies: Dict[str, str] = field(default_factory=dict)
    scripts: Dict[str, str] = field(default_factory=dict)
    package_manager: PackageManager = PackageManager.NPM
    engines: Dict[str, str] = field(default_factory=dict)
    license: Optional[str] = None
    repository: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary.

        WHY: Provide serializable representation for JSON/logging
        PATTERNS: Adapter pattern to dict representation

        Returns:
            Dictionary with project information
        """
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "dependencies": self.dependencies,
            "devDependencies": self.dev_dependencies,
            "scripts": self.scripts,
            "packageManager": self.package_manager.value,
            "engines": self.engines,
            "license": self.license,
            "repository": self.repository
        }


__all__ = [
    'PackageManager',
    'NpmProjectInfo'
]
