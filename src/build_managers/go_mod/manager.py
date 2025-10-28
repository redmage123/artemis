"""
Go Modules Manager - Main Orchestrator

WHY: Coordinate all Go module operations through a unified interface
RESPONSIBILITY: Main entry point that composes all specialized components
PATTERNS: Facade pattern, composition over inheritance, delegation
"""

from pathlib import Path
from typing import Dict, Optional, List, Any
import logging

from artemis_exceptions import wrap_exception
from build_system_exceptions import (
    BuildSystemNotFoundError,
    ProjectConfigurationError,
    BuildExecutionError,
    TestExecutionError,
    DependencyInstallError
)
from build_manager_base import BuildManagerBase, BuildResult
from build_manager_factory import register_build_manager, BuildSystem

from .models import GoModuleInfo
from .parser import GoModParser
from .version_detector import GoVersionDetector
from .dependency_manager import GoDependencyManager
from .build_operations import GoBuildOperations


@register_build_manager(BuildSystem.GO_MOD)
class GoModManager(BuildManagerBase):
    """
    WHY: Provide enterprise-grade Go modules management
    RESPONSIBILITY: Orchestrate all Go build system operations
    PATTERNS: Facade pattern - delegates to specialized components

    Example:
        go_mod = GoModManager(project_dir="/path/to/project")
        result = go_mod.build(output="app")
        test_result = go_mod.test()
    """

    def __init__(
        self,
        project_dir: Optional[Path] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        WHY: Initialize manager with all required components
        RESPONSIBILITY: Set up paths and delegate components
        PATTERNS: Dependency injection, composition

        Args:
            project_dir: Project directory (contains go.mod)
            logger: Logger instance

        Raises:
            BuildSystemNotFoundError: If Go not found
            ProjectConfigurationError: If go.mod invalid
        """
        self.go_mod_path = None
        self.go_sum_path = None

        super().__init__(project_dir, logger)

        self.go_sum_path = self.project_dir / "go.sum"

        # Initialize specialized components
        self._version_detector = GoVersionDetector(
            execute_command=self._execute_command,
            logger=self.logger
        )
        self._dependency_manager = GoDependencyManager(
            execute_command=self._execute_command,
            logger=self.logger
        )
        self._build_operations = GoBuildOperations(
            execute_command=self._execute_command,
            logger=self.logger
        )

    @wrap_exception(BuildSystemNotFoundError, "Go not found")
    def _validate_installation(self) -> None:
        """
        WHY: Ensure Go is installed before operations
        RESPONSIBILITY: Delegate to version detector
        PATTERNS: Delegation pattern

        Raises:
            BuildSystemNotFoundError: If Go not in PATH
        """
        self._version_detector.validate_installation()

    @wrap_exception(ProjectConfigurationError, "Invalid Go module")
    def _validate_project(self) -> None:
        """
        WHY: Ensure go.mod exists before operations
        RESPONSIBILITY: Validate project structure
        PATTERNS: Guard clause

        Raises:
            ProjectConfigurationError: If go.mod missing
        """
        self.go_mod_path = self.project_dir / "go.mod"

        if not self.go_mod_path.exists():
            raise ProjectConfigurationError(
                "go.mod not found",
                {"project_dir": str(self.project_dir)}
            )

    @wrap_exception(ProjectConfigurationError, "Failed to parse go.mod")
    def get_project_info(self) -> Dict[str, Any]:
        """
        WHY: Extract project metadata from go.mod
        RESPONSIBILITY: Delegate to parser and return dict
        PATTERNS: Delegation pattern

        Returns:
            Dict with project information

        Raises:
            ProjectConfigurationError: If go.mod malformed
        """
        module_info = GoModParser.parse_go_mod(
            self.go_mod_path,
            self.go_sum_path
        )
        return module_info.to_dict()

    @wrap_exception(BuildExecutionError, "Go build failed")
    def build(
        self,
        output: Optional[str] = None,
        tags: Optional[List[str]] = None,
        ldflags: Optional[str] = None,
        race: bool = False,
        goos: Optional[str] = None,
        goarch: Optional[str] = None,
        **kwargs
    ) -> BuildResult:
        """
        WHY: Build Go project with various options
        RESPONSIBILITY: Delegate to build operations
        PATTERNS: Delegation pattern

        Args:
            output: Output binary name
            tags: Build tags
            ldflags: Linker flags
            race: Enable race detector
            goos: Target OS (GOOS)
            goarch: Target architecture (GOARCH)

        Returns:
            BuildResult

        Raises:
            BuildExecutionError: If build fails
        """
        return self._build_operations.build(
            output=output,
            tags=tags,
            ldflags=ldflags,
            race=race,
            goos=goos,
            goarch=goarch
        )

    @wrap_exception(TestExecutionError, "Go tests failed")
    def test(
        self,
        package: Optional[str] = None,
        verbose: bool = False,
        race: bool = False,
        cover: bool = False,
        bench: bool = False,
        **kwargs
    ) -> BuildResult:
        """
        WHY: Run Go tests
        RESPONSIBILITY: Delegate to build operations
        PATTERNS: Delegation pattern

        Args:
            package: Specific package to test (default: ./...)
            verbose: Verbose output
            race: Enable race detector
            cover: Enable coverage
            bench: Run benchmarks

        Returns:
            BuildResult with test statistics

        Raises:
            TestExecutionError: If tests fail
        """
        return self._build_operations.test(
            package=package,
            verbose=verbose,
            race=race,
            cover=cover,
            bench=bench
        )

    @wrap_exception(DependencyInstallError, "Failed to add dependency")
    def install_dependency(
        self,
        module: str,
        version: Optional[str] = None,
        **kwargs
    ) -> bool:
        """
        WHY: Add a dependency to go.mod
        RESPONSIBILITY: Delegate to dependency manager
        PATTERNS: Delegation pattern

        Args:
            module: Module path
            version: Module version (optional)

        Returns:
            True if successful

        Raises:
            DependencyInstallError: If installation fails
        """
        return self._dependency_manager.install_dependency(module, version)

    @wrap_exception(BuildExecutionError, "Failed to download dependencies")
    def download_dependencies(self) -> BuildResult:
        """
        WHY: Download all dependencies
        RESPONSIBILITY: Delegate to dependency manager
        PATTERNS: Delegation pattern

        Returns:
            BuildResult

        Raises:
            BuildExecutionError: If download fails
        """
        return self._dependency_manager.download_dependencies()

    @wrap_exception(BuildExecutionError, "Failed to tidy dependencies")
    def tidy(self) -> BuildResult:
        """
        WHY: Clean up go.mod and go.sum
        RESPONSIBILITY: Delegate to dependency manager
        PATTERNS: Delegation pattern

        Returns:
            BuildResult

        Raises:
            BuildExecutionError: If tidy fails
        """
        return self._dependency_manager.tidy()

    @wrap_exception(BuildExecutionError, "Failed to verify dependencies")
    def verify(self) -> BuildResult:
        """
        WHY: Verify dependencies have expected content
        RESPONSIBILITY: Delegate to dependency manager
        PATTERNS: Delegation pattern

        Returns:
            BuildResult

        Raises:
            BuildExecutionError: If verification fails
        """
        return self._dependency_manager.verify()

    @wrap_exception(BuildExecutionError, "Failed to run go fmt")
    def fmt(self) -> BuildResult:
        """
        WHY: Format Go code
        RESPONSIBILITY: Delegate to build operations
        PATTERNS: Delegation pattern

        Returns:
            BuildResult

        Raises:
            BuildExecutionError: If formatting fails
        """
        return self._build_operations.fmt()

    @wrap_exception(BuildExecutionError, "Failed to run go vet")
    def vet(self) -> BuildResult:
        """
        WHY: Run go vet for suspicious code
        RESPONSIBILITY: Delegate to build operations
        PATTERNS: Delegation pattern

        Returns:
            BuildResult

        Raises:
            BuildExecutionError: If vet fails
        """
        return self._build_operations.vet()

    def clean(self) -> BuildResult:
        """
        WHY: Clean build cache
        RESPONSIBILITY: Delegate to build operations
        PATTERNS: Delegation pattern

        Returns:
            BuildResult
        """
        return self._build_operations.clean()

    def _extract_test_stats(self, output: str) -> Dict[str, int]:
        """
        WHY: Extract test statistics from Go test output
        RESPONSIBILITY: Delegate to build operations
        PATTERNS: Delegation pattern

        Args:
            output: Go test output

        Returns:
            Dict with test statistics
        """
        return GoBuildOperations.extract_test_stats(output)
