"""
Module: managers.build_managers.lua

WHY: Modular Lua build management system
RESPONSIBILITY: Export all Lua manager components for external use
PATTERNS: Facade Pattern (unified exports)

Components:
- LuaManager: Main orchestrator (implements BuildManagerBase)
- LuaVersionDetector: Lua/LuaJIT version detection
- LuaRocksPackageManager: Package installation and management
- LuaTestRunner: Test execution with busted
- LuaLinter: Static analysis with luacheck
- LuaFormatter: Code formatting with stylua
- LuaBuildOperations: Rock building and artifact management
- LuaProjectDetector: Project detection and metadata extraction
"""

from .manager import LuaManager
from .version_detector import LuaVersionDetector
from .package_manager import LuaRocksPackageManager
from .test_runner import LuaTestRunner
from .linter import LuaLinter
from .formatter import LuaFormatter
from .build_operations import LuaBuildOperations
from .project_detector import LuaProjectDetector

__all__ = [
    "LuaManager",
    "LuaVersionDetector",
    "LuaRocksPackageManager",
    "LuaTestRunner",
    "LuaLinter",
    "LuaFormatter",
    "LuaBuildOperations",
    "LuaProjectDetector",
]
