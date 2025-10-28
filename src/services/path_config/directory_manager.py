#!/usr/bin/env python3
"""
Directory Management Operations

WHY: Separate directory creation logic from path configuration logic (SRP).
RESPONSIBILITY: Create and manage directory structures for Artemis pipeline.
PATTERNS:
    - Command Pattern: Directory operations as discrete commands
    - Batch Operations: Process multiple directories efficiently

This module handles all directory creation and management operations,
ensuring directories exist before pipeline stages attempt to use them.
"""

from pathlib import Path
from typing import List, Set
from .models import PathConfiguration, DeveloperPaths


def ensure_directory_exists(directory: Path) -> None:
    """
    Create directory if it doesn't exist.

    WHY: Encapsulate directory creation with proper error handling.
    PERFORMANCE: O(1) - single filesystem operation.

    Args:
        directory: Path to directory to create

    Example:
        >>> ensure_directory_exists(Path('/tmp/artemis/data'))
    """
    directory.mkdir(parents=True, exist_ok=True)


def ensure_directories_exist(directories: List[Path]) -> None:
    """
    Create multiple directories if they don't exist.

    WHY: Batch operation for efficiency - create all directories at once.
    PERFORMANCE: O(n) where n is number of directories.
    PATTERNS: Batch processing for multiple operations.

    Args:
        directories: List of directory paths to create

    Example:
        >>> paths = [Path('/tmp/data1'), Path('/tmp/data2')]
        >>> ensure_directories_exist(paths)
    """
    for directory in directories:
        ensure_directory_exists(directory)


def ensure_core_directories(config: PathConfiguration) -> None:
    """
    Ensure all core directories exist.

    WHY: Convenience function to create all core directories from configuration.
    PERFORMANCE: O(1) - fixed number of directories.

    Args:
        config: Path configuration containing directory paths

    Example:
        >>> ensure_core_directories(path_config)
    """
    core_dirs = [
        config.core.temp_dir,
        config.core.checkpoint_dir,
        config.core.state_dir,
        config.core.status_dir
    ]
    ensure_directories_exist(core_dirs)


def ensure_artifact_directories(config: PathConfiguration) -> None:
    """
    Ensure all artifact directories exist.

    WHY: Convenience function to create all artifact directories from configuration.
    PERFORMANCE: O(1) - fixed number of directories.

    Args:
        config: Path configuration containing directory paths

    Example:
        >>> ensure_artifact_directories(path_config)
    """
    artifact_dirs = [
        config.artifacts.adr_dir,
        config.artifacts.developer_output_dir
    ]
    ensure_directories_exist(artifact_dirs)


def ensure_all_directories(config: PathConfiguration) -> None:
    """
    Ensure all configured directories exist.

    WHY: Single operation to create complete directory structure.
    PERFORMANCE: O(1) - fixed number of directories.
    PATTERNS: Facade - provides simple interface to complex operation.

    Args:
        config: Path configuration containing all directory paths

    Example:
        >>> ensure_all_directories(path_config)
    """
    ensure_core_directories(config)
    ensure_artifact_directories(config)


def ensure_developer_directories(dev_paths: DeveloperPaths) -> None:
    """
    Ensure developer-specific directories exist.

    WHY: Create complete directory structure for developer output.
    PERFORMANCE: O(1) - fixed number of directories per developer.

    Args:
        dev_paths: Developer paths structure

    Example:
        >>> dev_paths = DeveloperPaths(
        ...     developer_name='developer-a',
        ...     base_dir=Path('/output/developer-a'),
        ...     tests_dir=Path('/output/developer-a/tests'),
        ...     impl_dir=Path('/output/developer-a')
        ... )
        >>> ensure_developer_directories(dev_paths)
    """
    directories = [
        dev_paths.base_dir,
        dev_paths.tests_dir
    ]
    ensure_directories_exist(directories)


def get_all_directories(config: PathConfiguration) -> List[Path]:
    """
    Get list of all configured directories.

    WHY: Utility function to get all directories for validation or reporting.
    PERFORMANCE: O(1) - fixed number of directories.

    Args:
        config: Path configuration

    Returns:
        List of all directory paths

    Example:
        >>> dirs = get_all_directories(path_config)
        >>> len(dirs)
        6
    """
    return [
        config.core.temp_dir,
        config.core.checkpoint_dir,
        config.core.state_dir,
        config.core.status_dir,
        config.artifacts.adr_dir,
        config.artifacts.developer_output_dir
    ]


def validate_directories_writable(directories: List[Path]) -> Set[Path]:
    """
    Validate that directories are writable.

    WHY: Pre-flight check to ensure directories can be used by pipeline.
    PERFORMANCE: O(n) where n is number of directories.

    Args:
        directories: List of directories to validate

    Returns:
        Set of directories that are not writable

    Example:
        >>> non_writable = validate_directories_writable([Path('/tmp/data')])
        >>> if non_writable:
        ...     print(f"Cannot write to: {non_writable}")
    """
    non_writable = set()

    for directory in directories:
        # Guard clause: Check if directory exists
        if not directory.exists():
            non_writable.add(directory)
            continue

        # Check if writable
        if not os.access(directory, os.W_OK):
            non_writable.add(directory)

    return non_writable


import os
