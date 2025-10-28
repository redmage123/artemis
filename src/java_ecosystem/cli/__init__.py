#!/usr/bin/env python3
"""
WHY: CLI entry point for Java ecosystem management
RESPONSIBILITY: Coordinate parser, commands, and error handling
PATTERNS: Facade (unified CLI interface), Dispatch Table (command routing)

CLI module provides command-line interface for JavaEcosystemManager.
"""

import sys
import logging
from typing import Any
from java_ecosystem import JavaEcosystemManager
from java_ecosystem.cli.parser import create_parser
from java_ecosystem.cli.commands import (
    handle_analyze,
    handle_build,
    handle_test
)


def main(argv: list = None) -> int:
    """
    Main CLI entry point.

    WHY: Facade pattern - single entry point for all CLI operations.

    Args:
        argv: Command-line arguments (defaults to sys.argv)

    Returns:
        Exit code (0 for success, 1 for error)
    """
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )

    # Parse arguments
    parser = create_parser()
    args = parser.parse_args(argv)

    # Guard clause - no command specified
    if not args.command:
        parser.print_help()
        return 0

    # Create manager
    manager = JavaEcosystemManager(project_dir=args.project_dir)

    # Guard clause - not a Java project
    if not manager.is_java_project():
        print("Error: Not a Java project")
        return 1

    # Execute command using dispatch table (avoid if/elif chain)
    return _execute_command(manager, args, parser)


def _execute_command(
    manager: JavaEcosystemManager,
    args: Any,
    parser: Any
) -> int:
    """
    Execute CLI command using dispatch table.

    WHY: Strategy pattern with dispatch table avoids if/elif chain.
         Follows Open/Closed principle - new commands added to table.

    Args:
        manager: JavaEcosystemManager instance
        args: Parsed arguments
        parser: ArgumentParser for help display

    Returns:
        Exit code (0 for success, 1 for error)
    """
    # Command dispatch table (Strategy pattern)
    COMMAND_HANDLERS = {
        'analyze': handle_analyze,
        'build': handle_build,
        'test': handle_test
    }

    handler = COMMAND_HANDLERS.get(args.command)

    # Guard clause - unknown command
    if not handler:
        parser.print_help()
        return 0

    # Execute command with error handling
    try:
        handler(manager, args)
        return 0
    except Exception as e:
        logging.error(f"Command failed: {e}")
        return 1


# Allow direct execution
if __name__ == "__main__":
    sys.exit(main())
