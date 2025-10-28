"""
Go Modules - Data Models

WHY: Centralize all data structures and enums for Go module operations
RESPONSIBILITY: Define type-safe models for build modes, architectures, and module info
PATTERNS: Data class pattern, enum pattern for type safety
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any


class BuildMode(Enum):
    """
    WHY: Type-safe build mode specification
    RESPONSIBILITY: Define all supported Go build modes
    PATTERNS: Enum pattern for constrained choices
    """
    DEFAULT = ""
    PIE = "-buildmode=pie"
    C_ARCHIVE = "-buildmode=c-archive"
    C_SHARED = "-buildmode=c-shared"
    PLUGIN = "-buildmode=plugin"


class GoArch(Enum):
    """
    WHY: Type-safe architecture specification
    RESPONSIBILITY: Define common Go target architectures
    PATTERNS: Enum pattern for platform targeting
    """
    AMD64 = "amd64"
    ARM64 = "arm64"
    ARM = "arm"
    I386 = "386"


class GoOS(Enum):
    """
    WHY: Type-safe OS specification
    RESPONSIBILITY: Define common Go target operating systems
    PATTERNS: Enum pattern for cross-compilation
    """
    LINUX = "linux"
    DARWIN = "darwin"
    WINDOWS = "windows"
    FREEBSD = "freebsd"


@dataclass
class GoModuleInfo:
    """
    WHY: Structured representation of go.mod contents
    RESPONSIBILITY: Store and serialize module metadata
    PATTERNS: Data class pattern, to_dict for JSON serialization
    """
    module_path: str
    go_version: str
    dependencies: Dict[str, str] = field(default_factory=dict)
    replace_directives: Dict[str, str] = field(default_factory=dict)
    exclude_directives: List[str] = field(default_factory=list)
    has_sum_file: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """
        WHY: Enable JSON serialization of module info
        RESPONSIBILITY: Convert dataclass to dictionary
        PATTERNS: Serialization pattern
        """
        return {
            "modulePath": self.module_path,
            "goVersion": self.go_version,
            "dependencies": self.dependencies,
            "replaceDirectives": self.replace_directives,
            "excludeDirectives": self.exclude_directives,
            "hasSumFile": self.has_sum_file
        }
