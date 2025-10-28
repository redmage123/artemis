"""
Composer Build Manager - Modularized Components

WHY: Backward compatibility wrapper for refactored Composer manager
RESPONSIBILITY: Re-export all components for seamless migration
PATTERNS: Facade pattern - single import point for all functionality

This module provides a unified interface to the modularized Composer manager
components, allowing existing code to continue working without modification.
"""

# Models and data structures
from .models import (
    DependencyType,
    StabilityFlag,
    ComposerProjectInfo
)

# Specialized managers
from .parser import ComposerParser
from .dependency_manager import DependencyManager
from .autoloader import AutoloaderManager
from .version_detector import VersionDetector
from .test_runner import TestRunner

# CLI interface
from .cli_handlers import (
    handle_info_command,
    handle_install_command,
    handle_test_command,
    handle_update_command,
    handle_require_command,
    handle_show_command,
    handle_validate_command,
    handle_dump_autoload_command,
    handle_diagnose_command,
    handle_clean_command,
    get_command_handlers,
    execute_cli_command
)

# Main manager
from .manager import ComposerManager

__all__ = [
    # Models
    'DependencyType',
    'StabilityFlag',
    'ComposerProjectInfo',

    # Component managers
    'ComposerParser',
    'DependencyManager',
    'AutoloaderManager',
    'VersionDetector',
    'TestRunner',

    # CLI handlers
    'handle_info_command',
    'handle_install_command',
    'handle_test_command',
    'handle_update_command',
    'handle_require_command',
    'handle_show_command',
    'handle_validate_command',
    'handle_dump_autoload_command',
    'handle_diagnose_command',
    'handle_clean_command',
    'get_command_handlers',
    'execute_cli_command',

    # Main manager
    'ComposerManager'
]
