"""
Module: managers/build_managers/cargo/models.py

WHY: Data models and enums for Cargo build system.
RESPONSIBILITY: Define build profiles, cargo features, and project information structures.
PATTERNS: Value Object Pattern, Enum Pattern, Dataclass Pattern.

This module contains:
- BuildProfile enum (DEBUG, RELEASE)
- CargoFeature enum (DEFAULT, FULL, MINIMAL)
- CargoProjectInfo dataclass for Cargo.toml data

EXTRACTED FROM: cargo_manager.py (lines 32-77)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class BuildProfile(Enum):
    """Cargo build profiles"""
    DEBUG = "debug"
    RELEASE = "release"


class CargoFeature(Enum):
    """Common Cargo features"""
    DEFAULT = "default"
    FULL = "full"
    MINIMAL = "minimal"


@dataclass
class CargoProjectInfo:
    """
    Cargo.toml project information.

    WHY: Encapsulate all Cargo project metadata in a single structure.
    RESPONSIBILITY: Store and convert Cargo project configuration.
    """
    name: str
    version: str
    edition: str  # 2015, 2018, 2021
    authors: List[str] = field(default_factory=list)
    description: Optional[str] = None
    license: Optional[str] = None
    repository: Optional[str] = None
    dependencies: Dict[str, Any] = field(default_factory=dict)
    dev_dependencies: Dict[str, Any] = field(default_factory=dict)
    features: Dict[str, List[str]] = field(default_factory=dict)
    workspace_members: List[str] = field(default_factory=list)
    is_workspace: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary.

        Returns:
            Dict with camelCase keys for API consistency
        """
        return {
            "name": self.name,
            "version": self.version,
            "edition": self.edition,
            "authors": self.authors,
            "description": self.description,
            "license": self.license,
            "repository": self.repository,
            "dependencies": self.dependencies,
            "devDependencies": self.dev_dependencies,
            "features": self.features,
            "workspaceMembers": self.workspace_members,
            "isWorkspace": self.is_workspace
        }


__all__ = [
    "BuildProfile",
    "CargoFeature",
    "CargoProjectInfo",
]
