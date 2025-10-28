#!/usr/bin/env python3
"""
NPM/Yarn/PNPM Package Manager - Backward Compatibility Wrapper

WHY: Maintain backward compatibility during refactoring
RESPONSIBILITY: Re-export refactored components from build_managers/npm/
PATTERNS: Facade pattern, Module aliasing

This module serves as a backward compatibility wrapper for the refactored
NPM manager. All functionality has been moved to build_managers/npm/ but
existing imports will continue to work.

MIGRATION PATH:
    Old: from npm_manager import NpmManager, PackageManager
    New: from build_managers.npm import NpmManager, PackageManager

Both import styles are supported for seamless migration.
"""

# Re-export all components from refactored module
from build_managers.npm import (
    # Models
    PackageManager,
    NpmProjectInfo,

    # Component managers
    NpmConfigParser,
    VersionManager,
    DependencyManager,
    BuildOperations,

    # CLI handlers
    handle_info,
    handle_build,
    handle_test,
    handle_install,
    handle_clean,
    get_command_handlers,
    create_argument_parser,
    execute_cli_command,

    # Main manager
    NpmManager
)

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


# CLI interface
if __name__ == "__main__":
    import logging
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    parser = create_argument_parser()
    args = parser.parse_args()

    exit_code = execute_cli_command(args)
    sys.exit(exit_code)
