#!/usr/bin/env python3
"""
WHY: Define data structures for CMake build management
RESPONSIBILITY: Immutable models for generators, build types, and project info
PATTERNS: Value Object (immutable dataclasses), Enum (type safety)

CMake models provide type-safe representations of CMake concepts.
"""

from pathlib import Path
from typing import List, Any, Dict
from dataclasses import dataclass
from enum import Enum


class CMakeGenerator(Enum):
    """
    CMake generators.

    WHY: Type-safe generator selection prevents typos and invalid generators.
    """
    UNIX_MAKEFILES = "Unix Makefiles"
    NINJA = "Ninja"
    VISUAL_STUDIO = "Visual Studio"
    XCODE = "Xcode"


class BuildType(Enum):
    """
    CMake build types.

    WHY: Standard build configurations with compile/link flags.
    """
    DEBUG = "Debug"
    RELEASE = "Release"
    REL_WITH_DEB_INFO = "RelWithDebInfo"
    MIN_SIZE_REL = "MinSizeRel"


@dataclass
class CMakeProjectInfo:
    """
    CMake project information.

    WHY: Structured representation of project metadata from CMakeLists.txt.
    PATTERNS: Value Object (immutable data structure).
    """
    project_name: str
    version: str
    languages: List[str]
    build_dir: Path
    source_dir: Path
    generator: str
    build_type: str

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary.

        WHY: JSON serialization for API responses and logging.

        Returns:
            Dictionary representation

        Example:
            >>> info = CMakeProjectInfo(
            ...     project_name="MyApp",
            ...     version="1.0.0",
            ...     languages=["C", "CXX"],
            ...     build_dir=Path("build"),
            ...     source_dir=Path("."),
            ...     generator="Unix Makefiles",
            ...     build_type="Release"
            ... )
            >>> info.to_dict()["name"]
            'MyApp'
        """
        return {
            "name": self.project_name,
            "version": self.version,
            "languages": self.languages,
            "buildDir": str(self.build_dir),
            "sourceDir": str(self.source_dir),
            "generator": self.generator,
            "buildType": self.build_type
        }
