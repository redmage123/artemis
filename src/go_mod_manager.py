#!/usr/bin/env python3
"""
Go Modules Build Manager - Backward Compatibility Wrapper

WHY: Maintain backward compatibility during migration to modular structure
RESPONSIBILITY: Re-export all components from build_managers.go_mod
PATTERNS: Facade pattern, module aliasing, transparent migration

MIGRATION NOTE: This file provides backward compatibility.
New code should import from: build_managers.go_mod
Example:
    from build_managers.go_mod import GoModManager, BuildMode, GoArch
"""

# Re-export all public components
from build_managers.go_mod.models import (
    BuildMode,
    GoArch,
    GoOS,
    GoModuleInfo
)
from build_managers.go_mod.parser import GoModParser
from build_managers.go_mod.dependency_manager import GoDependencyManager
from build_managers.go_mod.build_operations import GoBuildOperations
from build_managers.go_mod.version_detector import GoVersionDetector
from build_managers.go_mod.manager import GoModManager

__all__ = [
    'BuildMode',
    'GoArch',
    'GoOS',
    'GoModuleInfo',
    'GoModParser',
    'GoDependencyManager',
    'GoBuildOperations',
    'GoVersionDetector',
    'GoModManager'
]

# CLI interface for backward compatibility
if __name__ == "__main__":
    from build_managers.go_mod.cli import main
    main()
