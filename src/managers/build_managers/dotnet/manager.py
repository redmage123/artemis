#!/usr/bin/env python3
"""
.NET Build Manager - Main Orchestrator

WHY: Compose all .NET build system components into a unified interface.
RESPONSIBILITY: Coordinate project parsing, builds, tests, and package management.
PATTERNS: Facade pattern, Composition over inheritance, Dependency Injection.

Part of: managers.build_managers.dotnet
Dependencies: All other dotnet submodules
"""

from pathlib import Path
from typing import Optional, Dict, Any

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

from managers.build_managers.dotnet.models import DotNetProjectInfo
from managers.build_managers.dotnet.project_parser import ProjectParser
from managers.build_managers.dotnet.nuget_manager import NuGetManager
from managers.build_managers.dotnet.build_operations import BuildOperations
from managers.build_managers.dotnet.framework_detector import FrameworkDetector


@register_build_manager(BuildSystem.DOTNET)
class DotNetManager(BuildManagerBase):
    """
    Enterprise-grade .NET build manager for C#/F#/VB.NET projects.

    WHY: Provide unified interface for all .NET build operations.
    RESPONSIBILITY: Orchestrate project parsing, building, testing, and publishing.
    PATTERNS: Facade pattern, Composition pattern.

    This class delegates to specialized components:
    - ProjectParser: Parse .csproj/.sln files
    - NuGetManager: Handle package operations
    - BuildOperations: Execute build/test/publish
    - FrameworkDetector: Detect SDK versions

    Example:
        dotnet = DotNetManager(project_dir="/path/to/project")
        result = dotnet.build(configuration="Release")
        test_result = dotnet.test()
    """

    def __init__(
        self,
        project_dir: Optional[Path] = None,
        logger: Optional['logging.Logger'] = None
    ):
        """
        Initialize .NET manager.

        WHY: Set up composition structure before validation.

        Args:
            project_dir: Project directory (contains .csproj/.sln)
            logger: Logger instance

        Raises:
            BuildSystemNotFoundError: If dotnet not found
            ProjectConfigurationError: If project file invalid

        Guards:
            - Validation occurs in parent class after initialization
        """
        self.project_file: Optional[Path] = None
        self.solution_file: Optional[Path] = None
        self.is_solution: bool = False

        # Component instances (initialized after project detection)
        self._nuget_manager: Optional[NuGetManager] = None
        self._build_operations: Optional[BuildOperations] = None
        self._framework_detector: Optional[FrameworkDetector] = None

        super().__init__(project_dir, logger)

    @wrap_exception(BuildSystemNotFoundError, ".NET SDK not found")
    def _validate_installation(self) -> None:
        """
        Validate .NET SDK is installed and accessible.

        WHY: Fail fast if dotnet CLI is not available.

        Raises:
            BuildSystemNotFoundError: If dotnet not in PATH
        """
        result = self._execute_command(
            ["dotnet", "--version"],
            timeout=10,
            error_type=BuildSystemNotFoundError,
            error_message=".NET SDK not installed or not in PATH"
        )

        version = result.output.strip()
        self.logger.info(f"Using .NET SDK version: {version}")

    @wrap_exception(ProjectConfigurationError, "Invalid .NET project")
    def _validate_project(self) -> None:
        """
        Validate project or solution file exists and initialize components.

        WHY: Detect project structure and configure specialized components.

        Raises:
            ProjectConfigurationError: If no project/solution file found

        Guards:
            - At least one .sln or .*proj file must exist
        """
        # Check for solution file first (preferred for multi-project)
        sln_files = list(self.project_dir.glob("*.sln"))

        if sln_files:
            self.solution_file = sln_files[0]
            self.is_solution = True
            self.logger.info(f"Found solution file: {self.solution_file.name}")
            self._initialize_components(self.solution_file)
            return

        # Check for project files
        project_files = (
            list(self.project_dir.glob("*.csproj")) +
            list(self.project_dir.glob("*.fsproj")) +
            list(self.project_dir.glob("*.vbproj"))
        )

        if not project_files:
            raise ProjectConfigurationError(
                "No .NET project or solution file found",
                {"project_dir": str(self.project_dir)}
            )

        self.project_file = project_files[0]
        self.logger.info(f"Found project file: {self.project_file.name}")
        self._initialize_components(self.project_file)

    def _initialize_components(self, target_path: Path) -> None:
        """
        Initialize specialized component managers.

        WHY: Use composition to delegate responsibilities.

        Args:
            target_path: Path to project or solution file

        Guards:
            - target_path must be valid
        """
        if not target_path or not target_path.exists():
            raise ValueError(f"Invalid target path: {target_path}")

        # Initialize NuGet manager (only for projects, not solutions)
        if not self.is_solution and self.project_file:
            self._nuget_manager = NuGetManager(
                project_file=self.project_file,
                execute_command=self._execute_command,
                logger=self.logger
            )

        # Initialize build operations
        self._build_operations = BuildOperations(
            target_path=target_path,
            is_solution=self.is_solution,
            execute_command=self._execute_command,
            logger=self.logger
        )

        # Initialize framework detector
        self._framework_detector = FrameworkDetector(
            execute_command=self._execute_command,
            logger=self.logger
        )

    @wrap_exception(ProjectConfigurationError, "Failed to parse project file")
    def get_project_info(self) -> Dict[str, Any]:
        """
        Parse project/solution file for metadata.

        WHY: Provide structured project information for tooling.

        Returns:
            Dict with project information (serialized DotNetProjectInfo)

        Raises:
            ProjectConfigurationError: If project file malformed

        Guards:
            - Either project_file or solution_file must be set
        """
        if self.is_solution and self.solution_file:
            info = ProjectParser.parse_solution(self.solution_file)
        elif self.project_file:
            info = ProjectParser.parse_project(self.project_file)
        else:
            raise ProjectConfigurationError(
                "No project or solution file available",
                {}
            )

        return info.to_dict()

    @wrap_exception(BuildExecutionError, ".NET build failed")
    def build(
        self,
        configuration: str = "Debug",
        framework: Optional[str] = None,
        runtime: Optional[str] = None,
        no_restore: bool = False,
        **kwargs
    ) -> BuildResult:
        """
        Build .NET project or solution.

        WHY: Compile source code to binaries.

        Args:
            configuration: Build configuration (Debug/Release)
            framework: Target framework (net8.0, net6.0, etc.)
            runtime: Runtime identifier (win-x64, linux-x64, etc.)
            no_restore: Skip restoring dependencies
            **kwargs: Additional arguments (ignored for compatibility)

        Returns:
            BuildResult with compilation details

        Raises:
            BuildExecutionError: If build fails

        Guards:
            - _build_operations must be initialized
        """
        if not self._build_operations:
            raise BuildExecutionError(
                "Build operations not initialized",
                {}
            )

        return self._build_operations.build(
            configuration=configuration,
            framework=framework,
            runtime=runtime,
            no_restore=no_restore
        )

    @wrap_exception(TestExecutionError, ".NET tests failed")
    def test(
        self,
        configuration: str = "Debug",
        no_build: bool = False,
        verbosity: Optional[str] = None,
        filter: Optional[str] = None,
        **kwargs
    ) -> BuildResult:
        """
        Run .NET unit tests.

        WHY: Execute test suite to verify code correctness.

        Args:
            configuration: Build configuration
            no_build: Skip building before testing
            verbosity: Log verbosity (q[uiet], m[inimal], n[ormal], d[etailed], diag[nostic])
            filter: Test filter expression
            **kwargs: Additional arguments (ignored for compatibility)

        Returns:
            BuildResult with test statistics

        Raises:
            TestExecutionError: If tests fail

        Guards:
            - _build_operations must be initialized
        """
        if not self._build_operations:
            raise TestExecutionError(
                "Build operations not initialized",
                {}
            )

        return self._build_operations.test(
            configuration=configuration,
            no_build=no_build,
            verbosity=verbosity,
            filter=filter
        )

    @wrap_exception(DependencyInstallError, "Failed to add package")
    def install_dependency(
        self,
        package: str,
        version: Optional[str] = None,
        **kwargs
    ) -> bool:
        """
        Add a NuGet package to project.

        WHY: Programmatically manage project dependencies.

        Args:
            package: Package name (e.g., "Newtonsoft.Json")
            version: Package version (optional, uses latest if not specified)
            **kwargs: Additional arguments (ignored for compatibility)

        Returns:
            True if successful

        Raises:
            DependencyInstallError: If installation fails

        Guards:
            - Cannot add packages to solution files
            - _nuget_manager must be initialized
        """
        if self.is_solution:
            raise DependencyInstallError(
                "Cannot add package to solution. Specify project file.",
                {"package": package}
            )

        if not self._nuget_manager:
            raise DependencyInstallError(
                "NuGet manager not initialized",
                {"package": package}
            )

        return self._nuget_manager.add_package(package, version)

    @wrap_exception(BuildExecutionError, "Failed to restore dependencies")
    def restore(self) -> BuildResult:
        """
        Restore NuGet packages for project or solution.

        WHY: Download all declared dependencies before build.

        Returns:
            BuildResult with restore details

        Raises:
            BuildExecutionError: If restore fails

        Guards:
            - Either project_file or solution_file must be set
        """
        target_path = self.solution_file if self.is_solution else self.project_file

        if not target_path:
            raise BuildExecutionError(
                "No target path for restore operation",
                {}
            )

        if not self._nuget_manager:
            # Create temporary NuGet manager for restore
            temp_manager = NuGetManager(
                project_file=target_path,
                execute_command=self._execute_command,
                logger=self.logger
            )
            return temp_manager.restore_packages(target_path)

        return self._nuget_manager.restore_packages(target_path)

    @wrap_exception(BuildExecutionError, "Failed to publish")
    def publish(
        self,
        configuration: str = "Release",
        framework: Optional[str] = None,
        runtime: Optional[str] = None,
        output: Optional[str] = None,
        self_contained: bool = False,
        **kwargs
    ) -> BuildResult:
        """
        Publish .NET application for deployment.

        WHY: Create deployment-ready artifacts with dependencies.

        Args:
            configuration: Build configuration
            framework: Target framework
            runtime: Runtime identifier
            output: Output directory path
            self_contained: Include .NET runtime in output
            **kwargs: Additional arguments (ignored for compatibility)

        Returns:
            BuildResult with publish details

        Raises:
            BuildExecutionError: If publish fails

        Guards:
            - _build_operations must be initialized
        """
        if not self._build_operations:
            raise BuildExecutionError(
                "Build operations not initialized",
                {}
            )

        return self._build_operations.publish(
            configuration=configuration,
            framework=framework,
            runtime=runtime,
            output=output,
            self_contained=self_contained
        )

    @wrap_exception(BuildExecutionError, "Failed to run application")
    def run(
        self,
        configuration: str = "Debug",
        framework: Optional[str] = None,
        **kwargs
    ) -> BuildResult:
        """
        Run .NET application directly.

        WHY: Execute console/web application without explicit build step.

        Args:
            configuration: Build configuration
            framework: Target framework
            **kwargs: Additional arguments (ignored for compatibility)

        Returns:
            BuildResult with run output

        Raises:
            BuildExecutionError: If run fails

        Guards:
            - _build_operations must be initialized
        """
        if not self._build_operations:
            raise BuildExecutionError(
                "Build operations not initialized",
                {}
            )

        return self._build_operations.run(
            configuration=configuration,
            framework=framework
        )

    def clean(self) -> BuildResult:
        """
        Clean build outputs (bin/obj directories).

        WHY: Remove intermediate and output files for fresh build.

        Returns:
            BuildResult (always succeeds, logs warnings on failure)

        Guards:
            - _build_operations must be initialized
        """
        if not self._build_operations:
            self.logger.warning("Build operations not initialized")
            return BuildResult(
                success=False,
                exit_code=1,
                duration=0.0,
                output="Build operations not initialized",
                build_system="dotnet"
            )

        return self._build_operations.clean()

    def _extract_test_stats(self, output: str) -> Dict[str, int]:
        """
        Extract test statistics from dotnet test output.

        WHY: Backward compatibility with existing code.

        Args:
            output: dotnet test command output

        Returns:
            Dictionary with test counts
        """
        return BuildOperations.extract_test_stats(output)


__all__ = ["DotNetManager"]
