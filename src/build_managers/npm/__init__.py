"""
NPM Build Manager - Modularized Components

WHY: Backward compatibility wrapper for refactored NPM manager
RESPONSIBILITY: Re-export all components for seamless migration
PATTERNS: Facade pattern - single import point for all functionality

This module provides a unified interface to the modularized NPM manager
components, allowing existing code to continue working without modification.
"""

# Models and data structures
from .models import (
    PackageManager,
    NpmProjectInfo
)

# Specialized managers
from .config_parser import NpmConfigParser
from .version_manager import VersionManager
from .dependency_manager import DependencyManager
from .build_operations import BuildOperations

# CLI interface
from .cli_handlers import (
    handle_info,
    handle_build,
    handle_test,
    handle_install,
    handle_clean,
    get_command_handlers,
    create_argument_parser,
    execute_cli_command
)

# Main manager
from .manager_core import NpmManager

__all__ = [
    # Models
    'PackageManager',
    'NpmProjectInfo',

    # Component managers
    'NpmConfigParser',
    'VersionManager',
    'DependencyManager',
    'BuildOperations',

    # CLI handlers
    'handle_info',
    'handle_build',
    'handle_test',
    'handle_install',
    'handle_clean',
    'get_command_handlers',
    'create_argument_parser',
    'execute_cli_command',

    # Main manager
    'NpmManager'
]
