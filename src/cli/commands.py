"""
WHY: Implement all CLI command handlers with clean separation
RESPONSIBILITY: Execute CLI commands and return structured results
PATTERNS:
- Command pattern with dispatch table
- Guard clauses for early validation
- Single Responsibility: One handler per command
- Strategy pattern for prompt actions
"""

import sys
import os
import subprocess
import shutil
import json
from pathlib import Path
from typing import Dict, Any, List, Callable, Optional
from cli.models import CLIArguments, CommandResult, PromptAction, SystemStatus, LLMConfig
from cli.formatters import OutputFormatter, StatusFormatter, PromptFormatter


class CommandHandler:
    """
    Base class for command handlers

    Responsibilities:
    - Provide common error handling
    - Standardize command execution flow
    """

    def __init__(self, args: CLIArguments):
        """
        Initialize command handler

        Args:
            args: Parsed CLI arguments
        """
        self.args = args

    def execute(self) -> CommandResult:
        """
        Execute the command

        Returns:
            CommandResult with execution status
        """
        raise NotImplementedError("Subclasses must implement execute()")

    def _handle_exception(self, error: Exception) -> CommandResult:
        """
        Handle command exception

        Args:
            error: Exception that occurred

        Returns:
            Failure CommandResult
        """
        message = f"Error: {error}"
        if self.args.verbose:
            import traceback
            traceback.print_exc()

        return CommandResult.failure_result(message=message)


class InitPromptsCommand(CommandHandler):
    """Initialize all Artemis prompts with DEPTH framework"""

    def execute(self) -> CommandResult:
        """Execute init-prompts command"""
        print(OutputFormatter.header("Initializing Artemis Prompts"))

        try:
            from initialize_artemis_prompts import create_all_artemis_prompts, create_default_prompts
            from prompt_manager import PromptManager
            from rag_agent import RAGAgent
            from hydra import initialize, compose

            # Initialize Hydra to get RAG DB path
            with initialize(version_base=None, config_path="conf"):
                cfg = compose(config_name="config")
                rag_db_path = cfg.storage.rag_db_path

            print(f"\nUsing RAG database: {rag_db_path}")

            # Initialize RAG and PromptManager
            rag = RAGAgent(db_path=rag_db_path, verbose=self.args.verbose)
            pm = PromptManager(rag, verbose=self.args.verbose)

            # Create default prompts
            print("\nCreating default prompts...")
            create_default_prompts(pm)

            # Create all other Artemis prompts
            print("\nCreating Artemis-specific prompts...")
            create_all_artemis_prompts(pm)

            success_msg = OutputFormatter.success("PROMPTS INITIALIZED!")
            print(success_msg)
            print("\nYou can now query prompts from agents:")
            print("  prompt = pm.get_prompt('developer_conservative_implementation')")
            print("  rendered = pm.render_prompt(prompt, variables)")

            return CommandResult.success_result()

        except Exception as e:
            return self._handle_exception(e)


class TestConfigCommand(CommandHandler):
    """Test Hydra configuration and storage setup"""

    def execute(self) -> CommandResult:
        """Execute test-config command"""
        print(OutputFormatter.header("Testing Artemis Configuration"))

        try:
            from test_hydra_logging_storage import test_all

            # Run all tests
            success = test_all()

            if success:
                print("\nAll configuration tests passed!")
                return CommandResult.success_result()

            print("\nSome configuration tests failed")
            return CommandResult.failure_result()

        except Exception as e:
            return self._handle_exception(e)


class RunCommand(CommandHandler):
    """Run Artemis orchestrator on a task"""

    def execute(self) -> CommandResult:
        """Execute run command"""
        if not self.args.card_id:
            return CommandResult.failure_result(message="Card ID required")

        print(OutputFormatter.header(f"Running Artemis on task: {self.args.card_id}"))

        try:
            # Build command to run artemis_orchestrator.py
            cmd = self._build_command()

            # Run the command
            print("\nStarting Artemis pipeline...")
            result = subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))

            if result.returncode == 0:
                print("\nPipeline completed successfully!")
                return CommandResult.success_result()

            print(f"\nPipeline failed with exit code: {result.returncode}")
            return CommandResult.failure_result(exit_code=result.returncode)

        except Exception as e:
            return self._handle_exception(e)

    def _build_command(self) -> List[str]:
        """
        Build subprocess command for orchestrator

        Returns:
            Command as list of strings
        """
        cmd = [
            sys.executable,
            "artemis_orchestrator.py",
            "--card-id", self.args.card_id
        ]

        if self.args.full:
            cmd.append("--full")

        if self.args.resume:
            cmd.append("--resume")

        # Add Hydra overrides
        if self.args.overrides:
            cmd.extend(self.args.overrides)

        return cmd


