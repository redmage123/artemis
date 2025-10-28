#!/usr/bin/env python3
"""
DevelopmentStage

Extracted from artemis_stages.py for strict Single Responsibility Principle compliance.
Each stage has its own file for independent testing and evolution.
"""

#!/usr/bin/env python3
"""
Artemis Stage Implementations (SOLID Principles)

Each stage class follows SOLID:
- Single Responsibility: ONE stage, ONE responsibility
- Open/Closed: Can add new stages without modifying existing
- Liskov Substitution: All stages implement PipelineStage interface
- Interface Segregation: Minimal, focused interfaces
- Dependency Inversion: Stages depend on injected abstractions
"""

import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from artemis_stage_interface import PipelineStage, LoggerInterface
from artemis_services import TestRunner, FileManager
from kanban_manager import KanbanBoard
from agent_messenger import AgentMessenger
from rag_agent import RAGAgent
from developer_invoker import DeveloperInvoker
from project_analysis_agent import ProjectAnalysisEngine, UserApprovalHandler
from artemis_exceptions import (
    FileReadError,
    ADRGenerationError,
    wrap_exception
)

# Import PromptManager for RAG-based prompts
try:
    from prompt_manager import PromptManager
    PROMPT_MANAGER_AVAILABLE = True
except ImportError:
    PROMPT_MANAGER_AVAILABLE = False
from supervised_agent_mixin import SupervisedStageMixin
from debug_mixin import DebugMixin
from knowledge_graph_factory import get_knowledge_graph

# Import centralized AI Query Service
from ai_query_service import (
    AIQueryService,
    create_ai_query_service,
    QueryType,
    AIQueryResult
)


# ============================================================================
# PROJECT ANALYSIS STAGE (Pre-Implementation Review)
# ============================================================================


