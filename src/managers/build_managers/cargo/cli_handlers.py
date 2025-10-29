"""
Module: managers/build_managers/cargo/cli_handlers.py

WHY: Handle CLI command routing for Cargo manager.
RESPONSIBILITY: Process command-line arguments and route to appropriate operations.
PATTERNS: Command Handler Pattern, Dispatch Tables, Guard Clauses.

This module contains:
- CLI command handlers (info, build, test, check, clippy, fmt, clean, add)
- Command dispatcher
- Argument parsing and validation

EXTRACTED FROM: cargo_manager.py (lines 478-597)
"""
import argparse
import json
import logging
import sys
from typing import Any, Callable, Dict
CargoManagerType = Any

def _get_command_handlers() -> Dict[str, Callable]:
    """
    Get command handler mapping.

    WHY: Use dispatch table instead of elif chains.
    RESPONSIBILITY: Return mapping of commands to handlers.

    Returns:
        Dict mapping command names to handler functions
    """
    return {'info': _handle_info_command, 'build': _handle_build_command, 'test': _handle_test_command, 'check': _handle_check_command, 'clippy': _handle_clippy_command, 'fmt': _handle_fmt_command, 'clean': _handle_clean_command, 'add': _handle_add_command}

def _handle_info_command(cargo: CargoManagerType) -> int:
    """
    Handle info command.

    WHY: Display project information from Cargo.toml.
    RESPONSIBILITY: Get and format project info as JSON.

    Args:
        cargo: CargoManager instance

    Returns:
        Exit code (0 for success)
    """
    info = cargo.get_project_info()
    
    logger.log(json.dumps(info, indent=2), 'INFO')
    return 0

def _handle_build_command(cargo: CargoManagerType, args: argparse.Namespace) -> int:
    """
    Handle build command.

    WHY: Build Rust project with specified options.
    RESPONSIBILITY: Parse features and execute build.

    Args:
        cargo: CargoManager instance
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    features = args.features.split(',') if args.features else None
    result = cargo.build(release=args.release, features=features)
    
    logger.log(result, 'INFO')
    return 0 if result.success else 1

def _handle_test_command(cargo: CargoManagerType, args: argparse.Namespace) -> int:
    """
    Handle test command.

    WHY: Execute Rust test suite.
    RESPONSIBILITY: Run tests with specified options.

    Args:
        cargo: CargoManager instance
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    result = cargo.test(release=args.release)
    
    logger.log(result, 'INFO')
    return 0 if result.success else 1

def _handle_check_command(cargo: CargoManagerType, args: argparse.Namespace) -> int:
    """
    Handle check command.

    WHY: Check project for errors without building.
    RESPONSIBILITY: Execute cargo check.

    Args:
        cargo: CargoManager instance
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    result = cargo.check()
    
    logger.log(result, 'INFO')
    return 0 if result.success else 1

def _handle_clippy_command(cargo: CargoManagerType, args: argparse.Namespace) -> int:
    """
    Handle clippy command.

    WHY: Run Rust linter.
    RESPONSIBILITY: Execute clippy.

    Args:
        cargo: CargoManager instance
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    result = cargo.clippy()
    
    logger.log(result, 'INFO')
    return 0 if result.success else 1

def _handle_fmt_command(cargo: CargoManagerType, args: argparse.Namespace) -> int:
    """
    Handle fmt command.

    WHY: Format Rust code.
    RESPONSIBILITY: Execute rustfmt.

    Args:
        cargo: CargoManager instance
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    result = cargo.fmt()
    
    logger.log(result, 'INFO')
    return 0 if result.success else 1

def _handle_clean_command(cargo: CargoManagerType, args: argparse.Namespace) -> int:
    """
    Handle clean command.

    WHY: Remove build artifacts.
    RESPONSIBILITY: Execute cargo clean.

    Args:
        cargo: CargoManager instance
        args: Parsed command-line arguments

    Returns:
        Exit code (always 0)
    """
    result = cargo.clean()
    
    logger.log(result, 'INFO')
    return 0

def _handle_add_command(cargo: CargoManagerType, args: argparse.Namespace) -> int:
    """
    Handle add command.

    WHY: Add crate dependency to project.
    RESPONSIBILITY: Validate crate name and add dependency.

    Args:
        cargo: CargoManager instance
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    if not args.crate:
        
        logger.log('Error: --crate required for add command', 'INFO')
        return 1
    cargo.install_dependency(args.crate, version=args.version, dev=args.dev)
    
    logger.log(f'Added {args.crate}', 'INFO')
    return 0

def run_cli() -> None:
    """
    Run CLI interface.

    WHY: Provide command-line interface for Cargo operations.
    RESPONSIBILITY: Parse arguments and dispatch to handlers.

    Example:
        $ python -m managers.build_managers.cargo.cli_handlers --project-dir . build --release
    """
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    parser = argparse.ArgumentParser(description='Cargo Manager')
    parser.add_argument('--project-dir', default='.', help='Project directory')
    parser.add_argument('command', choices=['info', 'build', 'test', 'check', 'clippy', 'fmt', 'clean', 'add'], help='Command to execute')
    parser.add_argument('--release', action='store_true', help='Release build')
    parser.add_argument('--features', help='Features to enable (comma-separated)')
    parser.add_argument('--crate', help='Crate to add')
    parser.add_argument('--version', help='Crate version')
    parser.add_argument('--dev', action='store_true', help='Add as dev dependency')
    args = parser.parse_args()
    try:
        from managers.build_managers.cargo.cargo_manager import CargoManager
        cargo = CargoManager(project_dir=args.project_dir)
        handlers = _get_command_handlers()
        handler = handlers.get(args.command)
        if not handler:
            logging.error(f'Unknown command: {args.command}')
            sys.exit(1)
        if args.command == 'info':
            exit_code = handler(cargo)
        else:
            exit_code = handler(cargo, args)
        sys.exit(exit_code)
    except Exception as e:
        logging.error(f'Error: {e}')
        sys.exit(1)
__all__ = ['run_cli']
if __name__ == '__main__':
    run_cli()