class CleanupCommand(CommandHandler):
    """Clean up Artemis temporary files and reset state"""

    def execute(self) -> CommandResult:
        """Execute cleanup command"""
        print(OutputFormatter.header("Cleaning up Artemis workspace"))

        try:
            from hydra import initialize, compose

            # Get storage paths from config
            with initialize(version_base=None, config_path="conf"):
                cfg = compose(config_name="config")

                paths_to_clean = self._get_paths_to_clean(cfg)

                # Clean up paths
                for description, path in paths_to_clean.items():
                    if path is None:
                        continue

                    self._clean_path(description, path)

                print("\nCleanup complete!")

                if self.args.full_reset:
                    print("\nFull reset performed - all state and checkpoints cleared")
                elif self.args.keep_checkpoints:
                    print("\nCheckpoints preserved")

            return CommandResult.success_result()

        except Exception as e:
            return self._handle_exception(e)

    def _get_paths_to_clean(self, cfg: Any) -> Dict[str, Optional[str]]:
        """
        Get paths to clean based on arguments

        Args:
            cfg: Hydra configuration

        Returns:
            Dictionary of description -> path
        """
        return {
            "Temporary files": cfg.storage.temp_dir,
            "Checkpoints": cfg.storage.checkpoint_dir if not self.args.keep_checkpoints else None,
            "State files": cfg.storage.state_dir if self.args.full_reset else None,
        }

    def _clean_path(self, description: str, path: str) -> None:
        """
        Clean a single path

        Args:
            description: Path description for logging
            path: Path to clean
        """
        path_obj = Path(path)

        if not path_obj.exists():
            print(f"Skipping {description} (doesn't exist): {path}")
            return

        print(f"\nCleaning {description}: {path}")
        if path_obj.is_dir():
            shutil.rmtree(path_obj)
            path_obj.mkdir(parents=True, exist_ok=True)
        else:
            path_obj.unlink()


