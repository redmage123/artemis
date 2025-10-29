"""
NPM Build Manager - CLI Handlers

WHY: Handle command-line interface operations
RESPONSIBILITY: Process CLI commands and format output
PATTERNS: Command pattern, Handler pattern, Dispatch table

This module provides CLI command handlers for the NPM manager,
enabling command-line usage of the NPM build system.
"""
import argparse
import json
import sys
from typing import Dict, Callable, Any
import logging
from .manager_core import NpmManager

def handle_info(npm: NpmManager, args: argparse.Namespace) -> int:
    """
    Handle info command.

    WHY: Display project information from package.json
    PATTERNS: Command handler pattern

    Args:
        npm: NpmManager instance
        args: Command arguments

    Returns:
        Exit code (0 for success)
    """
    info = npm.get_project_info()
    
    logger.log(json.dumps(info, indent=2), 'INFO')
    return 0

def handle_build(npm: NpmManager, args: argparse.Namespace) -> int:
    """
    Handle build command.

    WHY: Execute build script
    PATTERNS: Command handler pattern, Guard clause for result

    Args:
        npm: NpmManager instance
        args: Command arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    result = npm.build(script_name=args.script, production=args.production)
    
    logger.log(result, 'INFO')
    return 0 if result.success else 1

def handle_test(npm: NpmManager, args: argparse.Namespace) -> int:
    """
    Handle test command.

    WHY: Execute test suite
    PATTERNS: Command handler pattern, Guard clause for result

    Args:
        npm: NpmManager instance
        args: Command arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    result = npm.test(coverage=args.coverage)
    
    logger.log(result, 'INFO')
    return 0 if result.success else 1

def handle_install(npm: NpmManager, args: argparse.Namespace) -> int:
    """
    Handle install command.

    WHY: Install dependencies or specific package
    PATTERNS: Command handler pattern, Guard clause for package

    Args:
        npm: NpmManager instance
        args: Command arguments

    Returns:
        Exit code (0 for success)
    """
    if args.package:
        npm.install_dependency(args.package, version=args.version, dev=args.dev)
        
        logger.log(f'Installed {args.package}', 'INFO')
        return 0
    result = npm.install_dependencies(production=args.production)
    
    logger.log(result, 'INFO')
    return 0

def handle_clean(npm: NpmManager, args: argparse.Namespace) -> int:
    """
    Handle clean command.

    WHY: Clean build artifacts
    PATTERNS: Command handler pattern

    Args:
        npm: NpmManager instance
        args: Command arguments

    Returns:
        Exit code (0 for success)
    """
    result = npm.clean()
    
    logger.log(result, 'INFO')
    return 0

def get_command_handlers() -> Dict[str, Callable]:
    """
    Get command handler dispatch table.

    WHY: Centralize command routing
    PATTERNS: Dispatch table pattern

    Returns:
        Dictionary mapping command names to handler functions
    """
    return {'info': handle_info, 'build': handle_build, 'test': handle_test, 'install': handle_install, 'clean': handle_clean}

def create_argument_parser() -> argparse.ArgumentParser:
    """
    Create CLI argument parser.

    WHY: Centralize argument parsing configuration
    PATTERNS: Builder pattern

    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(description='npm/yarn/pnpm Manager')
    parser.add_argument('--project-dir', default='.', help='Project directory')
    parser.add_argument('command', choices=['info', 'build', 'test', 'install', 'clean'], help='Command to execute')
    parser.add_argument('--script', default='build', help='Script name for build command')
    parser.add_argument('--production', action='store_true', help='Production mode')
    parser.add_argument('--coverage', action='store_true', help='Generate coverage')
    parser.add_argument('--package', help='Package to install')
    parser.add_argument('--version', help='Package version')
    parser.add_argument('--dev', action='store_true', help='Install as dev dependency')
    return parser

def execute_cli_command(args: argparse.Namespace) -> int:
    """
    Execute CLI command with error handling.

    WHY: Centralize command execution and error handling
    PATTERNS: Command pattern, Guard clause for errors

    Args:
        args: Parsed command arguments

    Returns:
        Exit code
    """
    try:
        npm = NpmManager(project_dir=args.project_dir)
        handlers = get_command_handlers()
        handler = handlers.get(args.command)
        if not handler:
            logging.error(f'Unknown command: {args.command}')
            return 1
        return handler(npm, args)
    except Exception as e:
        logging.error(f'Error: {e}')
        return 1
__all__ = ['handle_info', 'handle_build', 'handle_test', 'handle_install', 'handle_clean', 'get_command_handlers', 'create_argument_parser', 'execute_cli_command']