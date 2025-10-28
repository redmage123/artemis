"""
Poetry Build Manager - Data Models

WHY: Centralize Poetry-specific data structures and enums
RESPONSIBILITY: Define domain models for Poetry project configuration
PATTERNS: Dataclass pattern for immutable data structures, Enum for type safety

This module contains all Poetry-specific data models including dependency groups,
project information structures, and configuration representations.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional, List, Any


class DependencyGroup(Enum):
    """
    Poetry dependency groups.

    WHY: Type-safe enumeration for dependency categorization
    PATTERNS: Enum pattern for constrained value sets
    """
    MAIN = "main"
    DEV = "dev"
    TEST = "test"
    DOCS = "docs"


@dataclass
class PoetryProjectInfo:
    """
    Poetry pyproject.toml project information.

    WHY: Structured representation of Poetry project metadata
    RESPONSIBILITY: Encapsulate all Poetry project configuration data
    PATTERNS: Dataclass with factory defaults, immutable by convention

    Attributes:
        name: Project name
        version: Project version (semver)
        description: Project description
        authors: List of author strings
        license: License identifier
        readme: README file path
        python_version: Required Python version constraint
        dependencies: Production dependencies
        dev_dependencies: Development dependencies
        scripts: Executable scripts defined in project
        has_lock_file: Whether poetry.lock exists
    """
    name: str
    version: str
    description: Optional[str] = None
    authors: List[str] = field(default_factory=list)
    license: Optional[str] = None
    readme: Optional[str] = None
    python_version: str = "^3.8"
    dependencies: Dict[str, Any] = field(default_factory=dict)
    dev_dependencies: Dict[str, Any] = field(default_factory=dict)
    scripts: Dict[str, str] = field(default_factory=dict)
    has_lock_file: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation.

        WHY: Enable JSON serialization and API responses
        RETURNS: Dictionary with camelCase keys for frontend compatibility
        """
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "authors": self.authors,
            "license": self.license,
            "readme": self.readme,
            "pythonVersion": self.python_version,
            "dependencies": self.dependencies,
            "devDependencies": self.dev_dependencies,
            "scripts": self.scripts,
            "hasLockFile": self.has_lock_file
        }


__all__ = [
    'DependencyGroup',
    'PoetryProjectInfo'
]
