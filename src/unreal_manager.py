"""
Unreal Engine Build Manager

WHY: Support Unreal Engine projects in Artemis pipeline
WHAT: Manages Unreal Engine 4/5 projects using UnrealBuildTool (UBT) and Unreal Automation Tool (UAT)
HOW: Uses BuildManagerBase with UBT for compilation and UAT for packaging/testing

RESPONSIBILITY:
    - Validate Unreal Engine installation
    - Build/compile Unreal projects using UnrealBuildTool
    - Run automated tests using Unreal Automation Tool
    - Extract project metadata from .uproject files

PATTERNS:
    - Template Method: Inherits from BuildManagerBase
    - Exception Wrapping: @wrap_exception on all methods
    - Dependency Injection: Logger injection
    - Guard Clauses: Max 1 level nesting
    - Registry: Auto-registration via decorator

SUPPORTED:
    - Unreal Engine 4.x and 5.x
    - C++ and Blueprint projects
    - UnrealBuildTool (UBT) compilation
    - Unreal Automation Tool (UAT) testing
    - .uproject file parsing

EXAMPLE:
    manager = UnrealManager(project_dir="/path/to/project")
    result = manager.build()
    if result.success:
        test_result = manager.test()
"""
from pathlib import Path
from typing import Optional, Dict, Any, List
import subprocess
import json
import re
import time
import platform
from build_manager_base import BuildManagerBase, BuildResult
from artemis_exceptions import wrap_exception
from build_system_exceptions import BuildSystemNotFoundError, ProjectConfigurationError, BuildExecutionError, TestExecutionError
from build_managers.factory import BuildSystem, register_build_manager


