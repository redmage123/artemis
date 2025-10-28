"""
Module: manager.py

WHY: Orchestrates Lua build operations using modular components
RESPONSIBILITY: Coordinate all Lua build operations, implement BuildManagerBase interface
PATTERNS: Facade Pattern (unified interface), Delegation Pattern
"""

import time
from pathlib import Path
from typing import Dict, List, Optional, Any

from artemis_logger import ArtemisLogger
from build_manager_base import BuildManagerBase, BuildResult

from .version_detector import LuaVersionDetector
from .package_manager import LuaRocksPackageManager
from .test_runner import LuaTestRunner
from .linter import LuaLinter
from .formatter import LuaFormatter
from .build_operations import LuaBuildOperations
from .project_detector import LuaProjectDetector


class LuaManager(BuildManagerBase):
    """
    Manages Lua project builds using LuaRocks and quality tools.

    WHY: Provides unified interface for all Lua build operations
    RESPONSIBILITY: Orchestrate components, implement BuildManagerBase interface
    PATTERNS: Facade Pattern - delegates to specialized components

    Supported Tools:
    - LuaRocks: Package/dependency manager
    - busted: BDD-style testing framework
    - luacheck: Static analyzer and linter
    - stylua: Code formatter
    - lua/luajit: Runtime interpreters
    """

    def __init__(self, project_dir: str = None, logger: Optional[ArtemisLogger] = None, **kwargs):
        """
        Initialize Lua manager.

        Args:
            project_dir: Root directory of Lua project
            logger: Optional logger instance
            **kwargs: Additional arguments (for factory compatibility)
        """
        self.project_path = Path(project_dir) if project_dir else Path.cwd()
        self.logger = logger or ArtemisLogger(component="LuaManager")

        # Initialize components
        self.version_detector = LuaVersionDetector(self.project_path)
        self.package_manager = LuaRocksPackageManager(self.project_path, self.logger)
        self.test_runner = LuaTestRunner(self.project_path, self.logger)
        self.linter = LuaLinter(self.project_path, self.logger)
        self.formatter = LuaFormatter(self.project_path, self.logger)
        self.build_ops = LuaBuildOperations(self.project_path, self.logger)
        self.detector = LuaProjectDetector(self.project_path, self.logger)

        self.rockspec_file = self.detector.find_rockspec()
        self._validate_installation()

        if self.detect():
            self._validate_project()

    def _validate_installation(self) -> None:
        """
        Validate Lua toolchain is installed.

        WHY: Ensures luarocks is available before operations
        """
        if not self.package_manager.is_luarocks_available():
            self.logger.warning("⚠️  luarocks not found - Lua support will be limited")

    def _validate_project(self) -> None:
        """
        Validate Lua project configuration.

        WHY: Ensures project has valid structure
        """
        if self.rockspec_file and not self.rockspec_file.exists():
            raise ValueError(f"Rockspec file not found: {self.rockspec_file}")

    def detect(self) -> bool:
        """
        Detect if this is a Lua project.

        Returns:
            True if Lua project detected
        """
        return self.detector.detect()

    def install_dependencies(self) -> Dict[str, Any]:
        """
        Install Lua dependencies using LuaRocks.

        Returns:
            Dict with success, installed_count, message, dependencies
        """
        self.logger.info("📦 Installing Lua dependencies...")

        if self.rockspec_file:
            return self.package_manager.install_from_rockspec(self.rockspec_file)
        else:
            self.logger.info("No rockspec found, installing dev tools...")
            return self.package_manager.install_dev_tools()

    def test(self, **kwargs) -> BuildResult:
        """
        Run tests using busted framework.

        Args:
            **kwargs: Additional test arguments

        Returns:
            BuildResult with test execution details
        """
        start_time = time.time()
        result = self.run_tests()
        duration = time.time() - start_time

        return BuildResult(
            success=result["success"],
            exit_code=0 if result["success"] else 1,
            duration=duration,
            output=result["message"]
        )

    def run_tests(self) -> Dict[str, Any]:
        """
        Run tests using busted framework.

        Returns:
            Dict with success, total, passed, failed, duration, message
        """
        return self.test_runner.run_tests()

    def lint(self) -> Dict[str, Any]:
        """
        Run luacheck static analyzer.

        Returns:
            Dict with success, errors, warnings, files_checked, message
        """
        return self.linter.lint()

    def format_code(self) -> Dict[str, Any]:
        """
        Format Lua code using stylua.

        Returns:
            Dict with success, files_formatted, message
        """
        return self.formatter.format_code()

    def build(self, **kwargs) -> BuildResult:
        """
        Build Lua rock using LuaRocks.

        Args:
            **kwargs: Additional build arguments

        Returns:
            BuildResult with build execution details
        """
        start_time = time.time()

        if not self.rockspec_file:
            self.logger.warning("⚠️  No rockspec file, skipping build")
            return BuildResult(
                success=False,
                exit_code=1,
                duration=time.time() - start_time,
                output="No rockspec file found"
            )

        result = self.build_ops.build_rock(self.rockspec_file)
        duration = time.time() - start_time

        return BuildResult(
            success=result["success"],
            exit_code=0 if result["success"] else 1,
            duration=duration,
            output=result["message"]
        )

    def clean(self) -> Dict[str, Any]:
        """
        Clean build artifacts.

        Returns:
            Dict with success, message
        """
        return self.build_ops.clean()

    def get_project_info(self) -> Dict[str, Any]:
        """
        Extract project metadata from rockspec.

        Returns:
            Dict with project name, version, description
        """
        return self.detector.get_project_info()

    def get_runtime_info(self) -> Dict[str, Any]:
        """
        Get Lua runtime version information.

        Returns:
            Dict with lua_version, luajit_version, has_lua, has_luajit
        """
        return self.version_detector.get_runtime_info()
