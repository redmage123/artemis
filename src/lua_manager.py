"""
Module: lua_manager.py

BACKWARD COMPATIBILITY WRAPPER

WHY: Maintains existing imports while code is refactored to modular structure
RESPONSIBILITY: Re-export all components from managers.build_managers.lua
PATTERNS: Facade Pattern (backward compatibility)

Original location: /home/bbrelin/src/repos/artemis/src/lua_manager.py (717 lines)
New location: /home/bbrelin/src/repos/artemis/src/managers/build_managers/lua/

Migration status: COMPLETE
- All functionality extracted to modular components
- This file provides backward compatibility
- Update imports to use managers.build_managers.lua directly

Usage:
    # Old import (still works via this wrapper):
    from lua_manager import LuaManager

    # New import (preferred):
    from managers.build_managers.lua import LuaManager
"""

from managers.build_managers.lua import (
    LuaManager,
    LuaVersionDetector,
    LuaRocksPackageManager,
    LuaTestRunner,
    LuaLinter,
    LuaFormatter,
    LuaBuildOperations,
    LuaProjectDetector,
)

# Maintain backward compatibility with registration decorator
from build_manager_factory import register_build_manager, BuildSystem

# Re-register with factory using wrapper
@register_build_manager(BuildSystem.LUA)
class LuaManagerWrapper(LuaManager):
    """Backward compatibility wrapper for LuaManager."""
    pass

# For direct imports
__all__ = [
    "LuaManager",
    "LuaManagerWrapper",
    "LuaVersionDetector",
    "LuaRocksPackageManager",
    "LuaTestRunner",
    "LuaLinter",
    "LuaFormatter",
    "LuaBuildOperations",
    "LuaProjectDetector",
]