@register_build_manager(BuildSystem.UNREAL)
class UnrealManager(BuildManagerBase):
    """
    Build manager for Unreal Engine projects.

    WHY: Enable Unreal Engine development within Artemis pipeline
    RESPONSIBILITY: Build, test, and validate Unreal projects
    PATTERNS: Template Method (inherits BuildManagerBase), Exception Wrapping

    Example:
        manager = UnrealManager(project_dir="/path/to/project", logger=logger)
        build_result = manager.build()
        test_result = manager.test()
        info = manager.get_project_info()
    """

    def __init__(self, project_dir: Optional[Path]=None, logger: Optional[
        Any]=None):
        """
        Initialize Unreal Engine build manager.

        WHY: Setup Unreal project environment with validation
        PERFORMANCE: Validates UE installation and project structure on init

        Args:
            project_dir: Path to Unreal project directory
            logger: Logger instance for output (dependency injection)

        Raises:
            BuildSystemNotFoundError: If Unreal Engine not installed
            ProjectConfigurationError: If project structure invalid
        """
        self.engine_version: Optional[str] = None
        self.uproject_file: Optional[Path] = None
        self.project_name: Optional[str] = None
        self.ubt_path: Optional[Path] = None
        self.uat_path: Optional[Path] = None
        self.project_metadata: Dict[str, Any] = {}
        super().__init__(project_dir=project_dir, logger=logger)

    @wrap_exception
    def _validate_installation(self) ->None:
        """
        Validate Unreal Engine is installed and accessible.

        WHY: Ensures UE, UBT, and UAT are available before attempting builds
        PERFORMANCE: O(1) - checks for UE executables
        Uses guard clauses to avoid nested ifs.

        Raises:
            BuildSystemNotFoundError: If Unreal Engine not found

        Notes:
            - Looks for UE installation in standard locations
            - Windows: C:/Program Files/Epic Games/UE_*
            - Linux: ~/UnrealEngine
            - Mac: /Users/Shared/Epic Games/UE_*
        """
        system = platform.system()
        if system == 'Windows':
            self._find_unreal_windows()
            return
        if system == 'Linux':
            self._find_unreal_linux()
            return
        if system == 'Darwin':
            self._find_unreal_mac()
            return
        raise BuildSystemNotFoundError(
            f'Unsupported platform for Unreal Engine: {system}', {
            'platform': system, 'supported': ['Windows', 'Linux', 'Darwin']})

    def _find_unreal_windows(self) ->None:
        """
        Find Unreal Engine installation on Windows.

        WHY: Locate UBT and UAT executables in Windows installation
        PERFORMANCE: O(n) where n is number of UE versions installed
        Uses guard clauses to avoid nested ifs.
        """
        import glob
        ue_base = Path('C:/Program Files/Epic Games')
        if not ue_base.exists():
            raise BuildSystemNotFoundError(
                'Unreal Engine installation not found', {'expected_path':
                str(ue_base), 'suggestion':
                'Install Unreal Engine from Epic Games Launcher'})
        ue_versions = list(ue_base.glob('UE_*'))
        if not ue_versions:
            raise BuildSystemNotFoundError('No Unreal Engine versions found',
                {'search_path': str(ue_base)})
        ue_install = sorted(ue_versions)[-1]
        self.engine_version = ue_install.name.replace('UE_', '')
        self.ubt_path = (ue_install / 'Engine' / 'Binaries' / 'DotNET' /
            'UnrealBuildTool' / 'UnrealBuildTool.exe')
        if not self.ubt_path.exists():
            raise BuildSystemNotFoundError('UnrealBuildTool not found', {
                'expected_path': str(self.ubt_path), 'engine_dir': str(
                ue_install)})
        self.uat_path = (ue_install / 'Engine' / 'Build' / 'BatchFiles' /
            'RunUAT.bat')
        self.logger.info(
            f'Found Unreal Engine {self.engine_version} at {ue_install}')

    def _find_unreal_linux(self) ->None:
        """
        Find Unreal Engine installation on Linux.

        WHY: Locate UBT and UAT executables in Linux installation
        PERFORMANCE: O(1) - checks single standard location
        Uses guard clauses to avoid nested ifs.
        """
        ue_paths = [Path.home() / 'UnrealEngine', Path('/opt/UnrealEngine')]
        ue_install = None
        for path in ue_paths:
            if path.exists():
                ue_install = path
                break
        if not ue_install:
            raise BuildSystemNotFoundError(
                'Unreal Engine installation not found on Linux', {
                'searched_paths': [str(p) for p in ue_paths], 'suggestion':
                'Clone and build from https://github.com/EpicGames/UnrealEngine'
                })
        self.ubt_path = (ue_install / 'Engine' / 'Binaries' / 'DotNET' /
            'UnrealBuildTool' / 'UnrealBuildTool')
        if not self.ubt_path.exists():
            raise BuildSystemNotFoundError('UnrealBuildTool not found', {
                'expected_path': str(self.ubt_path), 'engine_dir': str(
                ue_install)})
        self.uat_path = (ue_install / 'Engine' / 'Build' / 'BatchFiles' /
            'RunUAT.sh')
        self.logger.info(f'Found Unreal Engine at {ue_install}')

    def _find_unreal_mac(self) ->None:
        """
        Find Unreal Engine installation on macOS.

        WHY: Locate UBT and UAT executables in macOS installation
        PERFORMANCE: O(n) where n is number of UE versions installed
        Uses guard clauses to avoid nested ifs.
        """
        ue_base = Path('/Users/Shared/Epic Games')
        if not ue_base.exists():
            raise BuildSystemNotFoundError(
                'Unreal Engine installation not found on macOS', {
                'expected_path': str(ue_base), 'suggestion':
                'Install Unreal Engine from Epic Games Launcher'})
        ue_versions = list(ue_base.glob('UE_*'))
        if not ue_versions:
            raise BuildSystemNotFoundError('No Unreal Engine versions found',
                {'search_path': str(ue_base)})
        ue_install = sorted(ue_versions)[-1]
        self.engine_version = ue_install.name.replace('UE_', '')
        self.ubt_path = (ue_install / 'Engine' / 'Binaries' / 'Mac' /
            'UnrealBuildTool')
        if not self.ubt_path.exists():
            raise BuildSystemNotFoundError('UnrealBuildTool not found', {
                'expected_path': str(self.ubt_path), 'engine_dir': str(
                ue_install)})
        self.uat_path = (ue_install / 'Engine' / 'Build' / 'BatchFiles' /
            'RunUAT.command')
        self.logger.info(
            f'Found Unreal Engine {self.engine_version} at {ue_install}')

    @wrap_exception
    def _validate_project(self) ->None:
        """
        Validate Unreal project structure.

        WHY: Ensures project has required .uproject file
        PERFORMANCE: O(n) where n is number of files in directory
        Uses guard clauses to avoid nested ifs.

        Raises:
            ProjectConfigurationError: If no valid Unreal project found

        Valid project:
            - Must contain .uproject file
            - Optional: Source/ directory for C++ code
            - Optional: Content/ directory for assets
        """
        uproject_files = list(self.project_dir.glob('*.uproject'))
        if not uproject_files:
            raise ProjectConfigurationError(
                'No .uproject file found in project directory', {
                'project_dir': str(self.project_dir), 'suggestion':
                'Create Unreal project or specify correct directory',
                'required_files': ['*.uproject']})
        if len(uproject_files) > 1:
            raise ProjectConfigurationError('Multiple .uproject files found',
                {'project_dir': str(self.project_dir), 'found_files': [str(
                f) for f in uproject_files], 'suggestion':
                'Project should have exactly one .uproject file'})
        self.uproject_file = uproject_files[0]
        self.project_name = self.uproject_file.stem
        self._parse_project_metadata()
        self.logger.info(f'Detected Unreal project: {self.project_name}')

    @wrap_exception
    def _parse_project_metadata(self) ->None:
        """
        Parse Unreal project metadata from .uproject file.

        WHY: Extracts engine version, modules, and plugins
        PERFORMANCE: O(n) where n is file size - single file read
        Uses guard clauses to avoid nested ifs.

        Sets:
            self.project_metadata with engine association, modules, plugins
        """
        if not self.uproject_file:
            return
        try:
            with open(self.uproject_file, 'r', encoding='utf-8') as f:
                self.project_metadata = json.load(f)
            engine_association = self.project_metadata.get('EngineAssociation',
                'Unknown')
            modules = self.project_metadata.get('Modules', [])
            plugins = self.project_metadata.get('Plugins', [])
            self.logger.info(
                f'Project engine: {engine_association}, modules: {len(modules)}, plugins: {len(plugins)}'
                )
        except Exception as e:
            self.logger.warning(f'Failed to parse .uproject file: {e}')

    @wrap_exception
    def build(self, configuration: str='Development', platform_name: str=
        'Win64', clean_build: bool=False) ->BuildResult:
        """
        Build Unreal project using UnrealBuildTool.

        WHY: Compiles C++ code and prepares project for execution
        PERFORMANCE: Depends on project size - can take minutes for large projects
        Uses guard clauses to avoid nested ifs.

        Args:
            configuration: Build configuration (Development, Shipping, Debug)
            platform_name: Target platform (Win64, Linux, Mac, etc.)
            clean_build: Clean before building

        Returns:
            BuildResult with build status

        Raises:
            BuildExecutionError: If build fails

        Example:
            result = manager.build(configuration="Shipping")
            if result.success:
                self.logger.info(f"Build succeeded in {result.duration:.2f}s")
        """
        if not self.ubt_path:
            raise BuildExecutionError('UnrealBuildTool not found', {
                'suggestion': 'Unreal Engine installation may be incomplete'})
        if not self.project_name:
            raise BuildExecutionError('Project name not determined', {
                'uproject_file': str(self.uproject_file) if self.
                uproject_file else 'None'})
        cmd = [str(self.ubt_path), self.project_name, platform_name,
            configuration, f'-project={self.uproject_file}']
        if clean_build:
            cmd.append('-clean')
        try:
            return self._execute_command(cmd, timeout=1800, error_type=
                BuildExecutionError, error_message='Unreal build failed')
        except BuildExecutionError:
            raise
        except Exception as e:
            raise BuildExecutionError(
                f'Failed to execute Unreal build: {str(e)}', {'project':
                self.project_name, 'configuration': configuration,
                'platform': platform_name, 'command': ' '.join(cmd)},
                original_exception=e)

    @wrap_exception
    def test(self, test_filter: Optional[str]=None, test_suite: str='Editor'
        ) ->BuildResult:
        """
        Run Unreal Engine automated tests.

        WHY: Execute unit tests and functional tests in Unreal
        PERFORMANCE: Depends on test count - can take minutes
        Uses guard clauses to avoid nested ifs.

        Args:
            test_filter: Filter to specific tests (e.g., "MyPlugin")
            test_suite: Test suite to run (Editor, Game, Client, Server)

        Returns:
            BuildResult with test results

        Raises:
            TestExecutionError: If tests fail

        Example:
            result = manager.test(test_filter="MyPlugin")
            self.logger.info(f"Tests: {result.tests_passed}/{result.tests_run} passed")
        """
        if not self.uat_path:
            self.logger.warning(
                'Unreal Automation Tool not found, skipping tests')
            return BuildResult(success=True, exit_code=0, duration=0.0,
                output='No tests run (UAT not found)', build_system=
                'unreal', tests_run=0, tests_passed=0)
        if not self.project_name:
            raise TestExecutionError('Project name not determined', {
                'uproject_file': str(self.uproject_file) if self.
                uproject_file else 'None'})
        cmd = [str(self.uat_path), 'BuildCookRun',
            f'-project={self.uproject_file}', '-RunAutomationTests',
            f'-testsuite={test_suite}', '-nullrhi', '-unattended',
            '-stdout', '-nopause']
        if test_filter:
            cmd.append(f'-testfilter={test_filter}')
        try:
            return self._execute_command(cmd, timeout=600, error_type=
                TestExecutionError, error_message='Unreal tests failed')
        except TestExecutionError:
            raise
        except Exception as e:
            raise TestExecutionError(
                f'Failed to execute Unreal tests: {str(e)}', {'project':
                self.project_name, 'test_suite': test_suite, 'test_filter':
                test_filter, 'command': ' '.join(cmd)}, original_exception=e)

    @wrap_exception
    def get_project_info(self) ->Dict[str, Any]:
        """
        Get Unreal project information.

        WHY: Provides project metadata for pipeline decisions
        PERFORMANCE: O(1) - returns cached metadata

        Returns:
            Dict with project metadata:
                - project_name: Name from .uproject file
                - engine_version: Detected Unreal Engine version
                - engine_association: Engine version from .uproject
                - modules: List of C++ modules
                - plugins: List of enabled plugins
                - uproject_file: Path to .uproject file

        Example:
            info = manager.get_project_info()
            self.logger.info(f"Project: {info['project_name']} (UE {info['engine_version']})")
        """
        info = {'project_name': self.project_name, 'engine_version': self.
            engine_version, 'uproject_file': str(self.uproject_file) if
            self.uproject_file else None, 'project_dir': str(self.
            project_dir), 'ubt_path': str(self.ubt_path) if self.ubt_path else
            None, 'uat_path': str(self.uat_path) if self.uat_path else None}
        info.update(self.project_metadata)
        return info

    @wrap_exception
    def clean(self) ->BuildResult:
        """
        Clean Unreal build artifacts.

        WHY: Removes Binaries, Intermediate, and Saved directories
        PERFORMANCE: O(n) where n is number of files in build directories
        Uses guard clauses to avoid nested ifs.

        Returns:
            BuildResult with success status

        Example:
            result = manager.clean()
        """
        import shutil
        start_time = time.time()
        clean_dirs = [self.project_dir / 'Binaries', self.project_dir /
            'Intermediate', self.project_dir / 'Saved' / 'Automation']
        cleaned_count = 0
        for clean_dir in clean_dirs:
            if not clean_dir.exists():
                continue
            try:
                shutil.rmtree(clean_dir)
                self.logger.info(f'Removed: {clean_dir}')
                cleaned_count += 1
            except Exception as e:
                self.logger.warning(f'Failed to remove {clean_dir}: {e}')
        duration = time.time() - start_time
        return BuildResult(success=True, exit_code=0, duration=duration,
            output=f'Cleaned {cleaned_count} directories', build_system=
            'unreal', metadata={'cleaned_dirs': cleaned_count})


