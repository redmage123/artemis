#!/usr/bin/env python3
"""
.NET Manager CLI Interface

WHY: Provide command-line interface for .NET build operations.
RESPONSIBILITY: Parse arguments and dispatch to DotNetManager methods.
PATTERNS: Command pattern with dispatch table, Guard clauses.

Part of: managers.build_managers.dotnet
Dependencies: manager
"""

import argparse
import logging
import sys
import json
from typing import Callable, Dict

from managers.build_managers.dotnet.manager import DotNetManager


class DotNetCLI:
    """
    Command-line interface for .NET Manager.

    WHY: Enable standalone execution of .NET build operations.
    RESPONSIBILITY: Parse CLI arguments and execute operations.
    PATTERNS: Command pattern, Dispatch table pattern.
    """

    def __init__(self):
        """Initialize CLI with command dispatch table."""
        # Command dispatch table - no elif chains
        self.command_handlers: Dict[str, Callable] = {
            "info": self._handle_info,
            "build": self._handle_build,
            "test": self._handle_test,
            "restore": self._handle_restore,
            "publish": self._handle_publish,
            "run": self._handle_run,
            "clean": self._handle_clean,
            "add": self._handle_add,
        }

    def _handle_info(self, dotnet: DotNetManager, args: argparse.Namespace) -> None:
        """
        Handle 'info' command - display project metadata.

        WHY: Provide JSON output of project structure.

        Guards:
            - dotnet manager must be initialized
        """
        if not dotnet:
            print("Error: DotNetManager not initialized")
            sys.exit(1)

        info = dotnet.get_project_info()
        print(json.dumps(info, indent=2))

    def _handle_build(self, dotnet: DotNetManager, args: argparse.Namespace) -> None:
        """
        Handle 'build' command - compile project.

        WHY: Execute build with specified configuration.

        Guards:
            - dotnet manager must be initialized
        """
        if not dotnet:
            print("Error: DotNetManager not initialized")
            sys.exit(1)

        result = dotnet.build(
            configuration=args.configuration,
            framework=args.framework,
            runtime=args.runtime
        )
        print(result)
        sys.exit(0 if result.success else 1)

    def _handle_test(self, dotnet: DotNetManager, args: argparse.Namespace) -> None:
        """
        Handle 'test' command - run unit tests.

        WHY: Execute test suite with specified options.

        Guards:
            - dotnet manager must be initialized
        """
        if not dotnet:
            print("Error: DotNetManager not initialized")
            sys.exit(1)

        result = dotnet.test(
            configuration=args.configuration,
            verbosity=args.verbosity
        )
        print(result)
        sys.exit(0 if result.success else 1)

    def _handle_restore(self, dotnet: DotNetManager, args: argparse.Namespace) -> None:
        """
        Handle 'restore' command - download NuGet packages.

        WHY: Restore dependencies before build.

        Guards:
            - dotnet manager must be initialized
        """
        if not dotnet:
            print("Error: DotNetManager not initialized")
            sys.exit(1)

        result = dotnet.restore()
        print(result)
        sys.exit(0 if result.success else 1)

    def _handle_publish(self, dotnet: DotNetManager, args: argparse.Namespace) -> None:
        """
        Handle 'publish' command - create deployment artifacts.

        WHY: Publish application with specified runtime.

        Guards:
            - dotnet manager must be initialized
        """
        if not dotnet:
            print("Error: DotNetManager not initialized")
            sys.exit(1)

        result = dotnet.publish(
            configuration=args.configuration,
            framework=args.framework,
            runtime=args.runtime,
            output=args.output,
            self_contained=args.self_contained
        )
        print(result)
        sys.exit(0 if result.success else 1)

    def _handle_run(self, dotnet: DotNetManager, args: argparse.Namespace) -> None:
        """
        Handle 'run' command - execute application.

        WHY: Run application directly from source.

        Guards:
            - dotnet manager must be initialized
        """
        if not dotnet:
            print("Error: DotNetManager not initialized")
            sys.exit(1)

        result = dotnet.run(
            configuration=args.configuration,
            framework=args.framework
        )
        print(result)
        sys.exit(0 if result.success else 1)

    def _handle_clean(self, dotnet: DotNetManager, args: argparse.Namespace) -> None:
        """
        Handle 'clean' command - remove build artifacts.

        WHY: Clean intermediate files for fresh build.

        Guards:
            - dotnet manager must be initialized
        """
        if not dotnet:
            print("Error: DotNetManager not initialized")
            sys.exit(1)

        result = dotnet.clean()
        print(result)

    def _handle_add(self, dotnet: DotNetManager, args: argparse.Namespace) -> None:
        """
        Handle 'add' command - add NuGet package.

        WHY: Install new package dependency.

        Guards:
            - dotnet manager must be initialized
            - package argument must be provided
        """
        if not dotnet:
            print("Error: DotNetManager not initialized")
            sys.exit(1)

        if not args.package:
            print("Error: --package required for add command")
            sys.exit(1)

        dotnet.install_dependency(args.package, version=args.version)
        print(f"Added {args.package}")

    def run(self) -> None:
        """
        Execute CLI with parsed arguments.

        WHY: Main entry point for CLI execution.

        Guards:
            - Command must exist in dispatch table
        """
        parser = self._create_parser()
        args = parser.parse_args()

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Validate command
        if args.command not in self.command_handlers:
            print(f"Error: Unknown command '{args.command}'")
            sys.exit(1)

        try:
            # Initialize manager
            dotnet = DotNetManager(project_dir=args.project_dir)

            # Dispatch to handler
            handler = self.command_handlers[args.command]
            handler(dotnet, args)

        except Exception as e:
            logging.error(f"Error: {e}")
            sys.exit(1)

    def _create_parser(self) -> argparse.ArgumentParser:
        """
        Create argument parser with all commands and options.

        WHY: Centralize CLI argument definition.

        Returns:
            Configured ArgumentParser instance
        """
        parser = argparse.ArgumentParser(
            description=".NET Build Manager",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )

        parser.add_argument(
            "--project-dir",
            default=".",
            help="Project directory (default: current directory)"
        )

        parser.add_argument(
            "command",
            choices=list(self.command_handlers.keys()),
            help="Command to execute"
        )

        parser.add_argument(
            "--configuration", "-c",
            default="Debug",
            help="Build configuration (default: Debug)"
        )

        parser.add_argument(
            "--framework", "-f",
            help="Target framework (e.g., net8.0)"
        )

        parser.add_argument(
            "--runtime", "-r",
            help="Runtime identifier (e.g., linux-x64)"
        )

        parser.add_argument(
            "--package",
            help="Package name for 'add' command"
        )

        parser.add_argument(
            "--version", "-v",
            help="Package version for 'add' command"
        )

        parser.add_argument(
            "--output", "-o",
            help="Output directory for 'publish' command"
        )

        parser.add_argument(
            "--self-contained",
            action="store_true",
            help="Create self-contained deployment for 'publish'"
        )

        parser.add_argument(
            "--verbosity",
            choices=["q", "m", "n", "d", "diag"],
            help="Logging verbosity for 'test' command"
        )

        return parser


def main() -> None:
    """
    CLI entry point.

    WHY: Enable direct execution as script.
    """
    cli = DotNetCLI()
    cli.run()


if __name__ == "__main__":
    main()
