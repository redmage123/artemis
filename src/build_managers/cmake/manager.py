#!/usr/bin/env python3
"""
WHY: Enterprise-grade CMake build manager
RESPONSIBILITY: Orchestrate CMake operations (configure, build, test, clean)
PATTERNS: Facade (simplified API), Template Method (inherits BuildManagerBase)

CMake manager coordinates validation, configuration, building, and testing
for C/C++ projects using CMake.
"""

from pathlib import Path
from typing import Dict, Optional, Any
import shutil
from build_manager_base import BuildManagerBase, BuildResult
from build_manager_factory import register_build_manager, BuildSystem
from build_managers.cmake.validator import CMakeValidator
from build_managers.cmake.project_parser import CMakeProjectParser
from build_managers.cmake.configurator import CMakeConfigurator
from build_managers.cmake.builder import CMakeBuilder
from build_managers.cmake.test_runner import CMakeTestRunner
from build_managers.cmake.test_stats_parser import TestStatsParser


@register_build_manager(BuildSystem.CMAKE)
class CMakeManager(BuildManagerBase):
    """
    Enterprise-grade CMake manager for C/C++ projects.

    WHY: Provides unified interface for CMake operations.
    RESPONSIBILITY: Coordinate all CMake build operations.
    PATTERNS: Facade, Template Method, Composition.

    Example:
        >>> cmake = CMakeManager(project_dir="/path/to/project")
        >>> cmake.configure(build_type="Release")
        >>> result = cmake.build(target="all")
        >>> test_result = cmake.test()
    """

    def __init__(
        self,
        project_dir: Optional[Path] = None,
        logger: Optional['logging.Logger'] = None,
        build_dir: Optional[Path] = None
    ):
        """
        Initialize CMake manager.

        Args:
            project_dir: Project directory (contains CMakeLists.txt)
            logger: Logger instance
            build_dir: Build directory (defaults to project_dir/build)

        Raises:
            BuildSystemNotFoundError: If CMake not found
            ProjectConfigurationError: If CMakeLists.txt missing
        """
        self.cmakelists_path = None
        self.build_directory = None

        super().__init__(project_dir, logger)

        # Set build directory
        self.build_directory = Path(build_dir) if build_dir else self.project_dir / "build"

        # Initialize components (Composition pattern)
        self.validator = CMakeValidator(logger)
        self.parser = CMakeProjectParser()
        self.configurator = CMakeConfigurator()
        self.builder = CMakeBuilder()
        self.test_runner = CMakeTestRunner()
        self.stats_parser = TestStatsParser()

    def _validate_installation(self) -> None:
        """Validate CMake is installed"""
        self.validator.validate_installation(self._execute_command)

    def _validate_project(self) -> None:
        """Validate CMakeLists.txt exists"""
        self.cmakelists_path = self.validator.validate_project(self.project_dir)

    def get_project_info(self) -> Dict[str, Any]:
        """Parse CMakeLists.txt for project information"""
        return self.parser.parse_project_info(
            self.cmakelists_path,
            self.build_directory,
            self.project_dir
        )

    def configure(
        self,
        build_type: str = "Release",
        generator: Optional[str] = None,
        options: Optional[Dict[str, str]] = None
    ) -> BuildResult:
        """Configure CMake project"""
        return self.configurator.configure(
            self.project_dir,
            self.build_directory,
            self._execute_command,
            build_type,
            generator,
            options
        )

    def build(
        self,
        target: Optional[str] = None,
        parallel: bool = True,
        clean: bool = False,
        **kwargs
    ) -> BuildResult:
        """Build CMake project"""
        return self.builder.build(
            self.build_directory,
            self._execute_command,
            self.configure,
            self.clean,
            target,
            parallel,
            clean
        )

    def test(
        self,
        verbose: bool = False,
        parallel: bool = True,
        **kwargs
    ) -> BuildResult:
        """Run CMake tests using CTest"""
        return self.test_runner.test(
            self.build_directory,
            self._execute_command,
            verbose,
            parallel
        )

    def clean(self) -> BuildResult:
        """Clean build artifacts"""
        # Guard clause - return early if build dir doesn't exist
        if not self.build_directory.exists():
            return BuildResult(
                success=True,
                exit_code=0,
                duration=0.0,
                output="Nothing to clean",
                build_system="cmake"
            )

        self.logger.info(f"Removing {self.build_directory}...")
        shutil.rmtree(self.build_directory)

        return BuildResult(
            success=True,
            exit_code=0,
            duration=0.0,
            output="Clean completed",
            build_system="cmake"
        )

    def _extract_test_stats(self, output: str) -> Dict[str, int]:
        """Extract test statistics from CTest output"""
        return self.stats_parser.extract_test_stats(output)
