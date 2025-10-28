#!/usr/bin/env python3
"""
Composer Models and Data Structures

WHY: Centralized type definitions for Composer operations
RESPONSIBILITY: Define enums, dataclasses, and type structures for Composer
PATTERNS:
- Dataclass pattern for structured data
- Enum pattern for type-safe constants
- Immutable data structures where possible
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional, Any


class DependencyType(Enum):
    """
    Composer dependency types.

    WHY: Type-safe dependency classification
    RESPONSIBILITY: Distinguish between production and development dependencies
    """
    REQUIRE = "require"
    REQUIRE_DEV = "require-dev"


class StabilityFlag(Enum):
    """
    Package stability flags.

    WHY: Type-safe stability level specification
    RESPONSIBILITY: Define allowed package stability levels in dependency resolution
    """
    STABLE = "stable"
    RC = "RC"
    BETA = "beta"
    ALPHA = "alpha"
    DEV = "dev"


@dataclass
class ComposerProjectInfo:
    """
    Composer project information from composer.json.

    WHY: Structured representation of composer.json contents
    RESPONSIBILITY: Provide type-safe access to project metadata and configuration
    PATTERNS: Dataclass with default factories for mutable defaults
    """
    name: str
    description: Optional[str] = None
    type: str = "library"
    license: Optional[str] = None
    php_version: str = ">=7.0"
    require: Dict[str, str] = field(default_factory=dict)
    require_dev: Dict[str, str] = field(default_factory=dict)
    autoload: Dict[str, Any] = field(default_factory=dict)
    scripts: Dict[str, Any] = field(default_factory=dict)
    has_lock_file: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation.

        WHY: Enable JSON serialization and API responses
        RESPONSIBILITY: Transform dataclass to dict with camelCase keys

        Returns:
            Dictionary with camelCase keys for consistency
        """
        return {
            "name": self.name,
            "description": self.description,
            "type": self.type,
            "license": self.license,
            "phpVersion": self.php_version,
            "require": self.require,
            "requireDev": self.require_dev,
            "autoload": self.autoload,
            "scripts": self.scripts,
            "hasLockFile": self.has_lock_file
        }
