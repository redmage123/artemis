"""
Module: project_detector.py

WHY: Detects Lua projects and extracts metadata from rockspec files
RESPONSIBILITY: Project detection, rockspec parsing, metadata extraction
PATTERNS: Strategy Pattern (multiple detection methods), Parser Pattern
"""

import re
from typing import Optional, Dict, Any
from pathlib import Path


class LuaProjectDetector:
    """
    Detects Lua projects and parses metadata.

    WHY: Universal build system needs reliable Lua project detection
    RESPONSIBILITY: Detect Lua projects, parse rockspec, extract metadata
    """

    def __init__(self, project_path: Path, logger):
        """
        Initialize project detector.

        Args:
            project_path: Root directory to check
            logger: ArtemisLogger instance
        """
        self.project_path = project_path
        self.logger = logger

    def detect(self) -> bool:
        """
        Detect if directory contains a Lua project.

        WHY: Routes projects to appropriate build manager

        Returns:
            True if Lua project detected

        Detection criteria:
            - *.rockspec file exists
            - src/*.lua files exist
            - init.lua exists
            - .busted config exists
        """
        has_rockspec = self.find_rockspec() is not None
        has_lua_files = len(list(self.project_path.glob("src/*.lua"))) > 0
        has_init = (self.project_path / "init.lua").exists()
        has_busted_config = (self.project_path / ".busted").exists()

        is_lua_project = has_rockspec or has_lua_files or has_init or has_busted_config

        if is_lua_project:
            self.logger.info(f"✅ Detected Lua project at {self.project_path}")
            if has_rockspec:
                rockspec = self.find_rockspec()
                self.logger.info(f"   Rockspec: {rockspec.name}")

        return is_lua_project

    def find_rockspec(self) -> Optional[Path]:
        """
        Find .rockspec file in project directory.

        WHY: Rockspec defines project metadata and dependencies

        Returns:
            Path to rockspec file or None
        """
        rockspecs = list(self.project_path.glob("*.rockspec"))
        return rockspecs[0] if rockspecs else None

    def get_project_info(self) -> Dict[str, Any]:
        """
        Extract project metadata from rockspec.

        WHY: Provides project details for reporting

        Returns:
            Dict with name, version, description
        """
        rockspec_file = self.find_rockspec()

        if not rockspec_file:
            return {
                "name": "unknown",
                "version": "unknown",
                "description": "No rockspec found"
            }

        try:
            content = rockspec_file.read_text()
            return self._parse_rockspec_metadata(content)

        except Exception as e:
            self.logger.warning(f"Failed to parse rockspec: {e}")
            return {
                "name": "unknown",
                "version": "unknown",
                "description": "Parse error"
            }

    def _parse_rockspec_metadata(self, content: str) -> Dict[str, Any]:
        """
        Parse rockspec metadata using regex.

        WHY: Rockspec is Lua code, regex is simpler than Lua parser

        Args:
            content: Rockspec file content

        Returns:
            Dict with name, version, description
        """
        name_match = re.search(r'package\s*=\s*["\']([^"\']+)["\']', content)
        version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
        desc_match = re.search(r'description\s*=\s*{[^}]*summary\s*=\s*["\']([^"\']+)["\']', content)

        return {
            "name": name_match.group(1) if name_match else "unknown",
            "version": version_match.group(1) if version_match else "unknown",
            "description": desc_match.group(1) if desc_match else "Lua project"
        }