class StatusCommand(CommandHandler):
    """Show Artemis system status"""

    def execute(self) -> CommandResult:
        """Execute status command"""
        print(OutputFormatter.header("Artemis System Status"))

        try:
            from hydra import initialize, compose

            # Get configuration
            with initialize(version_base=None, config_path="conf"):
                cfg = compose(config_name="config")

                # Gather status information
                storage_paths = self._get_storage_paths(cfg)
                llm_config = self._get_llm_config(cfg)
                kanban_stats = self._get_kanban_stats()
                checkpoints = self._get_checkpoints(cfg)

                # Display status
                print(StatusFormatter.format_storage_paths(storage_paths))
                print(StatusFormatter.format_llm_config(llm_config))
                print(StatusFormatter.format_kanban_stats(kanban_stats))
                print(StatusFormatter.format_checkpoints(checkpoints))

            return CommandResult.success_result()

        except Exception as e:
            return self._handle_exception(e)

    def _get_storage_paths(self, cfg: Any) -> Dict[str, Dict[str, Any]]:
        """
        Get storage paths and their existence status

        Args:
            cfg: Hydra configuration

        Returns:
            Dictionary of path info
        """
        paths = {
            "RAG Database": cfg.storage.rag_db_path,
            "Temp Directory": cfg.storage.temp_dir,
            "Checkpoints": cfg.storage.checkpoint_dir,
            "State": cfg.storage.state_dir,
            "ADRs": cfg.storage.adr_dir,
            "Developer Output": cfg.storage.developer_output_dir,
            "Messages": cfg.storage.message_dir,
        }

        return {
            name: {"path": path, "exists": Path(path).exists()}
            for name, path in paths.items()
        }

    def _get_llm_config(self, cfg: Any) -> LLMConfig:
        """
        Get LLM configuration

        Args:
            cfg: Hydra configuration

        Returns:
            LLMConfig object
        """
        return LLMConfig(
            provider=cfg.llm.provider,
            model=cfg.llm.model
        )

    def _get_kanban_stats(self) -> Dict[str, Any]:
        """
        Get kanban board statistics

        Returns:
            Dictionary of kanban stats
        """
        kanban_path = Path("kanban_board.json")

        if not kanban_path.exists():
            return {}

        try:
            with open(kanban_path) as f:
                board = json.load(f)
                columns = board.get("columns", {})
                total_cards = sum(len(cards) for cards in columns.values())

                return {
                    "total_cards": total_cards,
                    "columns": {col_name: len(cards) for col_name, cards in columns.items()}
                }
        except Exception:
            return {}

    def _get_checkpoints(self, cfg: Any) -> List[str]:
        """
        Get list of recent checkpoints

        Args:
            cfg: Hydra configuration

        Returns:
            List of checkpoint filenames
        """
        checkpoint_dir = Path(cfg.storage.checkpoint_dir)

        if not checkpoint_dir.exists():
            return []

        checkpoints = sorted(
            checkpoint_dir.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        return [cp.name for cp in checkpoints[:5]]  # Return last 5


class PromptsCommand(CommandHandler):
    """Manage prompt templates"""

    def execute(self) -> CommandResult:
        """Execute prompts command"""
        print(OutputFormatter.header("Artemis Prompt Manager"))

        if not self.args.action:
            return CommandResult.failure_result(message="Action required")

        try:
            from prompt_manager import PromptManager
            from rag_agent import RAGAgent
            from hydra import initialize, compose

            # Initialize Hydra to get RAG DB path
            with initialize(version_base=None, config_path="conf"):
                cfg = compose(config_name="config")
                rag_db_path = cfg.storage.rag_db_path

            # Initialize RAG and PromptManager
            rag = RAGAgent(db_path=rag_db_path, verbose=False)
            pm = PromptManager(rag, verbose=False)

            # Dispatch to action handler
            action_handlers = self._get_action_handlers(pm)

            handler = action_handlers.get(self.args.action)
            if not handler:
                return CommandResult.failure_result(message=f"Unknown action: {self.args.action.value}")

            return handler()

        except Exception as e:
            return self._handle_exception(e)

    def _get_action_handlers(self, pm: Any) -> Dict[PromptAction, Callable[[], CommandResult]]:
        """
        Get dispatch table for prompt actions

        Args:
            pm: PromptManager instance

        Returns:
            Dictionary of action -> handler
        """
        return {
            PromptAction.LIST: lambda: self._handle_list(pm),
            PromptAction.SHOW: lambda: self._handle_show(pm),
            PromptAction.SEARCH: lambda: self._handle_search(pm),
        }

    def _handle_list(self, pm: Any) -> CommandResult:
        """
        Handle list action

        Args:
            pm: PromptManager instance

        Returns:
            CommandResult
        """
        prompts_by_category = {}

        for category in pm.PROMPT_CATEGORIES:
            prompts = pm.query_prompts(category=category, top_k=10)
            if prompts:
                prompts_by_category[category] = prompts

        output = PromptFormatter.format_prompt_list(prompts_by_category)
        print(output)

        return CommandResult.success_result()

    def _handle_show(self, pm: Any) -> CommandResult:
        """
        Handle show action

        Args:
            pm: PromptManager instance

        Returns:
            CommandResult
        """
        if not self.args.name:
            return CommandResult.failure_result(message="--name required for 'show' action")

        prompt = pm.get_prompt(self.args.name)
        if not prompt:
            return CommandResult.failure_result(message=f"Prompt not found: {self.args.name}")

        output = PromptFormatter.format_prompt_details(prompt)
        print(output)

        return CommandResult.success_result()

    def _handle_search(self, pm: Any) -> CommandResult:
        """
        Handle search action

        Args:
            pm: PromptManager instance

        Returns:
            CommandResult
        """
        if not self.args.query:
            return CommandResult.failure_result(message="--query required for 'search' action")

        results = pm.rag.query_similar(
            query_text=self.args.query,
            artifact_types=["prompt_template"],
            top_k=5
        )

        # Format results
        formatted_results = []
        for result in results:
            prompt_data = result["metadata"]["prompt_data"]
            prompt_data = json.loads(prompt_data) if isinstance(prompt_data, str) else prompt_data
            formatted_results.append({
                "prompt_data": prompt_data,
                "score": result["score"]
            })

        print(f"\nSearch results for: '{self.args.query}'")
        print(PromptFormatter.format_search_results(formatted_results))

        return CommandResult.success_result()


class CommandDispatcher:
    """
    Dispatches CLI commands to appropriate handlers

    Responsibilities:
    - Map CommandType to handler classes
    - Execute commands and return results
    """

    def __init__(self):
        """Initialize command dispatcher"""
        self.handlers = self._build_handler_map()

    def _build_handler_map(self) -> Dict[str, type]:
        """
        Build dispatch table for commands

        Returns:
            Dictionary of command type -> handler class
        """
        from cli.models import CommandType

        return {
            CommandType.INIT_PROMPTS: InitPromptsCommand,
            CommandType.TEST_CONFIG: TestConfigCommand,
            CommandType.RUN: RunCommand,
            CommandType.CLEANUP: CleanupCommand,
            CommandType.STATUS: StatusCommand,
            CommandType.PROMPTS: PromptsCommand,
        }

    def dispatch(self, args: CLIArguments) -> CommandResult:
        """
        Dispatch command to appropriate handler

        Args:
            args: Parsed CLI arguments

        Returns:
            CommandResult from handler
        """
        if not args.command:
            return CommandResult.failure_result(message="No command specified")

        handler_class = self.handlers.get(args.command)
        if not handler_class:
            return CommandResult.failure_result(message=f"Unknown command: {args.command}")

        handler = handler_class(args)
        return handler.execute()
