#!/usr/bin/env python3
"""
Path Configuration Service Package

WHY: Modular path configuration service for Artemis pipeline.
RESPONSIBILITY: Export public API for path configuration.
PATTERNS:
    - Facade Pattern: Simple public API hiding internal complexity
    - Separation of Concerns: Models, resolvers, and managers separated

This package provides centralized path configuration for the Artemis pipeline,
replacing the monolithic path_config_service.py with a modular structure.

Package Structure:
    - models.py: Immutable data structures for path configuration
    - resolver.py: Path resolution logic (absolute/relative)
    - directory_manager.py: Directory creation and management
    - service.py: Main PathConfigService class

Public API:
    - PathConfigService: Main service class
    - get_path_config(): Get singleton instance
    - reset_path_config(): Reset singleton (testing)

Example:
    >>> from services.path_config import get_path_config
    >>> config = get_path_config()
    >>> config.ensure_directories_exist()
    >>> temp_dir = config.temp_dir
"""

# Export main service and singleton getter
from .service import (
    PathConfigService,
    get_path_config,
    reset_path_config
)

# Export models for advanced use cases
from .models import (
    CoreDirectories,
    ArtifactDirectories,
    PathConfiguration,
    DeveloperPaths
)

# Export utility functions
from .resolver import (
    resolve_path,
    resolve_env_path,
    compute_developer_paths
)

from .directory_manager import (
    ensure_directory_exists,
    ensure_directories_exist,
    ensure_all_directories,
    ensure_developer_directories
)


__all__ = [
    # Main service
    'PathConfigService',
    'get_path_config',
    'reset_path_config',

    # Models
    'CoreDirectories',
    'ArtifactDirectories',
    'PathConfiguration',
    'DeveloperPaths',

    # Resolver utilities
    'resolve_path',
    'resolve_env_path',
    'compute_developer_paths',

    # Directory management utilities
    'ensure_directory_exists',
    'ensure_directories_exist',
    'ensure_all_directories',
    'ensure_developer_directories',
]
