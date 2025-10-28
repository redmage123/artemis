"""
Module: package_manager.py

WHY: Manages LuaRocks package installation and dependency resolution
RESPONSIBILITY: Install rocks, parse dependencies, manage package operations
PATTERNS: Command Pattern (execute package operations), Parser Pattern (extract deps)
"""

import subprocess
from typing import List, Dict, Any, Optional
from pathlib import Path


class LuaRocksPackageManager:
    """
    Manages LuaRocks package operations.

    WHY: LuaRocks is the standard Lua package manager (like npm for Node.js)
    RESPONSIBILITY: Install packages, parse installation output, manage dependencies
    """

    def __init__(self, project_path: Path, logger):
        """
        Initialize package manager.

        Args:
            project_path: Root directory of Lua project
            logger: ArtemisLogger instance
        """
        self.project_path = project_path
        self.logger = logger

    def install_from_rockspec(self, rockspec_file: Path) -> Dict[str, Any]:
        """
        Install dependencies from rockspec file.

        WHY: Rockspec files define project dependencies (like package.json)

        Args:
            rockspec_file: Path to .rockspec file

        Returns:
            Dict with success, installed_count, message, dependencies
        """
        if not rockspec_file.exists():
            return {
                "success": False,
                "installed_count": 0,
                "message": f"Rockspec not found: {rockspec_file}",
                "dependencies": []
            }

        try:
            result = subprocess.run(
                ["luarocks", "make", str(rockspec_file)],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                check=True
            )

            dependencies = self._parse_installed_deps(result.stdout)

            self.logger.info(f"✅ Installed {len(dependencies)} dependencies")
            return {
                "success": True,
                "installed_count": len(dependencies),
                "message": f"Installed {len(dependencies)} Lua dependencies",
                "dependencies": dependencies
            }

        except subprocess.CalledProcessError as e:
            self.logger.error(f"❌ Failed to install dependencies: {e.stderr}")
            return {
                "success": False,
                "installed_count": 0,
                "message": f"Installation failed: {e.stderr}",
                "dependencies": []
            }

    def install_dev_tools(self, tools: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Install common Lua development tools.

        WHY: Projects without rockspec still need testing/linting tools

        Args:
            tools: List of tools to install (defaults to busted, luacheck)

        Returns:
            Dict with success, installed_count, message, dependencies
        """
        if tools is None:
            tools = ["busted", "luacheck"]

        installed = []

        for tool in tools:
            if self._install_package(tool):
                installed.append(tool)
                self.logger.info(f"   ✅ Installed {tool}")
            else:
                self.logger.warning(f"   ⚠️  Failed to install {tool}")

        return {
            "success": len(installed) > 0,
            "installed_count": len(installed),
            "message": f"Installed {len(installed)} dev tools",
            "dependencies": installed
        }

    def install_package(self, package_name: str, version: Optional[str] = None) -> bool:
        """
        Install a specific LuaRocks package.

        WHY: Support programmatic installation of individual packages

        Args:
            package_name: Name of package to install
            version: Optional version constraint

        Returns:
            True if installation succeeded
        """
        package_spec = f"{package_name} {version}" if version else package_name
        return self._install_package(package_spec)

    def list_installed_packages(self) -> List[str]:
        """
        List all installed LuaRocks packages.

        WHY: Useful for diagnostics and dependency auditing

        Returns:
            List of installed package names
        """
        try:
            result = subprocess.run(
                ["luarocks", "list", "--porcelain"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                check=True
            )

            # Parse porcelain output: "package\tversion\tstatus\trepo"
            packages = []
            for line in result.stdout.split('\n'):
                if line.strip():
                    parts = line.split('\t')
                    if parts:
                        packages.append(parts[0])

            return packages

        except subprocess.CalledProcessError:
            return []

    def _install_package(self, package_spec: str) -> bool:
        """
        Install a package using luarocks.

        Args:
            package_spec: Package specification (name or name version)

        Returns:
            True if installation succeeded
        """
        try:
            subprocess.run(
                ["luarocks", "install", package_spec],
                cwd=self.project_path,
                capture_output=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def _parse_installed_deps(self, luarocks_output: str) -> List[str]:
        """
        Parse dependency names from LuaRocks output.

        WHY: Extract structured data from LuaRocks text output

        Args:
            luarocks_output: Stdout from luarocks make command

        Returns:
            List of installed dependency names
        """
        dependencies = []
        for line in luarocks_output.split('\n'):
            if "Installing" in line:
                # Format: "Installing <name> <version>"
                parts = line.split()
                if len(parts) >= 2:
                    dependencies.append(parts[1])
        return dependencies

    def is_luarocks_available(self) -> bool:
        """
        Check if luarocks command is available.

        Returns:
            True if luarocks is in PATH
        """
        try:
            subprocess.run(
                ["which", "luarocks"],
                capture_output=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError:
            return False
