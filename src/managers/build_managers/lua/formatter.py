"""
Module: formatter.py

WHY: Formats Lua code using stylua for consistent code style
RESPONSIBILITY: Format Lua files, report formatting results
PATTERNS: Command Pattern (execute formatting), Guard Clauses
"""

import subprocess
from typing import Dict, Any, List
from pathlib import Path


class LuaFormatter:
    """
    Formats Lua code using stylua.

    WHY: Consistent formatting improves readability and reduces diff noise
    RESPONSIBILITY: Execute stylua, collect formatted files, report results
    """

    def __init__(self, project_path: Path, logger):
        """
        Initialize formatter.

        Args:
            project_path: Root directory of Lua project
            logger: ArtemisLogger instance
        """
        self.project_path = project_path
        self.logger = logger

    def format_code(self) -> Dict[str, Any]:
        """
        Format Lua code using stylua.

        WHY: Consistent formatting improves code quality and maintainability

        Returns:
            Dict with success, files_formatted, message
        """
        if not self._is_stylua_available():
            self.logger.warning("⚠️  stylua not found, skipping formatting")
            return {
                "success": False,
                "files_formatted": 0,
                "message": "stylua not installed"
            }

        self.logger.info("✨ Formatting Lua code with stylua...")

        lua_files = self._find_lua_files()

        if not lua_files:
            return {
                "success": True,
                "files_formatted": 0,
                "message": "No Lua files found"
            }

        try:
            subprocess.run(
                ["stylua"] + [str(f) for f in lua_files],
                cwd=self.project_path,
                capture_output=True,
                check=True
            )

            self.logger.info(f"✅ Formatted {len(lua_files)} files")
            return {
                "success": True,
                "files_formatted": len(lua_files),
                "message": f"Formatted {len(lua_files)} Lua files"
            }

        except subprocess.CalledProcessError as e:
            self.logger.error(f"❌ Formatting failed: {e.stderr}")
            return {
                "success": False,
                "files_formatted": 0,
                "message": f"Formatting error: {e.stderr}"
            }

    def _find_lua_files(self) -> List[Path]:
        """
        Find all Lua files in project.

        Returns:
            List of .lua file paths
        """
        return list(self.project_path.rglob("*.lua"))

    def _is_stylua_available(self) -> bool:
        """
        Check if stylua is available.

        Returns:
            True if stylua command exists
        """
        try:
            subprocess.run(
                ["which", "stylua"],
                capture_output=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError:
            return False
