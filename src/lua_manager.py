"""
Module: lua_manager.py

Purpose: Manages Lua/LuaRocks build operations and quality tooling
Why: Lua is widely used in embedded systems, game development (e.g., LÖVE, Roblox),
     web servers (OpenResty/nginx), and configuration (Neovim, Redis). Artemis needs
     to support Lua projects with proper dependency management, testing, and linting.
Patterns: Strategy Pattern (implements BuildManagerBase interface)
Integration: Integrates with universal_build_system.py via BuildManagerFactory
"""

import subprocess
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from artemis_logger import ArtemisLogger
from build_manager_base import BuildManagerBase, BuildResult
from build_manager_factory import register_build_manager, BuildSystem


@register_build_manager(BuildSystem.LUA)
class LuaManager(BuildManagerBase):
    """
    Manages Lua project builds using LuaRocks package manager and quality tools.

    Why it exists: Lua projects need dependency management (LuaRocks), testing
                   (busted), linting (luacheck), and formatting (stylua). This manager
                   provides unified interface for all Lua build operations.

    Design pattern: Strategy Pattern - implements BuildManagerBase interface

    Responsibilities:
    - Detect Lua projects (*.rockspec files, src/*.lua, init.lua)
    - Install dependencies via LuaRocks
    - Run tests with busted framework
    - Lint code with luacheck
    - Format code with stylua
    - Build rocks/modules with LuaRocks
    - Generate rockspec files for new projects

    Supported Tools:
    - LuaRocks: Package/dependency manager (like npm for Node.js)
    - busted: BDD-style testing framework
    - luacheck: Static analyzer and linter
    - stylua: Code formatter (Lua's prettier)
    - lua/luajit: Runtime interpreters

    Why LuaRocks: De facto standard for Lua dependency management, supports
                  versioning, dependencies, and binary modules (C extensions)
    """

    def __init__(self, project_dir: str = None, logger: Optional[ArtemisLogger] = None, **kwargs):
        """
        Initialize Lua manager for a project.

        Why needed: Sets up paths and validates Lua toolchain availability

        Args:
            project_dir: Root directory of Lua project (matches BuildManagerBase interface)
            logger: Optional Artemis logger for consistent logging
            **kwargs: Additional arguments (for compatibility with factory)
        """
        self.project_path = Path(project_dir) if project_dir else Path.cwd()
        self.logger = logger or ArtemisLogger(component="LuaManager")
        self.rockspec_file = self._find_rockspec()
        self._validate_installation()
        if self.detect():
            self._validate_project()

    def _validate_installation(self) -> None:
        """
        Validate Lua toolchain is installed.

        Why needed: Ensures lua/luajit and luarocks are available before attempting operations

        Raises:
            RuntimeError: If required tools are missing
        """
        # LuaRocks is required, lua/luajit is optional (might use system lua)
        if not self._command_exists("luarocks"):
            self.logger.warning("⚠️  luarocks not found - Lua support will be limited")

    def _validate_project(self) -> None:
        """
        Validate Lua project configuration.

        Why needed: Ensures project has valid structure before build operations

        Raises:
            ValueError: If project structure is invalid
        """
        # If rockspec exists, basic validation
        if self.rockspec_file and not self.rockspec_file.exists():
            raise ValueError(f"Rockspec file not found: {self.rockspec_file}")

    def _find_rockspec(self) -> Optional[Path]:
        """
        Find .rockspec file in project directory.

        Why needed: Rockspec files define Lua project metadata, dependencies,
                    and build instructions (like package.json or Gemfile)

        Returns:
            Path to rockspec file if found, None otherwise

        Edge cases:
            - Multiple rockspec files: Returns first one found
            - Versioned rockspecs (myproject-1.0.rockspec): Finds any .rockspec
        """
        rockspecs = list(self.project_path.glob("*.rockspec"))
        return rockspecs[0] if rockspecs else None

    def detect(self) -> bool:
        """
        Detect if this is a Lua project.

        Why needed: Universal build system needs to identify Lua projects
                    to route to this manager

        Returns:
            True if Lua project detected, False otherwise

        Detection criteria (any of):
            - *.rockspec file exists (LuaRocks project)
            - src/*.lua files exist (common Lua structure)
            - init.lua exists (Lua module entry point)
            - .busted file exists (busted test configuration)
        """
        has_rockspec = self.rockspec_file is not None
        has_lua_files = len(list(self.project_path.glob("src/*.lua"))) > 0
        has_init = (self.project_path / "init.lua").exists()
        has_busted_config = (self.project_path / ".busted").exists()

        is_lua_project = has_rockspec or has_lua_files or has_init or has_busted_config

        if is_lua_project:
            self.logger.info(f"✅ Detected Lua project at {self.project_path}")
            if has_rockspec:
                self.logger.info(f"   Rockspec: {self.rockspec_file.name}")

        return is_lua_project

    def install_dependencies(self) -> Dict[str, Any]:
        """
        Install Lua dependencies using LuaRocks.

        Why needed: Lua projects depend on external rocks (libraries) that must
                    be installed before building/testing

        Returns:
            Dict with:
                - success: bool - Whether installation succeeded
                - installed_count: int - Number of dependencies installed
                - message: str - Summary message
                - dependencies: List[str] - Installed dependency names

        Raises:
            subprocess.CalledProcessError: If LuaRocks command fails

        How it works:
            1. If rockspec exists: luarocks make (installs all deps)
            2. If no rockspec: luarocks install busted luacheck (dev tools)
            3. Parses output to count installed dependencies
        """
        self.logger.info("📦 Installing Lua dependencies...")

        try:
            if self.rockspec_file:
                # Install from rockspec (includes dependencies)
                result = subprocess.run(
                    ["luarocks", "make", str(self.rockspec_file)],
                    cwd=self.project_path,
                    capture_output=True,
                    text=True,
                    check=True
                )

                # Parse installed dependencies from output
                dependencies = self._parse_installed_deps(result.stdout)

                self.logger.info(f"✅ Installed {len(dependencies)} dependencies")
                return {
                    "success": True,
                    "installed_count": len(dependencies),
                    "message": f"Installed {len(dependencies)} Lua dependencies",
                    "dependencies": dependencies
                }
            else:
                # No rockspec - install common dev tools
                self.logger.info("No rockspec found, installing dev tools...")
                dev_tools = ["busted", "luacheck"]
                installed = []

                for tool in dev_tools:
                    try:
                        subprocess.run(
                            ["luarocks", "install", tool],
                            cwd=self.project_path,
                            capture_output=True,
                            check=True
                        )
                        installed.append(tool)
                        self.logger.info(f"   ✅ Installed {tool}")
                    except subprocess.CalledProcessError:
                        self.logger.warning(f"   ⚠️  Failed to install {tool}")

                return {
                    "success": len(installed) > 0,
                    "installed_count": len(installed),
                    "message": f"Installed {len(installed)} dev tools",
                    "dependencies": installed
                }

        except subprocess.CalledProcessError as e:
            self.logger.error(f"❌ Failed to install dependencies: {e.stderr}")
            return {
                "success": False,
                "installed_count": 0,
                "message": f"Installation failed: {e.stderr}",
                "dependencies": []
            }

    def _parse_installed_deps(self, luarocks_output: str) -> List[str]:
        """
        Parse dependency names from LuaRocks output.

        Why needed: Extract structured data from LuaRocks text output

        Args:
            luarocks_output: Stdout from luarocks make command

        Returns:
            List of installed dependency names

        How it works:
            Looks for lines like "Installing foo 1.0.0" and extracts "foo"
        """
        dependencies = []
        for line in luarocks_output.split('\n'):
            if "Installing" in line:
                # Format: "Installing <name> <version>"
                parts = line.split()
                if len(parts) >= 2:
                    dependencies.append(parts[1])
        return dependencies

    def test(self, **kwargs) -> BuildResult:
        """
        Run tests using busted framework (BuildManagerBase interface).

        Why needed: Required by BuildManagerBase interface for standardized testing

        Args:
            **kwargs: Additional test arguments (unused for Lua)

        Returns:
            BuildResult with test execution details

        How it works:
            Delegates to run_tests() and converts to BuildResult format
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

        Why needed: Automated testing is critical for code quality and CI/CD

        Returns:
            Dict with:
                - success: bool - All tests passed
                - total: int - Total tests run
                - passed: int - Tests that passed
                - failed: int - Tests that failed
                - duration: float - Test execution time in seconds
                - message: str - Summary message

        Raises:
            subprocess.CalledProcessError: If busted not installed

        How it works:
            1. Runs busted with --output=json for structured results
            2. Parses JSON output for test counts
            3. Falls back to text output if JSON parsing fails

        Why busted: Most popular Lua testing framework, supports BDD style,
                    integrates with LuaRocks, good CI/CD support
        """
        self.logger.info("🧪 Running Lua tests with busted...")

        # Check if busted is available
        if not self._command_exists("busted"):
            self.logger.warning("⚠️  busted not found, skipping tests")
            return {
                "success": False,
                "total": 0,
                "passed": 0,
                "failed": 0,
                "duration": 0.0,
                "message": "busted not installed"
            }

        try:
            # Run busted with JSON output for easier parsing
            result = subprocess.run(
                ["busted", "--output=json"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout for tests
            )

            # Parse JSON output
            try:
                test_results = json.loads(result.stdout)
                total = test_results.get("tests", 0)
                passed = test_results.get("successes", 0)
                failed = test_results.get("failures", 0)
                duration = test_results.get("duration", 0.0)
            except json.JSONDecodeError:
                # Fallback: parse text output
                total, passed, failed, duration = self._parse_busted_text_output(result.stdout)

            success = failed == 0 and total > 0

            if success:
                self.logger.info(f"✅ All {passed} tests passed in {duration:.2f}s")
            else:
                self.logger.error(f"❌ {failed}/{total} tests failed")

            return {
                "success": success,
                "total": total,
                "passed": passed,
                "failed": failed,
                "duration": duration,
                "message": f"{passed}/{total} tests passed" if total > 0 else "No tests found"
            }

        except subprocess.TimeoutExpired:
            self.logger.error("❌ Tests timed out after 5 minutes")
            return {
                "success": False,
                "total": 0,
                "passed": 0,
                "failed": 0,
                "duration": 300.0,
                "message": "Tests timed out"
            }
        except Exception as e:
            self.logger.error(f"❌ Test execution failed: {e}")
            return {
                "success": False,
                "total": 0,
                "passed": 0,
                "failed": 0,
                "duration": 0.0,
                "message": f"Test execution error: {e}"
            }

    def _parse_busted_text_output(self, output: str) -> tuple:
        """
        Parse busted text output when JSON not available.

        Why needed: Fallback for older busted versions without JSON support

        Args:
            output: Text output from busted

        Returns:
            Tuple of (total, passed, failed, duration)
        """
        # Look for summary line like: "5 successes / 0 failures / 0 errors / 0 pending : 0.123 seconds"
        import re
        match = re.search(r'(\d+)\s+successes?\s+/\s+(\d+)\s+failures?', output)
        if match:
            passed = int(match.group(1))
            failed = int(match.group(2))
            total = passed + failed

            # Extract duration
            duration_match = re.search(r'([\d.]+)\s+seconds', output)
            duration = float(duration_match.group(1)) if duration_match else 0.0

            return total, passed, failed, duration

        return 0, 0, 0, 0.0

    def lint(self) -> Dict[str, Any]:
        """
        Run luacheck static analyzer to find code quality issues.

        Why needed: Catches common errors, enforces coding standards, detects
                    unused variables, globals misuse, and style violations

        Returns:
            Dict with:
                - success: bool - No errors found
                - errors: int - Number of errors
                - warnings: int - Number of warnings
                - files_checked: int - Files analyzed
                - message: str - Summary

        How it works:
            Runs luacheck on all .lua files, parses output for issue counts

        Why luacheck: Standard Lua linter, configurable via .luacheckrc,
                      detects globals, unused vars, cyclomatic complexity
        """
        self.logger.info("🔍 Running luacheck linter...")

        if not self._command_exists("luacheck"):
            self.logger.warning("⚠️  luacheck not found, skipping linting")
            return {
                "success": False,
                "errors": 0,
                "warnings": 0,
                "files_checked": 0,
                "message": "luacheck not installed"
            }

        try:
            # Run luacheck on project
            result = subprocess.run(
                ["luacheck", ".", "--formatter", "plain"],
                cwd=self.project_path,
                capture_output=True,
                text=True
            )

            # Parse output (luacheck returns non-zero if issues found)
            errors, warnings, files_checked = self._parse_luacheck_output(result.stdout)

            success = errors == 0

            if success:
                self.logger.info(f"✅ No errors found ({warnings} warnings in {files_checked} files)")
            else:
                self.logger.warning(f"⚠️  Found {errors} errors, {warnings} warnings")

            return {
                "success": success,
                "errors": errors,
                "warnings": warnings,
                "files_checked": files_checked,
                "message": f"{errors} errors, {warnings} warnings in {files_checked} files"
            }

        except Exception as e:
            self.logger.error(f"❌ Linting failed: {e}")
            return {
                "success": False,
                "errors": 0,
                "warnings": 0,
                "files_checked": 0,
                "message": f"Linting error: {e}"
            }

    def _parse_luacheck_output(self, output: str) -> tuple:
        """
        Parse luacheck output for error/warning counts.

        Args:
            output: Luacheck stdout

        Returns:
            Tuple of (errors, warnings, files_checked)
        """
        import re

        # Look for summary like: "Total: 3 warnings / 1 error in 5 files"
        match = re.search(r'Total:\s+(\d+)\s+warnings?\s+/\s+(\d+)\s+errors?\s+in\s+(\d+)\s+files?', output)
        if match:
            warnings = int(match.group(1))
            errors = int(match.group(2))
            files_checked = int(match.group(3))
            return errors, warnings, files_checked

        # Count individual issues if no summary
        errors = output.count("(E)")
        warnings = output.count("(W)")
        files_checked = len([line for line in output.split('\n') if line.strip().endswith('.lua')])

        return errors, warnings, files_checked

    def format_code(self) -> Dict[str, Any]:
        """
        Format Lua code using stylua.

        Why needed: Consistent code formatting improves readability and reduces
                    diff noise in code reviews

        Returns:
            Dict with:
                - success: bool - Formatting succeeded
                - files_formatted: int - Number of files formatted
                - message: str - Summary

        Why stylua: Modern Lua formatter inspired by prettier, supports
                    configuration, widely adopted in Lua community
        """
        self.logger.info("✨ Formatting Lua code with stylua...")

        if not self._command_exists("stylua"):
            self.logger.warning("⚠️  stylua not found, skipping formatting")
            return {
                "success": False,
                "files_formatted": 0,
                "message": "stylua not installed"
            }

        try:
            # Find all Lua files
            lua_files = list(self.project_path.rglob("*.lua"))

            if not lua_files:
                return {
                    "success": True,
                    "files_formatted": 0,
                    "message": "No Lua files found"
                }

            # Run stylua on all files
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

    def build(self, **kwargs) -> BuildResult:
        """
        Build Lua rock/module using LuaRocks (BuildManagerBase interface).

        Why needed: Required by BuildManagerBase interface for standardized building

        Args:
            **kwargs: Additional build arguments (unused for Lua)

        Returns:
            BuildResult with build execution details

        How it works:
            Creates distributable .rock file using luarocks pack
        """
        self.logger.info("🔨 Building Lua rock...")
        start_time = time.time()

        if not self.rockspec_file:
            self.logger.warning("⚠️  No rockspec file, skipping build")
            return BuildResult(
                success=False,
                exit_code=1,
                duration=time.time() - start_time,
                output="No rockspec file found"
            )

        try:
            result = subprocess.run(
                ["luarocks", "pack", str(self.rockspec_file)],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                check=True
            )

            # Find generated .rock file
            rock_files = list(self.project_path.glob("*.rock"))
            artifact = str(rock_files[0]) if rock_files else None

            duration = time.time() - start_time
            message = f"Built {Path(artifact).name if artifact else 'rock'}"
            self.logger.info(f"✅ {message}")

            return BuildResult(
                success=True,
                exit_code=0,
                duration=duration,
                output=message
            )

        except subprocess.CalledProcessError as e:
            duration = time.time() - start_time
            error_msg = f"Build error: {e.stderr}"
            self.logger.error(f"❌ {error_msg}")

            return BuildResult(
                success=False,
                exit_code=e.returncode,
                duration=duration,
                output=error_msg
            )

    def clean(self) -> Dict[str, Any]:
        """
        Clean build artifacts and installed rocks.

        Why needed: Removes cached/built files for fresh builds

        Returns:
            Dict with success status and message
        """
        self.logger.info("🧹 Cleaning Lua artifacts...")

        try:
            # Remove .rock files
            rock_files = list(self.project_path.glob("*.rock"))
            for rock in rock_files:
                rock.unlink()

            # Remove luarocks build directory
            build_dir = self.project_path / ".luarocks"
            if build_dir.exists():
                import shutil
                shutil.rmtree(build_dir)

            self.logger.info(f"✅ Cleaned {len(rock_files)} artifacts")
            return {
                "success": True,
                "message": f"Cleaned {len(rock_files)} build artifacts"
            }

        except Exception as e:
            self.logger.error(f"❌ Clean failed: {e}")
            return {
                "success": False,
                "message": f"Clean error: {e}"
            }

    def _command_exists(self, command: str) -> bool:
        """
        Check if a command is available in PATH.

        Why needed: Gracefully handle missing optional tools (busted, luacheck, stylua)

        Args:
            command: Command name to check

        Returns:
            True if command exists, False otherwise
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

    def get_project_info(self) -> Dict[str, Any]:
        """
        Extract project metadata from rockspec.

        Why needed: Provides project details for reporting and dashboard

        Returns:
            Dict with project name, version, description, dependencies
        """
        if not self.rockspec_file:
            return {
                "name": "unknown",
                "version": "unknown",
                "description": "No rockspec found"
            }

        try:
            # Parse rockspec (it's Lua code, so we execute it in safe sandbox)
            # For simplicity, use regex parsing instead
            content = self.rockspec_file.read_text()

            import re
            name_match = re.search(r'package\s*=\s*["\']([^"\']+)["\']', content)
            version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            desc_match = re.search(r'description\s*=\s*{[^}]*summary\s*=\s*["\']([^"\']+)["\']', content)

            return {
                "name": name_match.group(1) if name_match else "unknown",
                "version": version_match.group(1) if version_match else "unknown",
                "description": desc_match.group(1) if desc_match else "Lua project"
            }

        except Exception as e:
            self.logger.warning(f"Failed to parse rockspec: {e}")
            return {
                "name": "unknown",
                "version": "unknown",
                "description": "Parse error"
            }
