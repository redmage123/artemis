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
from java_ecosystem.cli.commands import handle_analyze, handle_build, handle_test

def main(argv: list=None) -> int:
    """
    Main CLI entry point.

    WHY: Facade pattern - single entry point for all CLI operations.

    Args:
        argv: Command-line arguments (defaults to sys.argv)

    Returns:
        Exit code (0 for success, 1 for error)
    """
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    parser = create_parser()
    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 0
    manager = JavaEcosystemManager(project_dir=args.project_dir)
    if not manager.is_java_project():
        
        logger.log('Error: Not a Java project', 'INFO')
        return 1
    return _execute_command(manager, args, parser)

def _execute_command(manager: JavaEcosystemManager, args: Any, parser: Any) -> int:
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
    COMMAND_HANDLERS = {'analyze': handle_analyze, 'build': handle_build, 'test': handle_test}
    handler = COMMAND_HANDLERS.get(args.command)
    if not handler:
        parser.print_help()
        return 0
    try:
        handler(manager, args)
        return 0
    except Exception as e:
        logging.error(f'Command failed: {e}')
        return 1
if __name__ == '__main__':
    sys.exit(main())