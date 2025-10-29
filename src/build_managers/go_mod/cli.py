"""
Go Modules Manager - CLI Interface

WHY: Separate CLI logic from core manager
RESPONSIBILITY: Provide command-line interface for Go operations
PATTERNS: Command pattern, dispatch table, argument parsing
"""
import argparse
import logging
import sys
import json
from typing import Callable, Dict
from .manager import GoModManager

class GoModCLI:
    """
    WHY: Encapsulate CLI logic
    RESPONSIBILITY: Parse arguments and execute commands
    PATTERNS: Command pattern, dispatch table
    """

    def __init__(self):
        """
        WHY: Initialize CLI with command handlers
        RESPONSIBILITY: Set up logging and command dispatch table
        PATTERNS: Dispatch table over elif chains
        """
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.command_handlers: Dict[str, Callable] = {'info': self._handle_info, 'build': self._handle_build, 'test': self._handle_test, 'get': self._handle_get, 'download': self._handle_download, 'tidy': self._handle_tidy, 'verify': self._handle_verify, 'fmt': self._handle_fmt, 'vet': self._handle_vet, 'clean': self._handle_clean}

    def run(self, argv=None):
        """
        WHY: Main entry point for CLI
        RESPONSIBILITY: Parse arguments and execute commands
        PATTERNS: Guard clause, dispatch table

        Args:
            argv: Command line arguments (for testing)

        Returns:
            Exit code
        """
        args = self._parse_arguments(argv)
        try:
            go_mod = GoModManager(project_dir=args.project_dir)
            handler = self.command_handlers.get(args.command)
            if not handler:
                logging.error(f'Unknown command: {args.command}')
                return 1
            exit_code = handler(go_mod, args)
            return exit_code
        except Exception as e:
            logging.error(f'Error: {e}')
            return 1

    def _parse_arguments(self, argv=None):
        """
        WHY: Parse command line arguments
        RESPONSIBILITY: Define and parse CLI arguments
        PATTERNS: Argument parser pattern

        Args:
            argv: Command line arguments (for testing)

        Returns:
            Parsed arguments
        """
        parser = argparse.ArgumentParser(description='Go Modules Manager')
        parser.add_argument('--project-dir', default='.', help='Project directory')
        parser.add_argument('command', choices=list(self.command_handlers.keys()), help='Command to execute')
        parser.add_argument('--output', help='Output binary name')
        parser.add_argument('--tags', help='Build tags (comma-separated)')
        parser.add_argument('--module', help='Module to add')
        parser.add_argument('--version', help='Module version')
        parser.add_argument('--package', help='Package to test')
        parser.add_argument('--verbose', action='store_true', help='Verbose output')
        parser.add_argument('--race', action='store_true', help='Enable race detector')
        parser.add_argument('--cover', action='store_true', help='Enable coverage')
        return parser.parse_args(argv)

    @staticmethod
    def _handle_info(go_mod, args):
        """
        WHY: Handle info command
        RESPONSIBILITY: Display project information
        PATTERNS: Static method for simple handler
        """
        info = go_mod.get_project_info()
        
        logger.log(json.dumps(info, indent=2), 'INFO')
        return 0

    @staticmethod
    def _handle_build(go_mod, args):
        """
        WHY: Handle build command
        RESPONSIBILITY: Execute build with parsed arguments
        PATTERNS: Guard clause for tag parsing
        """
        tags = args.tags.split(',') if args.tags else None
        result = go_mod.build(output=args.output, tags=tags, race=args.race)
        
        logger.log(result, 'INFO')
        return 0 if result.success else 1

    @staticmethod
    def _handle_test(go_mod, args):
        """
        WHY: Handle test command
        RESPONSIBILITY: Execute tests with parsed arguments
        PATTERNS: Static method for simple handler
        """
        result = go_mod.test(package=args.package, verbose=args.verbose, race=args.race, cover=args.cover)
        
        logger.log(result, 'INFO')
        return 0 if result.success else 1

    @staticmethod
    def _handle_get(go_mod, args):
        """
        WHY: Handle get command
        RESPONSIBILITY: Install dependency
        PATTERNS: Guard clause for required argument
        """
        if not args.module:
            
            logger.log('Error: --module required for get command', 'INFO')
            return 1
        go_mod.install_dependency(args.module, version=args.version)
        
        logger.log(f'Added {args.module}', 'INFO')
        return 0

    @staticmethod
    def _handle_download(go_mod, args):
        """
        WHY: Handle download command
        RESPONSIBILITY: Download dependencies
        PATTERNS: Static method for simple handler
        """
        result = go_mod.download_dependencies()
        
        logger.log(result, 'INFO')
        return 0 if result.success else 1

    @staticmethod
    def _handle_tidy(go_mod, args):
        """
        WHY: Handle tidy command
        RESPONSIBILITY: Tidy dependencies
        PATTERNS: Static method for simple handler
        """
        result = go_mod.tidy()
        
        logger.log(result, 'INFO')
        return 0 if result.success else 1

    @staticmethod
    def _handle_verify(go_mod, args):
        """
        WHY: Handle verify command
        RESPONSIBILITY: Verify dependencies
        PATTERNS: Static method for simple handler
        """
        result = go_mod.verify()
        
        logger.log(result, 'INFO')
        return 0 if result.success else 1

    @staticmethod
    def _handle_fmt(go_mod, args):
        """
        WHY: Handle fmt command
        RESPONSIBILITY: Format code
        PATTERNS: Static method for simple handler
        """
        result = go_mod.fmt()
        
        logger.log(result, 'INFO')
        return 0 if result.success else 1

    @staticmethod
    def _handle_vet(go_mod, args):
        """
        WHY: Handle vet command
        RESPONSIBILITY: Run static analysis
        PATTERNS: Static method for simple handler
        """
        result = go_mod.vet()
        
        logger.log(result, 'INFO')
        return 0 if result.success else 1

    @staticmethod
    def _handle_clean(go_mod, args):
        """
        WHY: Handle clean command
        RESPONSIBILITY: Clean build cache
        PATTERNS: Static method for simple handler
        """
        result = go_mod.clean()
        
        logger.log(result, 'INFO')
        return 0

def main():
    """
    WHY: Entry point for CLI
    RESPONSIBILITY: Run CLI and exit with proper code
    PATTERNS: Simple entry point
    """
    cli = GoModCLI()
    sys.exit(cli.run())
if __name__ == '__main__':
    main()