def _run_build_command(manager: 'UnrealManager', args, logger) -> int:
    """Execute build command and return exit code."""
    result = manager.build(configuration=args.configuration,
                          platform_name=args.platform)
    logger.log(str(result), 'INFO')
    return 0 if result.success else 1


def _run_test_command(manager: 'UnrealManager', args, logger) -> int:
    """Execute test command and return exit code."""
    result = manager.test()
    logger.log(str(result), 'INFO')
    return 0 if result.success else 1


def _run_clean_command(manager: 'UnrealManager', args, logger) -> int:
    """Execute clean command and return exit code."""
    result = manager.clean()
    logger.log(str(result), 'INFO')
    return 0 if result.success else 1


def _run_info_command(manager: 'UnrealManager', args, logger) -> int:
    """Execute info command and return exit code."""
    info = manager.get_project_info()
    logger.log(json.dumps(info, indent=2), 'INFO')
    return 0


if __name__ == '__main__':
    import argparse
    import sys
    from artemis_logger import get_logger

    parser = argparse.ArgumentParser(description=
        'Unreal Engine Build Manager CLI')
    parser.add_argument('--project-dir', type=Path, default=Path.cwd(),
        help='Unreal project directory')
    parser.add_argument('--command', choices=['build', 'test', 'clean',
        'info'], default='build', help='Command to execute')
    parser.add_argument('--configuration', choices=['Development',
        'Shipping', 'Debug'], default='Development', help='Build configuration')
    parser.add_argument('--platform', default='Win64', help='Target platform')
    parser.add_argument('--verbose', action='store_true', help=
        'Enable verbose logging')

    args = parser.parse_args()
    logger = get_logger(__name__)

    # Strategy pattern: dispatch to appropriate command handler
    command_handlers = {
        'build': _run_build_command,
        'test': _run_test_command,
        'clean': _run_clean_command,
        'info': _run_info_command,
    }

    try:
        manager = UnrealManager(project_dir=args.project_dir, logger=logger)
        handler = command_handlers.get(args.command)
        if handler:
            exit_code = handler(manager, args, logger)
            sys.exit(exit_code)
        else:
            logger.log(f'Unknown command: {args.command}', 'ERROR')
            sys.exit(1)
    except Exception as e:
        logger.log(f'Error: {str(e)}', 'ERROR')
        sys.exit(1)
