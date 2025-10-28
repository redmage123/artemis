"""
Poetry Build Manager - Modularized Components

WHY: Backward compatibility wrapper for refactored Poetry manager
RESPONSIBILITY: Re-export all components for seamless migration
PATTERNS: Facade pattern - single import point for all functionality

This module provides a unified interface to the modularized Poetry manager
components, allowing existing code to continue working without modification.
"""

# Models and data structures
from .models import (
    DependencyGroup,
    PoetryProjectInfo
)

# Specialized managers
from .config_parser import PoetryConfigParser
from .dependency_manager import DependencyManager
from .build_operations import BuildOperations
from .version_manager import VersionManager

# CLI interface
from .cli_handlers import (
    handle_info_command,
    handle_build_command,
    handle_test_command,
    handle_install_command,
    handle_update_command,
    handle_add_command,
    handle_show_command,
    handle_run_command,
    get_command_handlers,
    execute_cli_command
)

# Main manager
from .manager_core import PoetryManager

__all__ = [
    # Models
    'DependencyGroup',
    'PoetryProjectInfo',

    # Component managers
    'PoetryConfigParser',
    'DependencyManager',
    'BuildOperations',
    'VersionManager',

    # CLI handlers
    'handle_info_command',
    'handle_build_command',
    'handle_test_command',
    'handle_install_command',
    'handle_update_command',
    'handle_add_command',
    'handle_show_command',
    'handle_run_command',
    'get_command_handlers',
    'execute_cli_command',

    # Main manager
    'PoetryManager'
]
