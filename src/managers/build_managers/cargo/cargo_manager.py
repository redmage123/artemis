"""
Module: managers/build_managers/cargo/cargo_manager.py

WHY: Orchestrate Cargo build system operations for Rust projects.
RESPONSIBILITY: Coordinate build operations, dependency management, and validation.
PATTERNS: Facade Pattern, Composition, Delegation, Template Method.

This module contains:
- CargoManager main orchestrator class
- Integration of build operations, dependency management, and validation
- Coordination layer for modularized components

EXTRACTED FROM: cargo_manager.py (main orchestrator, lines 79-476)
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from artemis_exceptions import wrap_exception
from build_manager_base import BuildManagerBase, BuildResult
from build_manager_factory import BuildSystem, register_build_manager
from build_system_exceptions import ProjectConfigurationError
from managers.build_managers.cargo.build_operations import BuildOperations
from managers.build_managers.cargo.dependency_manager import DependencyManager
from managers.build_managers.cargo.toml_parser import parse_cargo_toml
from managers.build_managers.cargo.version_detector import VersionDetector


@register_build_manager(BuildSystem.CARGO)
class CargoManager(BuildManagerBase):
    """
    Enterprise-grade Cargo manager for Rust projects.

    WHY: Provide unified interface for Rust/Cargo build operations.
    RESPONSIBILITY: Orchestrate build, test, dependency, and validation operations.
    PATTERNS: Facade (single entry point), Composition (delegate to specialized components).

    Example:
        cargo = CargoManager(project_dir="/path/to/project")
        result = cargo.build(release=True)
        test_result = cargo.test()
    """

    def __init__(
        self,
        project_dir: Optional[Path] = None,
        logger: Optional['logging.Logger'] = None
    ):
        """
        Initialize Cargo manager.

        Args:
            project_dir: Project directory (contains Cargo.toml)
            logger: Logger instance

        Raises:
            BuildSystemNotFoundError: If Cargo not found
            ProjectConfigurationError: If Cargo.toml invalid
        """
        self.cargo_toml_path = None
        self.cargo_lock_path = None

        super().__init__(project_dir, logger)

        self.cargo_lock_path = self.project_dir / "Cargo.lock"

        # Initialize specialized components
        self._version_detector = VersionDetector(
            execute_command=self._execute_command,
            logger=self.logger
        )
        self._build_ops = BuildOperations(
            project_dir=self.project_dir,
            execute_command=self._execute_command,
            logger=self.logger
        )
        self._dependency_mgr = DependencyManager(
            project_dir=self.project_dir,
            execute_command=self._execute_command,
            logger=self.logger
        )

    def _validate_installation(self) -> None:
        """
        Validate Cargo is installed.

        WHY: Ensure Cargo is available before operations.
        RESPONSIBILITY: Delegate to VersionDetector.

        Raises:
            BuildSystemNotFoundError: If Cargo not in PATH
        """
        self._version_detector.validate_installation()

    @wrap_exception(ProjectConfigurationError, "Invalid Cargo project")
    def _validate_project(self) -> None:
        """
        Validate Cargo.toml exists.

        WHY: Ensure project is properly configured.
        RESPONSIBILITY: Check for Cargo.toml presence.

        Raises:
            ProjectConfigurationError: If Cargo.toml missing
        """
        self.cargo_toml_path = self.project_dir / "Cargo.toml"

        if not self.cargo_toml_path.exists():
            raise ProjectConfigurationError(
                "Cargo.toml not found",
                {"project_dir": str(self.project_dir)}
            )

    def get_project_info(self) -> Dict[str, Any]:
        """
        Parse Cargo.toml for project information.

        WHY: Extract project metadata for reporting and analysis.
        RESPONSIBILITY: Delegate to toml_parser module.

        Returns:
            Dict with project information

        Raises:
            ProjectConfigurationError: If Cargo.toml malformed

        Example:
            info = cargo.get_project_info()
            print(f"Project: {info['name']} v{info['version']}")
        """
        return parse_cargo_toml(self.cargo_toml_path)

    def build(
        self,
        release: bool = False,
        features: Optional[List[str]] = None,
        all_features: bool = False,
        no_default_features: bool = False,
        target: Optional[str] = None,
        **kwargs
    ) -> BuildResult:
        """
        Build Rust project with Cargo.

        WHY: Compile Rust code with various configurations.
        RESPONSIBILITY: Delegate to BuildOperations.

        Args:
            release: Build in release mode (optimized)
            features: List of features to enable
            all_features: Enable all features
            no_default_features: Disable default features
            target: Target triple (e.g., "x86_64-unknown-linux-gnu")

        Returns:
            BuildResult

        Raises:
            BuildExecutionError: If build fails

        Example:
            result = cargo.build(release=True, features=["full"])
        """
        return self._build_ops.build(
            release=release,
            features=features,
            all_features=all_features,
            no_default_features=no_default_features,
            target=target,
            **kwargs
        )

    def test(
        self,
        release: bool = False,
        test_name: Optional[str] = None,
        no_fail_fast: bool = False,
        **kwargs
    ) -> BuildResult:
        """
        Run Cargo tests.

        WHY: Execute Rust test suite.
        RESPONSIBILITY: Delegate to BuildOperations.

        Args:
            release: Test release build
            test_name: Specific test to run
            no_fail_fast: Run all tests regardless of failures

        Returns:
            BuildResult with test statistics

        Raises:
            TestExecutionError: If tests fail

        Example:
            result = cargo.test(test_name="integration_tests")
        """
        return self._build_ops.test(
            release=release,
            test_name=test_name,
            no_fail_fast=no_fail_fast,
            **kwargs
        )

    def install_dependency(
        self,
        crate: str,
        version: Optional[str] = None,
        dev: bool = False,
        **kwargs
    ) -> bool:
        """
        Add a dependency to Cargo.toml.

        WHY: Manage project dependencies programmatically.
        RESPONSIBILITY: Delegate to DependencyManager.

        Args:
            crate: Crate name
            version: Crate version (optional)
            dev: Add as dev dependency

        Returns:
            True if successful

        Raises:
            DependencyInstallError: If installation fails

        Example:
            cargo.install_dependency("serde", version="1.0")
            cargo.install_dependency("tokio", dev=True)
        """
        return self._dependency_mgr.install_dependency(
            crate=crate,
            version=version,
            dev=dev,
            **kwargs
        )

    def check(self, all_features: bool = False) -> BuildResult:
        """
        Check project for errors without building.

        WHY: Fast error checking without full compilation.
        RESPONSIBILITY: Delegate to BuildOperations.

        Args:
            all_features: Check with all features enabled

        Returns:
            BuildResult

        Raises:
            BuildExecutionError: If check fails

        Example:
            result = cargo.check(all_features=True)
        """
        return self._build_ops.check(all_features=all_features)

    def clippy(self, fix: bool = False) -> BuildResult:
        """
        Run Clippy linter.

        WHY: Enforce Rust code quality standards.
        RESPONSIBILITY: Delegate to BuildOperations.

        Args:
            fix: Automatically fix warnings

        Returns:
            BuildResult

        Raises:
            BuildExecutionError: If clippy fails

        Example:
            result = cargo.clippy(fix=True)
        """
        return self._build_ops.clippy(fix=fix)

    def fmt(self, check: bool = False) -> BuildResult:
        """
        Format code with rustfmt.

        WHY: Enforce consistent code formatting.
        RESPONSIBILITY: Delegate to BuildOperations.

        Args:
            check: Check formatting without applying

        Returns:
            BuildResult

        Raises:
            BuildExecutionError: If formatting fails

        Example:
            result = cargo.fmt(check=True)
        """
        return self._build_ops.fmt(check=check)

    def clean(self) -> BuildResult:
        """
        Clean build artifacts.

        WHY: Remove compiled artifacts to free space or force rebuild.
        RESPONSIBILITY: Delegate to BuildOperations.

        Returns:
            BuildResult

        Example:
            result = cargo.clean()
        """
        return self._build_ops.clean()


__all__ = [
    "CargoManager",
]
