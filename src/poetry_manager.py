#!/usr/bin/env python3
"""
Poetry Package Manager - Backward Compatibility Wrapper

WHY: Maintain backward compatibility during modularization
RESPONSIBILITY: Re-export refactored Poetry manager components
PATTERNS: Facade pattern - transparent migration path

This module serves as a backward compatibility wrapper for the refactored
Poetry manager. All functionality has been moved to build_managers/poetry/
but existing imports continue to work.

MIGRATION PATH:
- Old: from poetry_manager import PoetryManager
- New: from build_managers.poetry import PoetryManager

Both imports work identically. The old import path will be maintained
for backward compatibility.

Design Patterns:
- Template Method: Inherits from BuildManagerBase
- Exception Wrapper: All errors properly wrapped
- Strategy Pattern: Modern Python dependency management
"""

# Re-export all components from modularized package
from build_managers.poetry import (
    # Models
    DependencyGroup,
    PoetryProjectInfo,

    # Component managers
    PoetryConfigParser,
    DependencyManager,
    BuildOperations,
    VersionManager,

    # CLI handlers
    handle_info_command,
    handle_build_command,
    handle_test_command,
    handle_install_command,
    handle_update_command,
    handle_add_command,
    handle_show_command,
    handle_run_command,
    get_command_handlers,
    execute_cli_command,

    # Main manager
    PoetryManager
)

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


# CLI interface (preserved for backward compatibility)
if __name__ == "__main__":
    import argparse
    import logging
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    parser = argparse.ArgumentParser(description="Poetry Manager")
    parser.add_argument("--project-dir", default=".", help="Project directory")
    parser.add_argument(
        "command",
        choices=list(get_command_handlers().keys()),
        help="Command to execute"
    )
    parser.add_argument("--package", help="Package name")
    parser.add_argument("--version", help="Package version")
    parser.add_argument("--group", default="main", help="Dependency group")
    parser.add_argument("--format", default="wheel", help="Build format")
    parser.add_argument("--script", help="Script name to run")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    try:
        poetry = PoetryManager(project_dir=args.project_dir)
        execute_cli_command(args.command, poetry, args)

    except Exception as e:
        logging.error(f"Error: {e}")
        sys.exit(1)
