#!/usr/bin/env python3
"""
WHY: Orchestrate all git operations through a unified interface
RESPONSIBILITY: Coordinate repository, branch, commit, and remote operations
PATTERNS: Facade Pattern, dependency injection
"""

import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any

from artemis_logger import ArtemisLogger

from .config import RepositoryConfig
from .repo_operations import RepositoryOperations
from .branch_operations import BranchOperations
from .commit_operations import CommitOperations
from .remote_operations import RemoteOperations
from .operations_logger import OperationsLogger


class GitAgent:
    """
    WHY: Provide unified interface for all git operations
    RESPONSIBILITY: Orchestrate operations classes and manage state
    PATTERNS: Facade Pattern, Composition, dependency injection
    """

    def __init__(
        self,
        repo_config: Optional[RepositoryConfig] = None,
        verbose: bool = True,
        logger: Optional[ArtemisLogger] = None,
        observable: Optional['PipelineObservable'] = None,
        supervisor: Optional['SupervisorAgent'] = None
    ):
        """
        WHY: Initialize agent with configuration and dependencies
        RESPONSIBILITY: Set up operations classes and logger
        PATTERNS: Dependency injection, composition
        """
        self.logger = logger or ArtemisLogger(component_name="GitAgent")
        self.verbose = verbose
        self.repo_config = repo_config
        self.observable = observable
        self.supervisor = supervisor

        # Initialize operations logger
        self.ops_logger = OperationsLogger(self.logger, repo_config)

        # Initialize operations classes (lazy initialization)
        self._repo_ops: Optional[RepositoryOperations] = None
        self._branch_ops: Optional[BranchOperations] = None
        self._commit_ops: Optional[CommitOperations] = None
        self._remote_ops: Optional[RemoteOperations] = None

        # Initialize repository if config provided
        if repo_config:
            self._ensure_repository()

    # ========================================================================
    # REPOSITORY CONFIGURATION
    # ========================================================================

    def configure_repository(
        self,
        name: str,
        local_path: str,
        remote_url: Optional[str] = None,
        branch_strategy: str = "github_flow",
        **kwargs
    ) -> RepositoryConfig:
        """
        WHY: Configure target repository for Artemis operations
        RESPONSIBILITY: Create config and initialize repository
        PATTERNS: Builder pattern concepts
        """
        config = RepositoryConfig(
            name=name,
            local_path=local_path,
            remote_url=remote_url,
            branch_strategy=branch_strategy,
            **kwargs
        )

        self.repo_config = config
        self.ops_logger.repo_config = config
        self._ensure_repository()

        self.logger.info(f"Configured repository: {name} at {local_path}")

        # Notify observers
        from pipeline_observer import EventType
        self._notify_event(
            EventType.GIT_REPOSITORY_CONFIGURED,
            {
                "repository_name": name,
                "local_path": local_path,
                "remote_url": remote_url,
                "branch_strategy": branch_strategy
            }
        )

        return config

    # ========================================================================
    # REPOSITORY OPERATIONS
    # ========================================================================

    def get_status(self) -> Dict:
        """
        WHY: Query repository state
        RESPONSIBILITY: Delegate to repository operations
        """
        return self._get_repo_ops().get_status()

    # ========================================================================
    # BRANCH OPERATIONS
    # ========================================================================

    def create_feature_branch(
        self,
        feature_name: str,
        card_id: Optional[str] = None
    ) -> str:
        """
        WHY: Create feature branch following strategy
        RESPONSIBILITY: Delegate to branch operations
        """
        return self._get_branch_ops().create_feature_branch(feature_name, card_id)

    def cleanup_merged_branches(
        self,
        delete_remote: bool = False,
        exclude_branches: Optional[List[str]] = None
    ) -> List[str]:
        """
        WHY: Clean up merged branches
        RESPONSIBILITY: Delegate to branch operations
        """
        return self._get_branch_ops().cleanup_merged_branches(delete_remote, exclude_branches)

    def create_tag(
        self,
        tag_name: str,
        message: Optional[str] = None,
        push: bool = True
    ) -> bool:
        """
        WHY: Create git tag
        RESPONSIBILITY: Delegate to branch operations
        """
        return self._get_branch_ops().create_tag(tag_name, message, push)

    # ========================================================================
    # COMMIT OPERATIONS
    # ========================================================================

    def commit_changes(
        self,
        message: str,
        files: Optional[List[str]] = None,
        commit_type: Optional[str] = None,
        scope: Optional[str] = None
    ) -> str:
        """
        WHY: Create commit with formatted message
        RESPONSIBILITY: Delegate to commit operations and handle auto-push
        """
        commit_hash = self._get_commit_ops().commit_changes(
            message, files, commit_type, scope
        )

        # Auto-push if configured
        if self.repo_config.auto_push:
            self.push_changes()

        return commit_hash

    # ========================================================================
    # REMOTE OPERATIONS
    # ========================================================================

    def push_changes(
        self,
        branch: Optional[str] = None,
        force: bool = False,
        set_upstream: bool = True
    ) -> bool:
        """
        WHY: Push commits to remote
        RESPONSIBILITY: Delegate to remote operations
        """
        return self._get_remote_ops().push_changes(branch, force, set_upstream)

    def pull_changes(
        self,
        branch: Optional[str] = None,
        rebase: bool = True
    ) -> bool:
        """
        WHY: Pull changes from remote
        RESPONSIBILITY: Delegate to remote operations
        """
        return self._get_remote_ops().pull_changes(branch, rebase)

    def fetch_updates(self, prune: bool = True) -> bool:
        """
        WHY: Fetch remote updates
        RESPONSIBILITY: Delegate to remote operations
        """
        return self._get_remote_ops().fetch_updates(prune)

    def save_output_to_repo(
        self,
        source_dir: str,
        commit_message: str,
        branch: Optional[str] = None
    ) -> bool:
        """
        WHY: Copy Artemis output to repository
        RESPONSIBILITY: Delegate to remote operations with commit callback
        """
        return self._get_remote_ops().save_output_to_repo(
            source_dir,
            commit_message,
            branch,
            commit_callback=self.commit_changes
        )

    # ========================================================================
    # OPERATIONS LOGGING
    # ========================================================================

    def get_operations_summary(self) -> Dict:
        """
        WHY: Retrieve operations summary
        RESPONSIBILITY: Delegate to operations logger
        """
        return self.ops_logger.get_operations_summary()

    def save_operations_log(self, output_path: Optional[str] = None) -> str:
        """
        WHY: Persist operations log
        RESPONSIBILITY: Delegate to operations logger
        """
        return self.ops_logger.save_operations_log(output_path)

    # ========================================================================
    # PRIVATE HELPERS
    # ========================================================================

    def _ensure_repository(self) -> bool:
        """
        WHY: Guarantee repository exists before operations
        RESPONSIBILITY: Delegate to repository operations
        """
        return self._get_repo_ops().ensure_repository()

    def _get_repo_ops(self) -> RepositoryOperations:
        """
        WHY: Lazy initialization of repository operations
        RESPONSIBILITY: Create and cache repository operations instance
        PATTERNS: Lazy initialization pattern
        """
        if not self._repo_ops:
            self._repo_ops = RepositoryOperations(
                self.repo_config,
                self.logger,
                self.ops_logger.log_operation
            )
        return self._repo_ops

    def _get_branch_ops(self) -> BranchOperations:
        """
        WHY: Lazy initialization of branch operations
        RESPONSIBILITY: Create and cache branch operations instance
        PATTERNS: Lazy initialization pattern
        """
        if not self._branch_ops:
            self._branch_ops = BranchOperations(
                self.repo_config,
                self.logger,
                self.ops_logger.log_operation,
                self._run_git_command,
                self._notify_event
            )
        return self._branch_ops

    def _get_commit_ops(self) -> CommitOperations:
        """
        WHY: Lazy initialization of commit operations
        RESPONSIBILITY: Create and cache commit operations instance
        PATTERNS: Lazy initialization pattern
        """
        if not self._commit_ops:
            self._commit_ops = CommitOperations(
                self.repo_config,
                self.logger,
                self.ops_logger.log_operation,
                self._run_git_command,
                self._notify_event
            )
        return self._commit_ops

    def _get_remote_ops(self) -> RemoteOperations:
        """
        WHY: Lazy initialization of remote operations
        RESPONSIBILITY: Create and cache remote operations instance
        PATTERNS: Lazy initialization pattern
        """
        if not self._remote_ops:
            self._remote_ops = RemoteOperations(
                self.repo_config,
                self.logger,
                self.ops_logger.log_operation,
                self._run_git_command,
                self._notify_event
            )
        return self._remote_ops

    def _run_git_command(
        self,
        args: List[str],
        cwd: Optional[Path] = None,
        check: bool = True
    ) -> subprocess.CompletedProcess:
        """
        WHY: Execute git commands with consistent error handling
        RESPONSIBILITY: Run git subprocess and handle errors
        PATTERNS: Guard clauses, consistent error handling
        """
        from artemis_exceptions import GitOperationError

        if not cwd:
            cwd = Path(self.repo_config.local_path) if self.repo_config else Path.cwd()

        result = subprocess.run(
            ['git'] + args,
            capture_output=True,
            cwd=cwd,
            check=False
        )

        if check and result.returncode != 0:
            error_msg = result.stderr.decode().strip()
            raise GitOperationError(f"Git command failed: {' '.join(args)}\n{error_msg}")

        return result

    def _notify_event(
        self,
        event_type: Any,
        data: Dict[str, Any],
        card_id: Optional[str] = None
    ) -> None:
        """
        WHY: Notify observers of git events
        RESPONSIBILITY: Broadcast events through observable
        PATTERNS: Observer pattern
        """
        if not self.observable:
            return

        from pipeline_observer import PipelineEvent

        event = PipelineEvent(
            event_type=event_type,
            card_id=card_id,
            stage_name="git_agent",
            data=data
        )
        self.observable.notify(event)

    # ========================================================================
    # BACKWARD COMPATIBILITY PROPERTIES
    # ========================================================================

    @property
    def operations_history(self) -> List:
        """
        WHY: Maintain backward compatibility with old API
        RESPONSIBILITY: Expose operations history
        """
        return self.ops_logger.operations_history
