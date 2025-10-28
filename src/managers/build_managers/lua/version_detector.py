"""
Module: version_detector.py

WHY: Detects Lua and LuaJIT versions to ensure compatibility with project requirements
RESPONSIBILITY: Version detection and validation for Lua runtimes
PATTERNS: Command Pattern (execute version checks), Guard Clauses (early returns)
"""

import subprocess
from typing import Optional, Dict, Any
from pathlib import Path


class LuaVersionDetector:
    """
    Detects Lua and LuaJIT runtime versions.

    WHY: Different Lua versions have compatibility implications (5.1, 5.2, 5.3, 5.4, LuaJIT)
    RESPONSIBILITY: Query runtime versions, validate compatibility
    """

    def __init__(self, project_path: Path):
        """
        Initialize version detector.

        Args:
            project_path: Root directory of Lua project
        """
        self.project_path = project_path

    def detect_lua_version(self) -> Optional[str]:
        """
        Detect installed Lua version.

        WHY: Projects may require specific Lua versions (5.1 vs 5.3+)

        Returns:
            Version string (e.g., "5.4.4") or None if not found
        """
        if not self._command_exists("lua"):
            return None

        try:
            result = subprocess.run(
                ["lua", "-v"],
                capture_output=True,
                text=True,
                check=False
            )

            # Parse output like "Lua 5.4.4  Copyright (C) 1994-2022 Lua.org, PUC-Rio"
            output = result.stdout or result.stderr
            if "Lua" in output:
                parts = output.split()
                for i, part in enumerate(parts):
                    if part == "Lua" and i + 1 < len(parts):
                        return parts[i + 1]

            return None

        except Exception:
            return None

    def detect_luajit_version(self) -> Optional[str]:
        """
        Detect installed LuaJIT version.

        WHY: LuaJIT is a JIT compiler for Lua 5.1, widely used for performance

        Returns:
            Version string (e.g., "2.1.0-beta3") or None if not found
        """
        if not self._command_exists("luajit"):
            return None

        try:
            result = subprocess.run(
                ["luajit", "-v"],
                capture_output=True,
                text=True,
                check=False
            )

            # Parse output like "LuaJIT 2.1.0-beta3 -- Copyright (C) 2005-2022 Mike Pall."
            output = result.stdout or result.stderr
            if "LuaJIT" in output:
                parts = output.split()
                for i, part in enumerate(parts):
                    if part == "LuaJIT" and i + 1 < len(parts):
                        return parts[i + 1]

            return None

        except Exception:
            return None

    def get_runtime_info(self) -> Dict[str, Any]:
        """
        Get comprehensive runtime information.

        WHY: Provides full runtime context for diagnostics and compatibility checks

        Returns:
            Dict with lua_version, luajit_version, has_lua, has_luajit
        """
        lua_version = self.detect_lua_version()
        luajit_version = self.detect_luajit_version()

        return {
            "lua_version": lua_version,
            "luajit_version": luajit_version,
            "has_lua": lua_version is not None,
            "has_luajit": luajit_version is not None
        }

    def _command_exists(self, command: str) -> bool:
        """
        Check if command exists in PATH.

        Args:
            command: Command name to check

        Returns:
            True if command exists
        """
        try:
            subprocess.run(
                ["which", command],
                capture_output=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError:
            return False
