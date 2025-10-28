#!/usr/bin/env python3
"""
CLI Command Handlers for Composer Manager

WHY: Isolated CLI interface logic
RESPONSIBILITY: Handle command-line interface operations
PATTERNS:
- Command pattern: Each handler is a discrete command
- Dispatch table: Map commands to handlers
- Guard clauses: Validate inputs early
"""

from typing import Any, Dict, Callable
import json


def handle_info_command(composer: 'ComposerManager') -> int:
    """
    Handle info command - display project information.

    WHY: Show composer.json metadata
    RESPONSIBILITY: Format and display project info

    Args:
        composer: ComposerManager instance

    Returns:
        Exit code (0 for success)
    """
    info = composer.get_project_info()
    print(json.dumps(info, indent=2))
    return 0


def handle_install_command(composer: 'ComposerManager', args: Any) -> int:
    """
    Handle install command - install dependencies.

    WHY: Install all dependencies from composer.json
    RESPONSIBILITY: Execute install with user-specified options

    Args:
        composer: ComposerManager instance
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    result = composer.install(
        no_dev=args.no_dev,
        optimize_autoloader=args.optimize
    )
    print(result)
    return 0 if result.success else 1


def handle_test_command(composer: 'ComposerManager', args: Any) -> int:
    """
    Handle test command - run PHPUnit tests.

    WHY: Execute test suite
    RESPONSIBILITY: Run tests with user-specified options

    Args:
        composer: ComposerManager instance
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    result = composer.test(verbose=args.verbose)
    print(result)
    return 0 if result.success else 1


def handle_update_command(composer: 'ComposerManager', args: Any) -> int:
    """
    Handle update command - update dependencies.

    WHY: Update dependencies to latest versions
    RESPONSIBILITY: Execute update for all or specific package

    Args:
        composer: ComposerManager instance
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    result = composer.update(package=args.package)
    print(result)
    return 0 if result.success else 1


def handle_require_command(composer: 'ComposerManager', args: Any) -> int:
    """
    Handle require command - add package dependency.

    WHY: Add new package to project
    RESPONSIBILITY: Validate package and add to composer.json

    Args:
        composer: ComposerManager instance
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    if not args.package:
        print("Error: --package required for require command")
        return 1

    composer.install_dependency(args.package, version=args.version, dev=args.dev)
    print(f"Added {args.package}")
    return 0


def handle_show_command(composer: 'ComposerManager', args: Any) -> int:
    """
    Handle show command - display package information.

    WHY: Show package details and metadata
    RESPONSIBILITY: Display package information

    Args:
        composer: ComposerManager instance
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    result = composer.show(package=args.package)
    print(result.output)
    return 0


def handle_validate_command(composer: 'ComposerManager') -> int:
    """
    Handle validate command - validate composer.json.

    WHY: Check composer.json for errors
    RESPONSIBILITY: Execute validation and display results

    Args:
        composer: ComposerManager instance

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    result = composer.validate()
    print(result)
    return 0 if result.success else 1


def handle_dump_autoload_command(composer: 'ComposerManager', args: Any) -> int:
    """
    Handle dump-autoload command - regenerate autoloader.

    WHY: Update autoloader after file changes
    RESPONSIBILITY: Execute dump-autoload with optimization

    Args:
        composer: ComposerManager instance
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    result = composer.dump_autoload(optimize=args.optimize)
    print(result)
    return 0 if result.success else 1


def handle_diagnose_command(composer: 'ComposerManager') -> int:
    """
    Handle diagnose command - run diagnostics.

    WHY: Diagnose Composer and PHP setup issues
    RESPONSIBILITY: Execute diagnostics and display results

    Args:
        composer: ComposerManager instance

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    result = composer.diagnose()
    print(result)
    return 0 if result.success else 1


def handle_clean_command(composer: 'ComposerManager') -> int:
    """
    Handle clean command - clear Composer cache.

    WHY: Clear cache to resolve issues
    RESPONSIBILITY: Execute cache clear

    Args:
        composer: ComposerManager instance

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    result = composer.clean()
    print(result)
    return 0 if result.success else 1


def get_command_handlers() -> Dict[str, Callable]:
    """
    Get dispatch table of command handlers.

    WHY: Centralized command routing
    RESPONSIBILITY: Map command names to handler functions
    PATTERNS: Dispatch table pattern - replaces long if/elif chains

    Returns:
        Dictionary mapping command names to handler functions
    """
    return {
        "info": handle_info_command,
        "install": handle_install_command,
        "test": handle_test_command,
        "update": handle_update_command,
        "require": handle_require_command,
        "show": handle_show_command,
        "validate": handle_validate_command,
        "dump-autoload": handle_dump_autoload_command,
        "diagnose": handle_diagnose_command,
        "clean": handle_clean_command
    }


def execute_cli_command(args: Any, composer: 'ComposerManager') -> int:
    """
    Execute CLI command using dispatch table.

    WHY: Route commands to appropriate handlers
    RESPONSIBILITY: Look up and execute command handler

    Args:
        args: Parsed command-line arguments
        composer: ComposerManager instance

    Returns:
        Exit code from handler

    PATTERNS: Dispatch table - eliminates if/elif chains
    """
    handlers = get_command_handlers()
    handler = handlers.get(args.command)

    if not handler:
        print(f"Unknown command: {args.command}")
        return 1

    # Some handlers need args, some don't
    handler_params = handler.__code__.co_varnames
    if 'args' in handler_params:
        return handler(composer, args)
    else:
        return handler(composer)
