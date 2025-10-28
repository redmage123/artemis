#!/usr/bin/env python3
"""
Path Resolution Logic

WHY: Centralize path resolution logic to handle absolute and relative paths consistently.
RESPONSIBILITY: Convert path strings to absolute Path objects.
PATTERNS:
    - Strategy Pattern: Different resolution strategies for absolute vs relative paths
    - Pure Functions: Stateless path resolution functions

This module provides path resolution functionality, converting environment variable
values and relative paths into absolute Path objects.
"""

import os
from pathlib import Path
from typing import Dict, Optional


# Default path mappings for environment variables
# WHY: DRY principle - single source of truth for default paths
DEFAULT_PATH_MAP: Dict[str, str] = {
    'ARTEMIS_TEMP_DIR': '../../.artemis_data/temp',
    'ARTEMIS_CHECKPOINT_DIR': '../../.artemis_data/checkpoints',
    'ARTEMIS_STATE_DIR': '../../.artemis_data/state',
    'ARTEMIS_STATUS_DIR': '../../.artemis_data/status',
    'ARTEMIS_ADR_DIR': '../../.artemis_data/adrs',
    'ARTEMIS_DEVELOPER_DIR': '../../.artemis_data/developer_output'
}


def resolve_path(path_str: str, base_dir: Path) -> Path:
    """
    Resolve path string to absolute Path object.

    WHY: Handles both absolute and relative paths consistently.
    PERFORMANCE: O(1) - simple path operations, no I/O.
    PATTERNS: Strategy Pattern - delegates to absolute or relative resolution.

    Args:
        path_str: Path string to resolve (absolute or relative)
        base_dir: Base directory for resolving relative paths

    Returns:
        Absolute Path object

    Example:
        >>> script_dir = Path('/home/user/artemis/src')
        >>> resolve_path('../../data/temp', script_dir)
        PosixPath('/home/user/data/temp')
        >>> resolve_path('/absolute/path', script_dir)
        PosixPath('/absolute/path')
    """
    # Guard clause: Handle absolute paths
    if os.path.isabs(path_str):
        return Path(path_str)

    # Handle relative paths
    return _resolve_relative_path(path_str, base_dir)


def _resolve_relative_path(path_str: str, base_dir: Path) -> Path:
    """
    Resolve relative path to absolute Path.

    WHY: Private helper to keep path resolution logic modular.
    PERFORMANCE: O(1) - path joining operation.

    Args:
        path_str: Relative path string
        base_dir: Base directory to resolve from

    Returns:
        Absolute Path object
    """
    return base_dir / path_str


def get_env_path(env_var: str, default: Optional[str] = None) -> str:
    """
    Get path from environment variable with optional default.

    WHY: Centralize environment variable reading with fallback logic.
    PERFORMANCE: O(1) - simple dictionary lookup.
    PATTERNS: Functional programming - pure function with no side effects.

    Args:
        env_var: Environment variable name
        default: Default value if environment variable not set

    Returns:
        Path string from environment or default

    Example:
        >>> get_env_path('ARTEMIS_TEMP_DIR', '../../.artemis_data/temp')
        '../../.artemis_data/temp'
    """
    # Use default from map if not provided
    if default is None:
        default = DEFAULT_PATH_MAP.get(env_var, '')

    return os.getenv(env_var, default)


def resolve_env_path(env_var: str, base_dir: Path, default: Optional[str] = None) -> Path:
    """
    Resolve path from environment variable.

    WHY: Combines environment variable reading and path resolution.
    PERFORMANCE: O(1) - combines two O(1) operations.
    PATTERNS: Functional composition - combines get_env_path and resolve_path.

    Args:
        env_var: Environment variable name
        base_dir: Base directory for resolving relative paths
        default: Default path if environment variable not set

    Returns:
        Absolute Path object

    Example:
        >>> script_dir = Path('/home/user/artemis/src')
        >>> resolve_env_path('ARTEMIS_TEMP_DIR', script_dir)
        PosixPath('/home/user/artemis/.artemis_data/temp')
    """
    path_str = get_env_path(env_var, default)
    return resolve_path(path_str, base_dir)


def compute_developer_paths(developer_name: str, base_dir: Path) -> Dict[str, Path]:
    """
    Compute all paths for a specific developer.

    WHY: Centralize developer path computation logic.
    PERFORMANCE: O(1) - simple path joining operations.
    PATTERNS:
        - Pure Function: No side effects, deterministic output
        - DRY: Single source of truth for developer path structure

    Args:
        developer_name: Name of developer (e.g., "developer-a")
        base_dir: Base developer output directory

    Returns:
        Dictionary with developer path mappings

    Example:
        >>> compute_developer_paths('developer-a', Path('/output'))
        {
            'base_dir': PosixPath('/output/developer-a'),
            'tests_dir': PosixPath('/output/developer-a/tests'),
            'impl_dir': PosixPath('/output/developer-a')
        }
    """
    dev_base = base_dir / developer_name
    return {
        'base_dir': dev_base,
        'tests_dir': dev_base / 'tests',
        'impl_dir': dev_base
    }
