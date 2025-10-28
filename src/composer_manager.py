#!/usr/bin/env python3
"""
Composer Build Manager - Backward Compatibility Wrapper

WHY: Maintain backward compatibility during migration
RESPONSIBILITY: Re-export all components from modularized structure
PATTERNS: Facade pattern - transparent wrapper for legacy imports

This file provides backward compatibility for existing code that imports
from composer_manager.py. All components are now in build_managers/composer/
"""

# Re-export all components from the modularized structure
from build_managers.composer import (
    # Models
    DependencyType,
    StabilityFlag,
    ComposerProjectInfo,

    # Main manager
    ComposerManager,

    # Component managers (for advanced users)
    ComposerParser,
    DependencyManager,
    AutoloaderManager,
    VersionDetector,
    TestRunner,

    # CLI handlers
    execute_cli_command
)

# Make all exports available
__all__ = [
    'DependencyType',
    'StabilityFlag',
    'ComposerProjectInfo',
    'ComposerManager',
    'ComposerParser',
    'DependencyManager',
    'AutoloaderManager',
    'VersionDetector',
    'TestRunner',
    'execute_cli_command'
]


# CLI interface - maintain backward compatibility
if __name__ == "__main__":
    import argparse
    import logging
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    parser = argparse.ArgumentParser(description="Composer Manager")
    parser.add_argument("--project-dir", default=".", help="Project directory")
    parser.add_argument(
        "command",
        choices=[
            "info", "install", "test", "update", "require",
            "show", "validate", "dump-autoload", "diagnose", "clean"
        ],
        help="Command to execute"
    )
    parser.add_argument("--package", help="Package name")
    parser.add_argument("--version", help="Package version")
    parser.add_argument("--dev", action="store_true", help="Dev dependency")
    parser.add_argument("--no-dev", action="store_true", help="Skip dev dependencies")
    parser.add_argument("--optimize", action="store_true", help="Optimize autoloader")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    try:
        composer = ComposerManager(project_dir=args.project_dir)
        exit_code = execute_cli_command(args, composer)
        sys.exit(exit_code)
    except Exception as e:
        logging.error(f"Error: {e}")
        sys.exit(1)
