"""
Blender Build Manager

WHY: Support Blender projects, addons, and Python scripts in Artemis pipeline
WHAT: Manages Blender 2.8+ projects with Python API integration
HOW: Uses BuildManagerBase with Blender CLI for builds and tests

RESPONSIBILITY:
    - Validate Blender installation (2.8+)
    - Build/package Blender addons
    - Run Blender Python tests
    - Extract addon metadata

PATTERNS:
    - Template Method: Inherits from BuildManagerBase
    - Exception Wrapping: @wrap_exception on all methods
    - Dependency Injection: Logger injection
    - Guard Clauses: Max 1 level nesting
    - Registry: Auto-registration via decorator

SUPPORTED:
    - Blender 2.8+ (Python 3.x)
    - Addon development (packaging, metadata extraction)
    - Python script validation
    - Background mode testing

EXAMPLE:
    manager = BlenderManager(project_dir="/path/to/addon")
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
import shutil
from build_manager_base import BuildManagerBase, BuildResult
from artemis_exceptions import wrap_exception
from build_system_exceptions import BuildSystemNotFoundError, ProjectConfigurationError, BuildExecutionError, TestExecutionError
from build_managers.factory import BuildSystem, register_build_manager


@register_build_manager(BuildSystem.BLENDER)
class BlenderManager(BuildManagerBase):
    """
    Build manager for Blender projects and addons.

    WHY: Enable Blender development within Artemis pipeline
    RESPONSIBILITY: Build, test, and validate Blender projects
    PATTERNS: Template Method (inherits BuildManagerBase), Exception Wrapping

    Example:
        manager = BlenderManager(project_dir="/path/to/addon", logger=logger)
        build_result = manager.build()
        test_result = manager.test()
        info = manager.get_project_info()
    """

    def __init__(self, project_dir: Optional[Path]=None, logger: Optional[
        Any]=None):
        """
        Initialize Blender build manager.

        WHY: Setup Blender project environment with validation
        PERFORMANCE: Validates Blender installation and project structure on init

        Args:
            project_dir: Path to Blender project/addon directory
            logger: Logger instance for output (dependency injection)

        Raises:
            BuildSystemNotFoundError: If Blender not installed
            ProjectConfigurationError: If project structure invalid
        """
        self.blender_version: Optional[str] = None
        self.python_version: Optional[str] = None
        self.is_addon: bool = False
        self.addon_metadata: Dict[str, Any] = {}
        super().__init__(project_dir=project_dir, logger=logger)

    @wrap_exception
    def _validate_installation(self) ->None:
        """
        Validate Blender is installed and accessible.

        WHY: Ensures Blender executable is available before attempting builds
        PERFORMANCE: O(1) - single subprocess call to check version
        Uses guard clauses to avoid nested ifs.

        Raises:
            BuildSystemNotFoundError: If Blender not found in PATH

        Example:
            $ blender --version
            Blender 3.6.5
            Python 3.10.13
        """
        try:
            result = subprocess.run(['blender', '--version'],
                capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                raise BuildSystemNotFoundError('Blender command failed', {
                    'returncode': result.returncode, 'stderr': result.stderr})
            output = result.stdout
            version_match = re.search('Blender\\s+(\\d+\\.\\d+\\.\\d+)', output
                )
            if version_match:
                self.blender_version = version_match.group(1)
            python_match = re.search('Python\\s+(\\d+\\.\\d+\\.\\d+)', output)
            if python_match:
                self.python_version = python_match.group(1)
            self.logger.info(
                f"Found Blender {self.blender_version or 'unknown'} with Python {self.python_version or 'unknown'}"
                )
        except FileNotFoundError as e:
            raise BuildSystemNotFoundError(
                'Blender not found in PATH. Install Blender or add to PATH.',
                {'suggestion':
                'Install from https://www.blender.org/download/',
                'path_var': 'Add Blender to PATH environment variable'},
                original_exception=e)
        except subprocess.TimeoutExpired as e:
            raise BuildSystemNotFoundError('Blender version check timed out',
                {'timeout': '10s'}, original_exception=e)

    @wrap_exception
    def _validate_project(self) ->None:
        """
        Validate Blender project structure.

        WHY: Ensures project has required files (.blend or addon structure)
        PERFORMANCE: O(n) where n is number of files in directory
        Uses guard clauses to avoid nested ifs.

        Raises:
            ProjectConfigurationError: If no valid Blender project found

        Valid project types:
            1. Blender file: Contains .blend files
            2. Addon: Contains __init__.py with bl_info metadata
        """
        blend_files = list(self.project_dir.glob('*.blend'))
        init_file = self.project_dir / '__init__.py'
        if init_file.exists():
            self.is_addon = True
            self._parse_addon_metadata(init_file)
            self.logger.info(
                f"Detected Blender addon: {self.addon_metadata.get('name', 'Unknown')}"
                )
            return
        if blend_files:
            self.logger.info(
                f'Detected Blender project with {len(blend_files)} .blend file(s)'
                )
            return
        raise ProjectConfigurationError(
            'No valid Blender project found. Expected .blend files or addon structure.'
            , {'project_dir': str(self.project_dir), 'suggestion':
            'Create __init__.py for addon or add .blend files',
            'required_files': ['__init__.py (for addon)',
            '*.blend (for project)']})

    @wrap_exception
    def _parse_addon_metadata(self, init_file: Path) ->None:
        """
        Parse Blender addon metadata from __init__.py.

        WHY: Extracts bl_info dictionary for addon identification
        PERFORMANCE: O(n) where n is file size - single file read
        Uses guard clauses to avoid nested ifs.

        Args:
            init_file: Path to __init__.py

        Sets:
            self.addon_metadata with name, version, author, blender, category
        """
        try:
            with open(init_file, 'r', encoding='utf-8') as f:
                content = f.read()
            bl_info_match = re.search('bl_info\\s*=\\s*\\{([^}]+)\\}',
                content, re.DOTALL)
            if not bl_info_match:
                self.logger.warning('No bl_info found in __init__.py')
                return
            bl_info_text = bl_info_match.group(1)
            self.addon_metadata = {'name': self._extract_field(bl_info_text,
                'name'), 'version': self._extract_field(bl_info_text,
                'version'), 'author': self._extract_field(bl_info_text,
                'author'), 'blender': self._extract_field(bl_info_text,
                'blender'), 'category': self._extract_field(bl_info_text,
                'category'), 'description': self._extract_field(
                bl_info_text, 'description')}
        except Exception as e:
            self.logger.warning(f'Failed to parse addon metadata: {e}')

    def _extract_field(self, text: str, field_name: str) ->str:
        """
        Extract a field value from bl_info text.

        WHY: Parse individual fields from bl_info dictionary
        PERFORMANCE: O(n) where n is text length - regex match

        Args:
            text: bl_info dictionary content
            field_name: Field to extract (e.g., 'name', 'version')

        Returns:
            Field value or empty string if not found
        """
        pattern = f'"{field_name}"\\s*:\\s*"([^"]+)"'
        match = re.search(pattern, text)
        if match:
            return match.group(1)

        # Try tuple format for version field
        if field_name != 'version':
            return ''

        tuple_pattern = f'"{field_name}"\\s*:\\s*\\(([^)]+)\\)'
        tuple_match = re.search(tuple_pattern, text)
        if tuple_match:
            return tuple_match.group(1).strip()

        return ''

    @wrap_exception
    def build(self, output_dir: Optional[Path]=None, create_zip: bool=True
        ) ->BuildResult:
        """
        Build/package Blender addon.

        WHY: Packages addon for distribution or validates project structure
        PERFORMANCE: O(n) where n is number of files to package
        Uses guard clauses to avoid nested ifs.

        Args:
            output_dir: Directory for build output (default: project_dir/build)
            create_zip: Create zip archive of addon (default: True)

        Returns:
            BuildResult with success status and output

        Raises:
            BuildExecutionError: If build fails

        Example:
            result = manager.build()
            if result.success:
                self.logger.info(f"Build succeeded in {result.duration:.2f}s")
        """
        start_time = time.time()
        if not self.is_addon:
            duration = time.time() - start_time
            return BuildResult(success=True, exit_code=0, duration=duration,
                output='Blender project validated (.blend files found)',
                build_system='blender')
        output_dir = output_dir or self.project_dir / 'build'
        output_dir.mkdir(exist_ok=True)
        try:
            addon_name = self.addon_metadata.get('name', self.project_dir.name)
            if create_zip:
                zip_path = output_dir / f'{addon_name}.zip'
                self.logger.info(f'Creating addon archive: {zip_path}')
                shutil.make_archive(str(zip_path.with_suffix('')), 'zip',
                    self.project_dir)
                duration = time.time() - start_time
                return BuildResult(success=True, exit_code=0, duration=
                    duration, output=f'Addon packaged: {zip_path}',
                    build_system='blender', metadata={'package': str(zip_path)}
                    )
            dest_dir = output_dir / addon_name
            dest_dir.mkdir(exist_ok=True)
            for py_file in self.project_dir.glob('*.py'):
                shutil.copy(py_file, dest_dir)
            duration = time.time() - start_time
            return BuildResult(success=True, exit_code=0, duration=duration,
                output=f'Addon copied to: {dest_dir}', build_system=
                'blender', metadata={'build_dir': str(dest_dir)})
        except Exception as e:
            duration = time.time() - start_time
            raise BuildExecutionError(f'Blender addon build failed: {str(e)}',
                {'addon_name': addon_name, 'output_dir': str(output_dir),
                'duration': duration}, original_exception=e)

    @wrap_exception
    def test(self, test_script: Optional[Path]=None, background: bool=True
        ) ->BuildResult:
        """
        Run Blender Python tests.

        WHY: Execute tests in Blender environment to validate addon/scripts
        PERFORMANCE: Depends on test complexity - runs in Blender subprocess
        Uses guard clauses to avoid nested ifs.

        Args:
            test_script: Path to test script (default: tests/test_addon.py)
            background: Run in background mode (no GUI)

        Returns:
            BuildResult with test results

        Raises:
            TestExecutionError: If tests fail

        Example:
            result = manager.test()
            self.logger.info(f"Tests: {result.tests_passed}/{result.tests_run} passed")
        """
        if test_script is None:
            test_script = self.project_dir / 'tests' / 'test_addon.py'
        if not test_script.exists():
            self.logger.warning(f'No test script found: {test_script}')
            return BuildResult(success=True, exit_code=0, duration=0.0,
                output='No tests found', build_system='blender', tests_run=
                0, tests_passed=0)
        cmd = ['blender', '--background', '--python', str(test_script)]
        if not background:
            cmd.remove('--background')
        try:
            return self._execute_command(cmd, timeout=300, error_type=
                TestExecutionError, error_message='Blender tests failed')
        except TestExecutionError:
            raise
        except Exception as e:
            raise TestExecutionError(
                f'Failed to execute Blender tests: {str(e)}', {
                'test_script': str(test_script), 'command': ' '.join(cmd)},
                original_exception=e)

    @wrap_exception
    def get_project_info(self) ->Dict[str, Any]:
        """
        Get Blender project information.

        WHY: Provides project metadata for pipeline decisions
        PERFORMANCE: O(1) - returns cached metadata

        Returns:
            Dict with project metadata:
                - type: 'addon' or 'project'
                - blender_version: Required Blender version
                - python_version: Blender's Python version
                - name: Project/addon name
                - version: Addon version
                - author: Addon author
                - category: Addon category

        Example:
            info = manager.get_project_info()
            self.logger.info(f"Project: {info['name']} v{info['version']}")
        """
        info = {'type': 'addon' if self.is_addon else 'project',
            'blender_version': self.blender_version, 'python_version': self
            .python_version, 'project_dir': str(self.project_dir)}
        if self.is_addon:
            info.update(self.addon_metadata)
        return info

    @wrap_exception
    def clean(self) ->BuildResult:
        """
        Clean Blender build artifacts.

        WHY: Removes build directory and generated files
        PERFORMANCE: O(n) where n is number of files in build directory
        Uses guard clauses to avoid nested ifs.

        Returns:
            BuildResult with success status

        Example:
            result = manager.clean()
        """
        start_time = time.time()
        build_dir = self.project_dir / 'build'
        if not build_dir.exists():
            duration = time.time() - start_time
            return BuildResult(success=True, exit_code=0, duration=duration,
                output='No build artifacts to clean', build_system='blender')
        try:
            shutil.rmtree(build_dir)
            duration = time.time() - start_time
            self.logger.info(f'Cleaned build directory: {build_dir}')
            return BuildResult(success=True, exit_code=0, duration=duration,
                output=f'Removed build directory: {build_dir}',
                build_system='blender')
        except Exception as e:
            duration = time.time() - start_time
            raise BuildExecutionError(
                f'Failed to clean build artifacts: {str(e)}', {'build_dir':
                str(build_dir), 'duration': duration}, original_exception=e)


def _run_build_command(manager: 'BlenderManager', args, logger) -> int:
    """Execute build command and return exit code."""
    result = manager.build()
    logger.log(str(result), 'INFO')
    return 0 if result.success else 1


def _run_test_command(manager: 'BlenderManager', args, logger) -> int:
    """Execute test command and return exit code."""
    result = manager.test()
    logger.log(str(result), 'INFO')
    return 0 if result.success else 1


def _run_clean_command(manager: 'BlenderManager', args, logger) -> int:
    """Execute clean command and return exit code."""
    result = manager.clean()
    logger.log(str(result), 'INFO')
    return 0 if result.success else 1


def _run_info_command(manager: 'BlenderManager', args, logger) -> int:
    """Execute info command and return exit code."""
    info = manager.get_project_info()
    logger.log(json.dumps(info, indent=2), 'INFO')
    return 0


if __name__ == '__main__':
    import argparse
    import sys
    from artemis_logger import get_logger

    parser = argparse.ArgumentParser(description='Blender Build Manager CLI')
    parser.add_argument('--project-dir', type=Path, default=Path.cwd(),
        help='Blender project directory')
    parser.add_argument('--command', choices=['build', 'test', 'clean',
        'info'], default='build', help='Command to execute')
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
        manager = BlenderManager(project_dir=args.project_dir, logger=logger)
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
