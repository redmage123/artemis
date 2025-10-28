"""
Module: build_operations.py

WHY: Manages Lua rock building and artifact creation using LuaRocks
RESPONSIBILITY: Build rocks, clean artifacts, manage build lifecycle
PATTERNS: Command Pattern (execute builds), Guard Clauses
"""

import subprocess
import shutil
from typing import Dict, Any, Optional, List
from pathlib import Path


class LuaBuildOperations:
    """
    Manages Lua rock build operations.

    WHY: LuaRocks packages (rocks) need to be built for distribution
    RESPONSIBILITY: Execute builds, clean artifacts, manage build outputs
    """

    def __init__(self, project_path: Path, logger):
        """
        Initialize build operations.

        Args:
            project_path: Root directory of Lua project
            logger: ArtemisLogger instance
        """
        self.project_path = project_path
        self.logger = logger

    def build_rock(self, rockspec_file: Optional[Path]) -> Dict[str, Any]:
        """
        Build Lua rock using LuaRocks pack.

        WHY: Creates distributable .rock file for installation

        Args:
            rockspec_file: Path to .rockspec file

        Returns:
            Dict with success, artifact_path, message, duration
        """
        if not rockspec_file:
            return {
                "success": False,
                "artifact_path": None,
                "message": "No rockspec file found",
                "duration": 0.0
            }

        if not rockspec_file.exists():
            return {
                "success": False,
                "artifact_path": None,
                "message": f"Rockspec not found: {rockspec_file}",
                "duration": 0.0
            }

        self.logger.info("🔨 Building Lua rock...")

        try:
            result = subprocess.run(
                ["luarocks", "pack", str(rockspec_file)],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                check=True
            )

            # Find generated .rock file
            rock_files = list(self.project_path.glob("*.rock"))
            artifact = str(rock_files[0]) if rock_files else None

            message = f"Built {Path(artifact).name if artifact else 'rock'}"
            self.logger.info(f"✅ {message}")

            return {
                "success": True,
                "artifact_path": artifact,
                "message": message,
                "stdout": result.stdout
            }

        except subprocess.CalledProcessError as e:
            error_msg = f"Build error: {e.stderr}"
            self.logger.error(f"❌ {error_msg}")

            return {
                "success": False,
                "artifact_path": None,
                "message": error_msg,
                "stderr": e.stderr
            }

    def clean(self) -> Dict[str, Any]:
        """
        Clean build artifacts and cache.

        WHY: Removes build artifacts for fresh builds

        Returns:
            Dict with success, artifacts_removed, message
        """
        self.logger.info("🧹 Cleaning Lua artifacts...")

        try:
            artifacts_removed = 0

            # Remove .rock files
            rock_files = list(self.project_path.glob("*.rock"))
            for rock in rock_files:
                rock.unlink()
                artifacts_removed += 1

            # Remove luarocks build directory
            build_dir = self.project_path / ".luarocks"
            if build_dir.exists():
                shutil.rmtree(build_dir)
                artifacts_removed += 1

            self.logger.info(f"✅ Cleaned {artifacts_removed} artifacts")
            return {
                "success": True,
                "artifacts_removed": artifacts_removed,
                "message": f"Cleaned {artifacts_removed} build artifacts"
            }

        except Exception as e:
            self.logger.error(f"❌ Clean failed: {e}")
            return {
                "success": False,
                "artifacts_removed": 0,
                "message": f"Clean error: {e}"
            }

    def find_artifacts(self) -> List[Path]:
        """
        Find all build artifacts.

        WHY: Useful for listing outputs and diagnostics

        Returns:
            List of artifact paths (.rock files)
        """
        return list(self.project_path.glob("*.rock"))

    def validate_rockspec(self, rockspec_file: Path) -> Dict[str, Any]:
        """
        Validate rockspec file syntax.

        WHY: Catch rockspec errors before build attempts

        Args:
            rockspec_file: Path to .rockspec file

        Returns:
            Dict with valid (bool) and message
        """
        if not rockspec_file.exists():
            return {
                "valid": False,
                "message": f"Rockspec not found: {rockspec_file}"
            }

        try:
            # Use luarocks lint to validate
            result = subprocess.run(
                ["luarocks", "lint", str(rockspec_file)],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                check=False
            )

            # Exit code 0 means valid
            valid = result.returncode == 0

            return {
                "valid": valid,
                "message": result.stdout if valid else result.stderr
            }

        except Exception as e:
            return {
                "valid": False,
                "message": f"Validation error: {e}"
            }
