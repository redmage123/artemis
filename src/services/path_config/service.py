#!/usr/bin/env python3
"""
Path Configuration Service

WHY: Provide centralized path configuration for Artemis pipeline (SRP).
RESPONSIBILITY: Manage all path configuration with single source of truth.
PATTERNS:
    - Singleton Pattern: Single instance for global configuration
    - Facade Pattern: Simple interface to complex path configuration
    - Composition: Delegates to resolver and directory_manager modules

This service provides the main interface for path configuration throughout
the Artemis pipeline, ensuring consistent path handling and directory management.
"""

from pathlib import Path
from typing import Optional

from .models import (
    CoreDirectories,
    ArtifactDirectories,
    PathConfiguration,
    DeveloperPaths
)
from .resolver import resolve_env_path, compute_developer_paths
from .directory_manager import (
    ensure_all_directories,
    ensure_developer_directories
)


class PathConfigService:
    """
    Centralized path configuration service for Artemis pipeline.

    WHY: Single Responsibility - manage all path configuration in one place.
    RESPONSIBILITY:
        - Read environment variables for path configuration
        - Provide consistent path construction
        - Handle relative-to-absolute path resolution
        - Maintain default fallbacks
    PATTERNS:
        - Singleton: Single instance for global configuration
        - Facade: Simple interface to complex path operations
        - Composition: Uses resolver and directory_manager modules

    Example:
        >>> service = PathConfigService()
        >>> service.ensure_directories_exist()
        >>> temp_path = service.temp_dir
        >>> dev_tests = service.get_developer_tests_dir('developer-a')
    """

    def __init__(self):
        """
        Initialize path configuration from environment variables.

        WHY: Read all configuration once at initialization for efficiency.
        PERFORMANCE: O(1) - reads environment variables once, no I/O.
        """
        # Get script directory for resolving relative paths
        self._script_dir = Path(__file__).parent.parent.parent.resolve()

        # Initialize configuration using composition
        self._config = self._build_configuration()

    def _build_configuration(self) -> PathConfiguration:
        """
        Build complete path configuration.

        WHY: Separate configuration building for testability.
        PERFORMANCE: O(1) - simple object construction.
        PATTERNS: Builder pattern for complex object construction.

        Returns:
            Complete PathConfiguration object
        """
        # Build core directories
        core = CoreDirectories(
            temp_dir=resolve_env_path('ARTEMIS_TEMP_DIR', self._script_dir),
            checkpoint_dir=resolve_env_path('ARTEMIS_CHECKPOINT_DIR', self._script_dir),
            state_dir=resolve_env_path('ARTEMIS_STATE_DIR', self._script_dir),
            status_dir=resolve_env_path('ARTEMIS_STATUS_DIR', self._script_dir)
        )

        # Build artifact directories
        artifacts = ArtifactDirectories(
            adr_dir=resolve_env_path('ARTEMIS_ADR_DIR', self._script_dir),
            developer_output_dir=resolve_env_path('ARTEMIS_DEVELOPER_DIR', self._script_dir)
        )

        return PathConfiguration(
            core=core,
            artifacts=artifacts,
            script_dir=self._script_dir
        )

    # ========================================================================
    # Public API - Core Directory Properties
    # ========================================================================

    @property
    def temp_dir(self) -> Path:
        """
        Get temporary directory path.

        WHY: Provides immutable access to configuration.
        PERFORMANCE: O(1) - property access.

        Returns:
            Path to temporary directory
        """
        return self._config.core.temp_dir

    @property
    def checkpoint_dir(self) -> Path:
        """
        Get checkpoint directory path.

        WHY: Provides immutable access to configuration.
        PERFORMANCE: O(1) - property access.

        Returns:
            Path to checkpoint directory
        """
        return self._config.core.checkpoint_dir

    @property
    def state_dir(self) -> Path:
        """
        Get state directory path.

        WHY: Provides immutable access to configuration.
        PERFORMANCE: O(1) - property access.

        Returns:
            Path to state directory
        """
        return self._config.core.state_dir

    @property
    def status_dir(self) -> Path:
        """
        Get status directory path.

        WHY: Provides immutable access to configuration.
        PERFORMANCE: O(1) - property access.

        Returns:
            Path to status directory
        """
        return self._config.core.status_dir

    # ========================================================================
    # Public API - Artifact Directory Properties
    # ========================================================================

    @property
    def adr_dir(self) -> Path:
        """
        Get ADR directory path.

        WHY: Provides immutable access to configuration.
        PERFORMANCE: O(1) - property access.

        Returns:
            Path to Architecture Decision Records directory
        """
        return self._config.artifacts.adr_dir

    @property
    def developer_output_dir(self) -> Path:
        """
        Get developer output base directory path.

        WHY: Provides immutable access to configuration.
        PERFORMANCE: O(1) - property access.

        Returns:
            Path to developer output base directory
        """
        return self._config.artifacts.developer_output_dir

    # ========================================================================
    # Public API - Developer-Specific Paths
    # ========================================================================

    def get_developer_dir(self, developer_name: str) -> Path:
        """
        Get specific developer's output directory.

        WHY: Encapsulate developer path computation.
        PERFORMANCE: O(1) - path joining operation.

        Args:
            developer_name: Name of developer (e.g., "developer-a")

        Returns:
            Path to developer's output directory

        Example:
            >>> service.get_developer_dir('developer-a')
            PosixPath('/artemis/.artemis_data/developer_output/developer-a')
        """
        return self._config.artifacts.developer_output_dir / developer_name

    def get_developer_tests_dir(self, developer_name: str) -> Path:
        """
        Get specific developer's tests directory.

        WHY: Encapsulate developer tests path computation.
        PERFORMANCE: O(1) - path joining operation.

        Args:
            developer_name: Name of developer (e.g., "developer-a")

        Returns:
            Path to developer's tests directory

        Example:
            >>> service.get_developer_tests_dir('developer-a')
            PosixPath('/artemis/.artemis_data/developer_output/developer-a/tests')
        """
        return self.get_developer_dir(developer_name) / "tests"

    def get_developer_impl_dir(self, developer_name: str) -> Path:
        """
        Get specific developer's implementation directory.

        WHY: Encapsulate developer implementation path computation.
        PERFORMANCE: O(1) - path joining operation.
        PATTERNS: Alias for get_developer_dir for semantic clarity.

        Args:
            developer_name: Name of developer (e.g., "developer-a")

        Returns:
            Path to developer's implementation directory

        Example:
            >>> service.get_developer_impl_dir('developer-a')
            PosixPath('/artemis/.artemis_data/developer_output/developer-a')
        """
        return self.get_developer_dir(developer_name)

    def get_developer_paths(self, developer_name: str) -> DeveloperPaths:
        """
        Get all paths for specific developer.

        WHY: Convenience method to get complete developer path structure.
        PERFORMANCE: O(1) - path operations.

        Args:
            developer_name: Name of developer

        Returns:
            DeveloperPaths object with all developer paths

        Example:
            >>> paths = service.get_developer_paths('developer-a')
            >>> paths.base_dir
            PosixPath('/artemis/.artemis_data/developer_output/developer-a')
        """
        base_dir = self.get_developer_dir(developer_name)
        return DeveloperPaths(
            developer_name=developer_name,
            base_dir=base_dir,
            tests_dir=base_dir / "tests",
            impl_dir=base_dir
        )

    # ========================================================================
    # Public API - Directory Management
    # ========================================================================

    def ensure_directories_exist(self) -> None:
        """
        Create all configured directories if they don't exist.

        WHY: Ensure directory structure exists before pipeline operations.
        PERFORMANCE: O(1) - fixed number of directories.
        PATTERNS: Facade - delegates to directory_manager module.

        Example:
            >>> service.ensure_directories_exist()
        """
        ensure_all_directories(self._config)

    def ensure_developer_dirs_exist(self, developer_name: str) -> None:
        """
        Create developer-specific directories if they don't exist.

        WHY: Ensure developer directory structure exists before output.
        PERFORMANCE: O(1) - fixed number of directories.
        PATTERNS: Facade - delegates to directory_manager module.

        Args:
            developer_name: Name of developer (e.g., "developer-a")

        Example:
            >>> service.ensure_developer_dirs_exist('developer-a')
        """
        dev_paths = self.get_developer_paths(developer_name)
        ensure_developer_directories(dev_paths)

    # ========================================================================
    # Public API - Configuration Access
    # ========================================================================

    @property
    def configuration(self) -> PathConfiguration:
        """
        Get complete path configuration.

        WHY: Provide access to complete configuration for advanced use cases.
        PERFORMANCE: O(1) - property access.

        Returns:
            Complete PathConfiguration object
        """
        return self._config


# ============================================================================
# Singleton Instance Management
# ============================================================================

_path_config_instance: Optional[PathConfigService] = None


def get_path_config() -> PathConfigService:
    """
    Get singleton PathConfigService instance.

    WHY: Singleton ensures single source of truth for path configuration.
    PERFORMANCE: O(1) - simple instance creation and caching.
    PATTERNS: Singleton pattern with lazy initialization.

    Returns:
        PathConfigService singleton instance

    Example:
        >>> config = get_path_config()
        >>> temp_dir = config.temp_dir
    """
    global _path_config_instance
    if _path_config_instance is None:
        _path_config_instance = PathConfigService()
    return _path_config_instance


def reset_path_config() -> None:
    """
    Reset singleton instance (primarily for testing).

    WHY: Allows tests to reset configuration state.
    PERFORMANCE: O(1) - simple variable assignment.

    Example:
        >>> reset_path_config()
        >>> config = get_path_config()  # Creates new instance
    """
    global _path_config_instance
    _path_config_instance = None
