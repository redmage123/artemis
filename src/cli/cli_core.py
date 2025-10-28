"""
WHY: Orchestrate CLI execution flow with clean error handling
RESPONSIBILITY: Main entry point for CLI, coordinates parser and dispatcher
PATTERNS:
- Facade pattern for CLI subsystems
- Guard clauses for validation
- Single responsibility for CLI lifecycle management
"""

import sys
from typing import Optional, List
from cli.parser import ArgumentParser
from cli.commands import CommandDispatcher
from cli.models import CommandResult


class ArtemisCLI:
    """
    Main CLI orchestrator for Artemis tools

    Responsibilities:
    - Coordinate argument parsing
    - Dispatch commands to handlers
    - Handle top-level errors and signals
    - Provide unified exit handling
    """

    def __init__(self):
        """Initialize CLI components"""
        self.parser = ArgumentParser()
        self.dispatcher = CommandDispatcher()

    def run(self, args: Optional[List[str]] = None) -> int:
        """
        Run the CLI with given arguments

        Args:
            args: Optional command-line arguments (defaults to sys.argv)

        Returns:
            Exit code (0 for success, non-zero for failure)
        """
        try:
            # Parse arguments
            cli_args = self.parser.parse(args)

            # Handle no command case
            if not cli_args.command:
                self.parser.print_help()
                return 0

            # Dispatch command
            result = self.dispatcher.dispatch(cli_args)

            # Handle result
            return self._handle_result(result)

        except KeyboardInterrupt:
            print("\n\nInterrupted by user")
            return 130
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            import traceback
            traceback.print_exc()
            return 1

    def _handle_result(self, result: CommandResult) -> int:
        """
        Handle command result

        Args:
            result: CommandResult from command handler

        Returns:
            Exit code
        """
        if result.message:
            print(result.message)

        return result.exit_code


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for Artemis CLI

    Args:
        args: Optional command-line arguments

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    cli = ArtemisCLI()
    return cli.run(args)


if __name__ == "__main__":
    sys.exit(main())
