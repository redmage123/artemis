"""
WHY: Parse command-line arguments into typed structures
RESPONSIBILITY: Convert raw CLI input into validated CLIArguments objects
PATTERNS:
- Builder pattern for argument parser configuration
- Guard clauses for validation
- Type conversion to domain models
"""

import argparse
from typing import Optional, List
from cli.models import CLIArguments, CommandType, PromptAction


class ArgumentParser:
    """
    Builds and configures argument parser for Artemis CLI

    Responsibilities:
    - Configure argparse with all commands and options
    - Convert argparse Namespace to CLIArguments
    - Provide help and usage information
    """

    def __init__(self):
        """Initialize the argument parser"""
        self.parser = self._build_parser()

    def _build_parser(self) -> argparse.ArgumentParser:
        """
        Build the complete argument parser

        Returns:
            Configured ArgumentParser instance
        """
        parser = argparse.ArgumentParser(
            description="Artemis CLI - Unified interface for Artemis tools",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )

        parser.add_argument(
            "-v", "--verbose",
            action="store_true",
            help="Enable verbose output"
        )

        subparsers = parser.add_subparsers(dest="command", help="Command to run")

        self._add_init_prompts_command(subparsers)
        self._add_test_config_command(subparsers)
        self._add_run_command(subparsers)
        self._add_cleanup_command(subparsers)
        self._add_status_command(subparsers)
        self._add_prompts_command(subparsers)

        return parser

    def _add_init_prompts_command(self, subparsers) -> None:
        """Add init-prompts command"""
        parser = subparsers.add_parser(
            "init-prompts",
            help="Initialize all prompts with DEPTH framework"
        )
        parser.set_defaults(command_type=CommandType.INIT_PROMPTS)

    def _add_test_config_command(self, subparsers) -> None:
        """Add test-config command"""
        parser = subparsers.add_parser(
            "test-config",
            help="Test Hydra configuration and storage"
        )
        parser.set_defaults(command_type=CommandType.TEST_CONFIG)

    def _add_run_command(self, subparsers) -> None:
        """Add run command"""
        parser = subparsers.add_parser(
            "run",
            help="Run Artemis orchestrator on a task"
        )
        parser.add_argument(
            "card_id",
            help="Card ID to process"
        )
        parser.add_argument(
            "--full",
            action="store_true",
            help="Run full pipeline"
        )
        parser.add_argument(
            "--resume",
            action="store_true",
            help="Resume from checkpoint"
        )
        parser.add_argument(
            "--override",
            dest="overrides",
            action="append",
            help="Hydra config overrides (e.g., llm.model=gpt-4o)"
        )
        parser.set_defaults(command_type=CommandType.RUN)

    def _add_cleanup_command(self, subparsers) -> None:
        """Add cleanup command"""
        parser = subparsers.add_parser(
            "cleanup",
            help="Clean up temporary files and reset state"
        )
        parser.add_argument(
            "--full-reset",
            action="store_true",
            help="Full reset including state files"
        )
        parser.add_argument(
            "--keep-checkpoints",
            action="store_true",
            help="Keep checkpoint files"
        )
        parser.set_defaults(command_type=CommandType.CLEANUP)

    def _add_status_command(self, subparsers) -> None:
        """Add status command"""
        parser = subparsers.add_parser(
            "status",
            help="Show Artemis system status"
        )
        parser.set_defaults(command_type=CommandType.STATUS)

    def _add_prompts_command(self, subparsers) -> None:
        """Add prompts command"""
        parser = subparsers.add_parser(
            "prompts",
            help="Manage prompt templates"
        )
        parser.add_argument(
            "action",
            choices=["list", "show", "search"],
            help="Action to perform"
        )
        parser.add_argument(
            "--name",
            help="Prompt name (for 'show' action)"
        )
        parser.add_argument(
            "--query",
            help="Search query (for 'search' action)"
        )
        parser.set_defaults(command_type=CommandType.PROMPTS)

    def parse(self, args: Optional[List[str]] = None) -> CLIArguments:
        """
        Parse command-line arguments

        Args:
            args: Optional list of arguments (default: sys.argv)

        Returns:
            Parsed CLIArguments object
        """
        namespace = self.parser.parse_args(args)
        return self._namespace_to_cli_arguments(namespace)

    def _namespace_to_cli_arguments(self, namespace: argparse.Namespace) -> CLIArguments:
        """
        Convert argparse Namespace to CLIArguments

        Args:
            namespace: Parsed argparse Namespace

        Returns:
            Typed CLIArguments object
        """
        # Extract common arguments
        command = getattr(namespace, 'command_type', None)
        verbose = getattr(namespace, 'verbose', False)

        # Extract run command arguments
        card_id = getattr(namespace, 'card_id', None)
        full = getattr(namespace, 'full', False)
        resume = getattr(namespace, 'resume', False)
        overrides = getattr(namespace, 'overrides', None) or []

        # Extract cleanup command arguments
        full_reset = getattr(namespace, 'full_reset', False)
        keep_checkpoints = getattr(namespace, 'keep_checkpoints', False)

        # Extract prompts command arguments
        action_str = getattr(namespace, 'action', None)
        action = PromptAction(action_str) if action_str else None
        name = getattr(namespace, 'name', None)
        query = getattr(namespace, 'query', None)

        return CLIArguments(
            command=command,
            verbose=verbose,
            card_id=card_id,
            full=full,
            resume=resume,
            overrides=overrides,
            full_reset=full_reset,
            keep_checkpoints=keep_checkpoints,
            action=action,
            name=name,
            query=query
        )

    def print_help(self) -> None:
        """Print help message"""
        self.parser.print_help()