class DevelopmentStage(PipelineStage, SupervisedStageMixin, DebugMixin):
    """
    Single Responsibility: Invoke parallel developers

    This stage ONLY invokes developers - nothing else.
    Uses DeveloperInvoker to launch autonomous developer agents.

    Integrates with supervisor for:
    - LLM cost tracking
    - Code execution sandboxing
    - Unexpected state handling and recovery
    - Automatic heartbeat and health monitoring
    """

    def __init__(
        self,
        board: KanbanBoard,
        rag: RAGAgent,
        logger: LoggerInterface,
        observable: Optional['PipelineObservable'] = None,
        supervisor: Optional['SupervisorAgent'] = None,
        git_agent: Optional['GitAgent'] = None
    ):
        # Initialize PipelineStage
        PipelineStage.__init__(self)

        # Initialize SupervisedStageMixin for health monitoring
        SupervisedStageMixin.__init__(
            self,
            supervisor=supervisor,
            stage_name="DevelopmentStage",
            heartbeat_interval=15
        )

        # Initialize DebugMixin
        DebugMixin.__init__(self, component_name="development")

        self.board = board
        self.rag = rag
        self.logger = logger
        self.observable = observable
        self.supervisor = supervisor
        self.git_agent = git_agent  # Git Agent for autonomous repository operations
        self.invoker = DeveloperInvoker(logger, observable=observable)

    def execute(self, card: Dict, context: Dict) -> Dict:
        """Execute with supervisor monitoring"""
        metadata = {
            "task_id": card.get('card_id'),
            "stage": "development"
        }

        with self.supervised_execution(metadata):
            return self._do_work(card, context)

    def _do_work(self, card: Dict, context: Dict) -> Dict:
        """Internal method - invokes developers and tracks their work"""
        stage_name = "development"
        self.logger.log("Starting Development Stage", "STAGE")

        card_id = card['card_id']
        num_developers = context.get('parallel_developers', 1)

        # DEBUG: Log stage entry
        self.debug_log("Starting development stage", card_id=card_id, num_developers=num_developers)

        # Update progress: starting
        self.update_progress({"step": "starting", "progress_percent": 10})

        # Create feature branch if git_agent is configured
        feature_branch = None
        if self.git_agent:
            try:
                card_title = card.get('title', 'feature').lower().replace(' ', '-')
                feature_branch = self.git_agent.create_feature_branch(
                    feature_name=card_title,
                    card_id=card_id
                )
                self.logger.log(f"Created feature branch: {feature_branch}", "INFO")
            except Exception as e:
                self.logger.log(f"Failed to create feature branch: {e}", "WARNING")
                # Continue without git operations

        # Register stage with supervisor
        if self.supervisor:
            from supervisor_agent import RecoveryStrategy
            self.supervisor.register_stage(
                stage_name=stage_name,
                recovery_strategy=RecoveryStrategy(
                    max_retries=3,
                    retry_delay_seconds=10,
                    timeout_seconds=600,  # 10 minutes for developers
                    circuit_breaker_threshold=5
                )
            )

        try:
            # Get ADR from context
            self.update_progress({"step": "reading_adr", "progress_percent": 20})
            adr_file = context.get('adr_file', '')
            adr_content = self._read_adr(adr_file)

            # Invoke developers in parallel
            self.update_progress({"step": "invoking_developers", "progress_percent": 30})
            self.logger.log(f"Invoking {num_developers} parallel developer(s)...", "INFO")

            # DEBUG: Track developer invocation with context manager
            with self.debug_section("Developer Invocation"):
                self.debug_if_enabled('log_developers', f"Invoking {num_developers} developers",
                                     adr_file=adr_file)

                developer_results = self.invoker.invoke_parallel_developers(
                    num_developers=num_developers,
                    card=card,
                    adr_content=adr_content,
                    adr_file=adr_file,
                    rag_agent=self.rag  # Pass RAG agent so developers can query feedback
                )

                # DEBUG: Dump developer results
                self.debug_dump_if_enabled('dump_dev_results', "Developer Results", {
                    "count": len(developer_results),
                    "successful": sum(1 for r in developer_results if r.get('success', False)),
                    "developers": [r.get('developer', 'unknown') for r in developer_results]
                })

            # Track LLM costs for each developer
            self.update_progress({"step": "tracking_llm_costs", "progress_percent": 50})
            self._track_developer_llm_costs(developer_results, stage_name)

            # Execute developer code in sandbox (if supervisor has sandboxing enabled)
            self.update_progress({"step": "sandboxing_code", "progress_percent": 65})
            self._execute_in_sandbox_if_enabled(developer_results)

            # Store each developer's solution in RAG
            self.update_progress({"step": "storing_in_rag", "progress_percent": 80})
            for dev_result in developer_results:
                self._store_developer_solution_in_rag(card_id, card, dev_result)

            # Store development artifacts in Knowledge Graph
            self._store_development_in_knowledge_graph(card_id, developer_results)

            # Check if we have any successful developers
            self.update_progress({"step": "checking_results", "progress_percent": 90})
            successful_devs = [r for r in developer_results if r.get("success", False)]

            if not successful_devs:
                # All developers failed - report unexpected state
                # Early return: raise immediately if no supervisor
                if not self.supervisor or not hasattr(self.supervisor, 'handle_unexpected_state'):
                    raise Exception("All developers failed")

                recovery = self.supervisor.handle_unexpected_state(
                    current_state="STAGE_FAILED_ALL_DEVELOPERS",
                    expected_states=["STAGE_COMPLETED"],
                    context={
                        "stage_name": stage_name,
                        "error_message": "All developers failed",
                        "card_id": card_id,
                        "developer_count": len(developer_results),
                        "developer_errors": [r.get("error") for r in developer_results]
                    },
                    auto_learn=True  # Let supervisor learn how to fix this
                )

                # Early return: raise immediately if recovery failed
                if not recovery or not recovery.get("success"):
                    raise Exception("All developers failed and recovery unsuccessful")

                self.logger.log(
                    "Supervisor recovered from all-developers-failed state!",
                    "INFO"
                )
                # In production, would retry or apply learned solution here

            # Update progress: complete
            self.update_progress({"step": "complete", "progress_percent": 100})

            # Commit changes to git if git_agent is configured and we have successful developers
            git_commit_hash = None
            if self.git_agent and successful_devs:
                try:
                    # Determine scope from card
                    scope = card.get('component', 'core')
                    card_title = card.get('title', 'development work')

                    # Commit all changes
                    git_commit_hash = self.git_agent.commit_changes(
                        message=f"implement {card_title}",
                        commit_type="feat",
                        scope=scope
                    )
                    self.logger.log(f"Committed changes: {git_commit_hash}", "INFO")

                    # Optionally push if auto_push is enabled
                    if self.git_agent.repo_config.auto_push:
                        self.git_agent.push_changes(set_upstream=True)
                        self.logger.log(f"Pushed changes to remote", "INFO")

                except Exception as e:
                    self.logger.log(f"Failed to commit changes: {e}", "WARNING")
                    # Continue - git failure shouldn't fail the stage

            return {
                "stage": "development",
                "num_developers": num_developers,
                "developers": developer_results,
                "successful_developers": len(successful_devs),
                "status": "COMPLETE",
                "git_branch": feature_branch,
                "git_commit": git_commit_hash
            }

        except Exception as e:
            # Let supervisor learn from this failure
            self._handle_stage_failure(e, stage_name, card_id)
            # Re-raise after supervisor has learned
            raise

    def get_stage_name(self) -> str:
        return "development"

    def _track_developer_llm_costs(self, developer_results: list, stage_name: str):
        """Track LLM costs for each developer's work"""
        # Early return: no supervisor available
        if not self.supervisor:
            return

        for result in developer_results:
            # Early return: skip if not successful or no tokens
            if not result.get('success', False) or not result.get('tokens_used'):
                continue

            try:
                tokens_used = result['tokens_used']
                self.supervisor.track_llm_call(
                    model=result.get('llm_model', 'gpt-4o'),
                    provider=result.get('llm_provider', 'openai'),
                    tokens_input=getattr(tokens_used, 'prompt_tokens', 0),
                    tokens_output=getattr(tokens_used, 'completion_tokens', 0),
                    stage=stage_name,
                    purpose=result.get('developer', 'unknown')
                )
                self.logger.log(
                    f"Tracked LLM cost for {result.get('developer')}",
                    "INFO"
                )
            except Exception as e:
                # Budget exceeded or other cost tracking error
                self.logger.log(f"Cost tracking error: {e}", "ERROR")
                # Early return: re-raise budget errors immediately
                if "Budget" in str(e):
                    raise

    def _handle_stage_failure(self, exception: Exception, stage_name: str, card_id: str):
        """Handle stage failure with supervisor recovery if available"""
        # Early return: no supervisor available
        if not self.supervisor or not hasattr(self.supervisor, 'handle_unexpected_state'):
            return

        import traceback
        self.logger.log(f"Development stage failed, consulting supervisor...", "WARNING")

        recovery = self.supervisor.handle_unexpected_state(
            current_state="STAGE_FAILED",
            expected_states=["STAGE_COMPLETED"],
            context={
                "stage_name": stage_name,
                "error_message": str(exception),
                "stack_trace": traceback.format_exc(),
                "card_id": card_id
            },
            auto_learn=True
        )

        if recovery and recovery.get("success"):
            self.logger.log("Supervisor recovered from failure!", "INFO")
            # The supervisor's learned workflow already executed
            # In production, we might want to retry the stage here
        else:
            self.logger.log("Supervisor could not recover", "ERROR")

    def _read_adr(self, adr_file: str) -> str:
        """Read ADR content"""
        # Check if adr_file is empty or None
        if not adr_file or not adr_file.strip():
            raise FileReadError(
                "ADR file path is empty",
                {
                    "adr_file": adr_file,
                    "stage": "development"
                }
            )

        try:
            return FileManager.read_text(Path(adr_file))
        except Exception as e:
            raise wrap_exception(
                e,
                FileReadError,
                "Failed to read ADR file",
                {
                    "adr_file": adr_file,
                    "stage": "development"
                }
            )

    def _store_developer_solution_in_rag(self, card_id: str, card: Dict, dev_result: Dict):
        """Store developer solution in RAG for learning"""
        # Use .get() with defaults to handle missing keys defensively
        developer = dev_result.get('developer', 'unknown')
        approach = dev_result.get('approach', 'standard')  # Default approach if missing

        # Store in RAG using helper (DRY)


        RAGStorageHelper.store_stage_artifact(


            rag=self.rag,
            stage_name="developer_solution",
            card_id=card_id,
            task_title=card.get('title', 'Unknown'),
            content=f"{developer} solution using {approach} approach",
            metadata={
                "developer": developer,
                "approach": approach,
                "tdd_compliant": dev_result.get('tdd_workflow', {}).get('tests_written_first', False),
                "implementation_files": dev_result.get('implementation_files', []),
                "test_files": dev_result.get('test_files', [])
            }
        )

    def _execute_in_sandbox_if_enabled(self, developer_results: list):
        """Execute developer code in sandbox if supervisor has sandboxing enabled"""
        # Early return: skip if no sandbox configured
        if not self.supervisor or not hasattr(self.supervisor, 'sandbox') or not self.supervisor.sandbox:
            return

        # Executable extensions only (skip HTML, notebooks, markdown, etc.)
        executable_exts = {'.py', '.js', '.ts', '.java', '.go', '.rs', '.c', '.cpp'}

        for result in developer_results:
            # Early return: skip failed results
            if not result.get('success', False):
                continue

            dev_name = result.get('developer', 'unknown')
            impl_files = result.get('implementation_files', [])

            for impl_file in impl_files:
                file_path = Path(impl_file)

                # Early return: skip non-executable artifacts
                if not file_path.exists() or file_path.suffix not in executable_exts:
                    continue

                self.logger.log(f"Executing {dev_name} code in sandbox: {file_path.name}...", "INFO")
                code = file_path.read_text()

                # Execute in sandbox
                exec_result = self.supervisor.execute_code_safely(
                    code=code,
                    scan_security=True
                )

                if not exec_result["success"]:
                    error_msg = (
                        f"{dev_name} code execution failed: "
                        f"{exec_result.get('kill_reason', 'unknown')}"
                    )
                    self.logger.log(error_msg, "ERROR")

                    # Mark this developer solution as failed
                    result["success"] = False
                    result["error"] = error_msg

    def _add_files_to_knowledge_graph(self, kg, card_id: str, file_paths: list) -> int:
        """Helper to add a list of files to knowledge graph. Returns count of files added."""
        files_added = 0
        for file_path in file_paths:
            try:
                file_type = self._detect_file_type(str(file_path))
                kg.add_file(str(file_path), file_type)
                kg.link_task_to_file(card_id, str(file_path))
                files_added += 1
            except Exception as e:
                self.logger.log(f"   Could not add file {file_path}: {e}", "DEBUG")
        return files_added

    def _store_development_in_knowledge_graph(self, card_id: str, developer_results: list):
        """Store development artifacts in Knowledge Graph for traceability"""
        kg = get_knowledge_graph()
        # Early return: no knowledge graph available
        if not kg:
            self.logger.log("Knowledge Graph not available - skipping KG storage", "DEBUG")
            return

        try:
            self.logger.log("Storing development artifacts in Knowledge Graph...", "DEBUG")
            total_files = 0

            # Process each developer's implementation
            for dev_result in developer_results:
                # Early return: skip failed implementations
                if not dev_result.get('success', False):
                    continue

                # Add implementation files
                impl_files = dev_result.get('implementation_files', [])
                total_files += self._add_files_to_knowledge_graph(kg, card_id, impl_files)

                # Add test files
                test_files = dev_result.get('test_files', [])
                total_files += self._add_files_to_knowledge_graph(kg, card_id, test_files)

            if total_files > 0:
                self.logger.log(f"✅ Stored {total_files} implementation files in Knowledge Graph", "INFO")
            else:
                self.logger.log("✅ Development stage recorded in Knowledge Graph", "INFO")

        except Exception as e:
            self.logger.log(f"Warning: Could not store development artifacts in Knowledge Graph: {e}", "WARNING")
            self.logger.log(f"   Exception details: {type(e).__name__}", "DEBUG")

    def _detect_file_type(self, file_path: str) -> str:
        """Detect file type from path using early returns"""
        # Early returns: check each type and return immediately
        if file_path.endswith('.py'):
            return 'python'

        if file_path.endswith(('.js', '.jsx', '.ts', '.tsx')):
            return 'javascript'

        if file_path.endswith('.java'):
            return 'java'

        if file_path.endswith('.go'):
            return 'go'

        if file_path.endswith('.rs'):
            return 'rust'

        if file_path.endswith(('.c', '.cpp', '.h', '.hpp')):
            return 'c++'

        if file_path.endswith('.md'):
            return 'markdown'

        if file_path.endswith(('.yaml', '.yml')):
            return 'yaml'

        if file_path.endswith('.json'):
            return 'json'

        return 'unknown'


# ============================================================================
# VALIDATION STAGE
# ============================================================================

