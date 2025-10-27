#!/usr/bin/env python3
"""
Git Agent - Autonomous Git Operations Manager

Acts as a build master for Artemis, handling all git workflows including:
- Repository initialization and cloning
- Branch strategies (GitFlow, GitHub Flow, trunk-based)
- Commit management with conventional commits
- Push/pull/fetch operations
- PR creation and merging
- Target repository configuration
- Output directory management

Author: Artemis Team
Date: October 26, 2025
"""

import os
import subprocess
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
from abc import ABC, abstractmethod

from artemis_logger import ArtemisLogger
from artemis_exceptions import GitOperationError, RepositoryNotFoundError
from pipeline_observer import EventType, PipelineEvent

# Constants
GIT_REMOTE_ORIGIN = 'origin'
GIT_STATUS_SUCCESS = 'success'
GIT_STATUS_FAILED = 'failed'
ARTEMIS_FOOTER = "\n\n🤖 Generated with Artemis Autonomous Pipeline"


class BranchStrategy(Enum):
    """Git branching strategies"""
    GITFLOW = "gitflow"  # main, develop, feature/*, release/*, hotfix/*
    GITHUB_FLOW = "github_flow"  # main, feature/*
    TRUNK_BASED = "trunk_based"  # main only with short-lived branches
    CUSTOM = "custom"


class CommitConvention(Enum):
    """Commit message conventions"""
    CONVENTIONAL = "conventional"  # feat:, fix:, docs:, etc.
    SEMANTIC = "semantic"  # Similar to conventional
    CUSTOM = "custom"


@dataclass
class RepositoryConfig:
    """Configuration for target repository"""
    name: str
    local_path: str
    remote_url: Optional[str] = None
    branch_strategy: str = "github_flow"
    default_branch: str = "main"
    commit_convention: str = "conventional"
    auto_push: bool = False
    create_if_missing: bool = True

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class GitOperation:
    """Record of a git operation"""
    operation_type: str
    timestamp: str
    status: str
    details: Dict
    error: Optional[str] = None


# ============================================================================
# STRATEGY PATTERN - Branch Strategies
# ============================================================================

class BranchStrategyHandler(ABC):
    """Abstract strategy for branch management"""

    @abstractmethod
    def get_base_branch(self, default_branch: str) -> str:
        """Get the base branch for creating feature branches"""
        pass

    @abstractmethod
    def get_branch_prefix(self) -> str:
        """Get the prefix for feature branches"""
        pass


class GitFlowStrategyHandler(BranchStrategyHandler):
    """GitFlow strategy: main/develop with feature/release/hotfix branches"""

    def get_base_branch(self, default_branch: str) -> str:
        return "develop"

    def get_branch_prefix(self) -> str:
        return "feature/"


class GitHubFlowStrategyHandler(BranchStrategyHandler):
    """GitHub Flow strategy: main with feature branches"""

    def get_base_branch(self, default_branch: str) -> str:
        return default_branch

    def get_branch_prefix(self) -> str:
        return "feature/"


class TrunkBasedStrategyHandler(BranchStrategyHandler):
    """Trunk-based development: main with short-lived branches"""

    def get_base_branch(self, default_branch: str) -> str:
        return default_branch

    def get_branch_prefix(self) -> str:
        return ""


class BranchStrategyFactory:
    """Factory for creating branch strategy handlers"""

    _strategies = {
        BranchStrategy.GITFLOW: GitFlowStrategyHandler,
        BranchStrategy.GITHUB_FLOW: GitHubFlowStrategyHandler,
        BranchStrategy.TRUNK_BASED: TrunkBasedStrategyHandler,
    }

    @classmethod
    def create(cls, strategy: BranchStrategy) -> BranchStrategyHandler:
        """Create strategy handler for given strategy type"""
        handler_class = cls._strategies.get(strategy, GitHubFlowStrategyHandler)
        return handler_class()


# ============================================================================
# STRATEGY PATTERN - Commit Message Formatters
# ============================================================================

class CommitMessageFormatter(ABC):
    """Abstract formatter for commit messages"""

    @abstractmethod
    def format(self, message: str, commit_type: Optional[str], scope: Optional[str]) -> str:
        """Format commit message according to convention"""
        pass


class ConventionalCommitFormatter(CommitMessageFormatter):
    """Conventional commits formatter (feat:, fix:, etc.)"""

    def format(self, message: str, commit_type: Optional[str], scope: Optional[str]) -> str:
        if not commit_type:
            return message

        if scope:
            return f"{commit_type}({scope}): {message}"
        return f"{commit_type}: {message}"


class PlainCommitFormatter(CommitMessageFormatter):
    """Plain commit formatter - no special formatting"""

    def format(self, message: str, commit_type: Optional[str], scope: Optional[str]) -> str:
        return message


class CommitFormatterFactory:
    """Factory for creating commit message formatters"""

    _formatters = {
        CommitConvention.CONVENTIONAL: ConventionalCommitFormatter,
        CommitConvention.SEMANTIC: ConventionalCommitFormatter,
        CommitConvention.CUSTOM: PlainCommitFormatter,
    }

    @classmethod
    def create(cls, convention: CommitConvention) -> CommitMessageFormatter:
        """Create formatter for given convention"""
        formatter_class = cls._formatters.get(convention, PlainCommitFormatter)
        return formatter_class()


# ============================================================================
# MAIN GIT AGENT
# ============================================================================

class GitAgent:
    """
    Autonomous Git Agent - Build Master for Artemis

    Manages all git operations for projects being created or refactored by Artemis.
    Acts as the team's build master, handling workflows, branching, and repository management.
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
        Initialize Git Agent

        Args:
            repo_config: Configuration for target repository
            verbose: Enable verbose logging
            logger: Optional Artemis logger instance
            observable: Pipeline observable for event broadcasting
            supervisor: Supervisor agent for health monitoring
        """
        self.logger = logger or ArtemisLogger(component_name="GitAgent")
        self.verbose = verbose
        self.repo_config = repo_config
        self.operations_history: List[GitOperation] = []
        self.observable = observable
        self.supervisor = supervisor

        # Initialize repository if config provided
        if repo_config:
            self._ensure_repository()

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def _get_current_branch(self) -> str:
        """Get the current git branch name"""
        result = self._run_git_command(['rev-parse', '--abbrev-ref', 'HEAD'])
        return result.stdout.decode().strip()

    def _sanitize_branch_name(self, name: str) -> str:
        """Sanitize branch name (lowercase, replace spaces/underscores with dashes)"""
        return name.lower().replace(' ', '-').replace('_', '-')

    def _build_branch_name(
        self,
        strategy_handler: BranchStrategyHandler,
        feature_name: str,
        card_id: Optional[str] = None
    ) -> str:
        """Build branch name using strategy pattern"""
        prefix = strategy_handler.get_branch_prefix()
        name = f"{card_id}-{feature_name}" if card_id else feature_name
        return self._sanitize_branch_name(f"{prefix}{name}")

    def _notify_event(
        self,
        event_type: EventType,
        data: Dict[str, Any],
        card_id: Optional[str] = None
    ) -> None:
        """
        Notify observers of git event

        Args:
            event_type: Type of event
            data: Event data
            card_id: Optional card ID
        """
        if self.observable:
            event = PipelineEvent(
                event_type=event_type,
                card_id=card_id,
                stage_name="git_agent",
                data=data
            )
            self.observable.notify(event)

    def configure_repository(
        self,
        name: str,
        local_path: str,
        remote_url: Optional[str] = None,
        branch_strategy: str = "github_flow",
        **kwargs
    ) -> RepositoryConfig:
        """
        Configure target repository for Artemis operations

        Args:
            name: Repository name
            local_path: Local path where repo exists or will be created
            remote_url: Optional remote URL (GitHub, GitLab, etc.)
            branch_strategy: Branching strategy to use
            **kwargs: Additional repository configuration

        Returns:
            RepositoryConfig object
        """
        config = RepositoryConfig(
            name=name,
            local_path=local_path,
            remote_url=remote_url,
            branch_strategy=branch_strategy,
            **kwargs
        )

        self.repo_config = config
        self._ensure_repository()

        self.logger.info(f"Configured repository: {name} at {local_path}")

        # Notify observers
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

    def _ensure_repository(self) -> bool:
        """
        Ensure repository exists, create or clone if necessary

        Returns:
            True if repository ready, False otherwise
        """
        if not self.repo_config:
            raise ValueError("Repository configuration not set")

        repo_path = Path(self.repo_config.local_path)

        # Repository already exists
        if (repo_path / ".git").exists():
            self.logger.info(f"Repository exists: {repo_path}")
            return True

        # Create new repository
        if self.repo_config.create_if_missing:
            if self.repo_config.remote_url:
                return self._clone_repository()
            else:
                return self._init_repository()

        raise RepositoryNotFoundError(f"Repository not found: {repo_path}")

    def _init_repository(self) -> bool:
        """
        Initialize new git repository

        Returns:
            True if successful
        """
        repo_path = Path(self.repo_config.local_path)
        repo_path.mkdir(parents=True, exist_ok=True)

        try:
            # Initialize git
            self._run_git_command(['init'], cwd=repo_path)

            # Set default branch
            default_branch = self.repo_config.default_branch
            self._run_git_command(
                ['checkout', '-b', default_branch],
                cwd=repo_path
            )

            # Add remote if provided
            if self.repo_config.remote_url:
                self._run_git_command(
                    ['remote', 'add', GIT_REMOTE_ORIGIN, self.repo_config.remote_url],
                    cwd=repo_path
                )

            self._log_operation(
                'init_repository',
                GIT_STATUS_SUCCESS,
                {'path': str(repo_path), 'branch': default_branch}
            )

            self.logger.info(f"Initialized repository: {repo_path}")
            return True

        except Exception as e:
            self._log_operation('init_repository', GIT_STATUS_FAILED, {'error': str(e)})
            raise GitOperationError(f"Failed to initialize repository: {e}")

    def _clone_repository(self) -> bool:
        """
        Clone repository from remote URL

        Returns:
            True if successful
        """
        if not self.repo_config.remote_url:
            raise ValueError("Remote URL required for cloning")

        repo_path = Path(self.repo_config.local_path)
        parent_dir = repo_path.parent
        parent_dir.mkdir(parents=True, exist_ok=True)

        try:
            self._run_git_command(
                ['clone', self.repo_config.remote_url, str(repo_path)],
                cwd=parent_dir
            )

            self._log_operation(
                'clone_repository',
                'success',
                {
                    'url': self.repo_config.remote_url,
                    'path': str(repo_path)
                }
            )

            self.logger.info(f"Cloned repository: {self.repo_config.remote_url}")
            return True

        except Exception as e:
            self._log_operation('clone_repository', 'failed', {'error': str(e)})
            raise GitOperationError(f"Failed to clone repository: {e}")

    def create_feature_branch(
        self,
        feature_name: str,
        card_id: Optional[str] = None
    ) -> str:
        """
        Create feature branch following configured strategy

        Args:
            feature_name: Name of the feature
            card_id: Optional Kanban card ID

        Returns:
            Branch name created
        """
        # Use Strategy Pattern to determine branch details
        strategy = BranchStrategy(self.repo_config.branch_strategy)
        strategy_handler = BranchStrategyFactory.create(strategy)

        base_branch = strategy_handler.get_base_branch(self.repo_config.default_branch)
        branch_name = self._build_branch_name(strategy_handler, feature_name, card_id)

        try:
            # Ensure on base branch and up to date
            self._run_git_command(['checkout', base_branch])

            if self.repo_config.remote_url:
                self._run_git_command(['pull', GIT_REMOTE_ORIGIN, base_branch])

            # Create and checkout feature branch
            self._run_git_command(['checkout', '-b', branch_name])

            self._log_operation(
                'create_feature_branch',
                GIT_STATUS_SUCCESS,
                {
                    'branch': branch_name,
                    'base': base_branch,
                    'feature': feature_name,
                    'card_id': card_id
                }
            )

            self.logger.info(f"Created feature branch: {branch_name}")

            # Notify observers
            self._notify_event(
                EventType.GIT_BRANCH_CREATED,
                {
                    "branch_name": branch_name,
                    "base_branch": base_branch,
                    "feature_name": feature_name,
                    "strategy": strategy.value
                },
                card_id=card_id
            )

            return branch_name

        except Exception as e:
            self._log_operation('create_feature_branch', GIT_STATUS_FAILED, {'error': str(e)})

            # Notify observers of failure
            self._notify_event(
                EventType.GIT_OPERATION_FAILED,
                {
                    "operation": "create_feature_branch",
                    "error": str(e),
                    "feature_name": feature_name
                },
                card_id=card_id
            )

            raise GitOperationError(f"Failed to create feature branch: {e}")

    def commit_changes(
        self,
        message: str,
        files: Optional[List[str]] = None,
        commit_type: Optional[str] = None,
        scope: Optional[str] = None
    ) -> str:
        """
        Commit changes with conventional commit format

        Args:
            message: Commit message
            files: Optional list of specific files to commit (None = all)
            commit_type: Type of commit (feat, fix, docs, etc.)
            scope: Optional scope of change

        Returns:
            Commit hash
        """
        # Use Formatter Pattern to format commit message
        convention = CommitConvention(self.repo_config.commit_convention)
        formatter = CommitFormatterFactory.create(convention)
        formatted_message = formatter.format(message, commit_type, scope) + ARTEMIS_FOOTER

        try:
            # Stage files - optimize: use single git add command
            if files:
                self._run_git_command(['add'] + files)
            else:
                self._run_git_command(['add', '.'])

            # Create commit
            self._run_git_command(['commit', '-m', formatted_message])

            # Get commit hash
            result = self._run_git_command(['rev-parse', 'HEAD'])
            commit_hash = result.stdout.decode().strip()[:8]

            self._log_operation(
                'commit',
                GIT_STATUS_SUCCESS,
                {
                    'hash': commit_hash,
                    'message': message,
                    'type': commit_type,
                    'files_count': len(files) if files else 'all'
                }
            )

            self.logger.info(f"Created commit: {commit_hash} - {message[:50]}")

            # Notify observers
            self._notify_event(
                EventType.GIT_COMMIT_CREATED,
                {
                    "commit_hash": commit_hash,
                    "message": message,
                    "commit_type": commit_type,
                    "scope": scope,
                    "files_count": len(files) if files else "all"
                }
            )

            # Auto-push if configured
            if self.repo_config.auto_push:
                self.push_changes()

            return commit_hash

        except Exception as e:
            self._log_operation('commit', GIT_STATUS_FAILED, {'error': str(e)})

            # Notify observers of failure
            self._notify_event(
                EventType.GIT_OPERATION_FAILED,
                {
                    "operation": "commit",
                    "error": str(e),
                    "message": message
                }
            )

            raise GitOperationError(f"Failed to commit changes: {e}")

    def push_changes(
        self,
        branch: Optional[str] = None,
        force: bool = False,
        set_upstream: bool = True
    ) -> bool:
        """
        Push changes to remote repository

        Args:
            branch: Branch to push (None = current branch)
            force: Force push
            set_upstream: Set upstream tracking

        Returns:
            True if successful
        """
        if not self.repo_config.remote_url:
            self.logger.warning("No remote URL configured, skipping push")
            return False

        try:
            # Get current branch if not specified
            if not branch:
                result = self._run_git_command(['rev-parse', '--abbrev-ref', 'HEAD'])
                branch = result.stdout.decode().strip()

            # Build push command
            args = ['push']
            if set_upstream:
                args.extend(['-u', 'origin', branch])
            else:
                args.extend(['origin', branch])

            if force:
                args.append('--force')

            # Notify observers - push started
            from pipeline_observer import EventType
            self._notify_event(
                EventType.GIT_PUSH_STARTED,
                {
                    "branch": branch,
                    "remote": "origin",
                    "force": force
                }
            )

            self._run_git_command(args)

            self._log_operation(
                'push',
                'success',
                {'branch': branch, 'force': force}
            )

            self.logger.info(f"Pushed changes to: {branch}")

            # Notify observers - push completed
            self._notify_event(
                EventType.GIT_PUSH_COMPLETED,
                {
                    "branch": branch,
                    "remote": "origin",
                    "force": force
                }
            )

            return True

        except Exception as e:
            self._log_operation('push', 'failed', {'error': str(e)})

            # Notify observers of failure
            from pipeline_observer import EventType
            self._notify_event(
                EventType.GIT_PUSH_FAILED,
                {
                    "branch": branch,
                    "error": str(e)
                }
            )

            raise GitOperationError(f"Failed to push changes: {e}")

    def pull_changes(
        self,
        branch: Optional[str] = None,
        rebase: bool = True
    ) -> bool:
        """
        Pull changes from remote repository

        Args:
            branch: Branch to pull (None = current branch)
            rebase: Use rebase instead of merge

        Returns:
            True if successful
        """
        if not self.repo_config.remote_url:
            self.logger.warning("No remote URL configured, skipping pull")
            return False

        try:
            # Get current branch if not specified
            if not branch:
                result = self._run_git_command(['rev-parse', '--abbrev-ref', 'HEAD'])
                branch = result.stdout.decode().strip()

            # Build pull command
            args = ['pull', 'origin', branch]
            if rebase:
                args.append('--rebase')

            self._run_git_command(args)

            self._log_operation(
                'pull',
                'success',
                {'branch': branch, 'rebase': rebase}
            )

            self.logger.info(f"Pulled changes from: {branch}")
            return True

        except Exception as e:
            self._log_operation('pull', 'failed', {'error': str(e)})
            raise GitOperationError(f"Failed to pull changes: {e}")

    def fetch_updates(self, prune: bool = True) -> bool:
        """
        Fetch updates from remote

        Args:
            prune: Remove deleted remote branches

        Returns:
            True if successful
        """
        if not self.repo_config.remote_url:
            return False

        try:
            args = ['fetch', 'origin']
            if prune:
                args.append('--prune')

            self._run_git_command(args)

            self._log_operation('fetch', 'success', {'prune': prune})
            self.logger.info("Fetched updates from remote")
            return True

        except Exception as e:
            self._log_operation('fetch', 'failed', {'error': str(e)})
            return False

    def get_status(self) -> Dict:
        """
        Get repository status

        Returns:
            Dictionary with status information
        """
        try:
            # Get current branch
            result = self._run_git_command(['rev-parse', '--abbrev-ref', 'HEAD'])
            current_branch = result.stdout.decode().strip()

            # Get uncommitted changes
            result = self._run_git_command(['status', '--porcelain'])
            uncommitted = len([l for l in result.stdout.decode().strip().split('\n') if l])

            # Get unpushed commits
            if self.repo_config.remote_url:
                self.fetch_updates(prune=False)
                result = self._run_git_command(
                    ['log', f'origin/{current_branch}..{current_branch}', '--oneline'],
                    check=False
                )
                unpushed = len([l for l in result.stdout.decode().strip().split('\n') if l])
            else:
                unpushed = 0

            return {
                'repository': self.repo_config.name,
                'path': self.repo_config.local_path,
                'branch': current_branch,
                'uncommitted_changes': uncommitted,
                'unpushed_commits': unpushed,
                'has_remote': bool(self.repo_config.remote_url)
            }

        except Exception as e:
            self.logger.error(f"Failed to get status: {e}")
            return {}

    def create_tag(
        self,
        tag_name: str,
        message: Optional[str] = None,
        push: bool = True
    ) -> bool:
        """
        Create git tag

        Args:
            tag_name: Name of tag (e.g., v1.0.0)
            message: Optional tag message
            push: Push tag to remote

        Returns:
            True if successful
        """
        try:
            args = ['tag']
            if message:
                args.extend(['-a', tag_name, '-m', message])
            else:
                args.append(tag_name)

            self._run_git_command(args)

            if push and self.repo_config.remote_url:
                self._run_git_command(['push', 'origin', tag_name])

            self._log_operation(
                'create_tag',
                'success',
                {'tag': tag_name, 'pushed': push}
            )

            self.logger.info(f"Created tag: {tag_name}")
            return True

        except Exception as e:
            self._log_operation('create_tag', 'failed', {'error': str(e)})
            return False

    def cleanup_merged_branches(
        self,
        delete_remote: bool = False,
        exclude_branches: Optional[List[str]] = None
    ) -> List[str]:
        """
        Clean up branches that have been merged

        Args:
            delete_remote: Also delete remote branches
            exclude_branches: Branches to exclude from cleanup

        Returns:
            List of deleted branches
        """
        base_branch = self.repo_config.default_branch
        protected = exclude_branches or []
        protected.extend([base_branch, 'develop', 'main', 'master'])

        try:
            # Get merged branches
            result = self._run_git_command(['branch', '--merged', base_branch])
            branches = result.stdout.decode().strip().split('\n')

            deleted = []
            for branch in branches:
                branch = branch.strip().replace('* ', '')
                if branch and branch not in protected:
                    try:
                        self._run_git_command(['branch', '-d', branch])
                        deleted.append(branch)

                        if delete_remote and self.repo_config.remote_url:
                            self._run_git_command(
                                ['push', 'origin', '--delete', branch],
                                check=False
                            )
                    except:
                        pass

            self._log_operation(
                'cleanup_branches',
                'success',
                {'deleted': deleted, 'count': len(deleted)}
            )

            self.logger.info(f"Cleaned up {len(deleted)} merged branches")
            return deleted

        except Exception as e:
            self._log_operation('cleanup_branches', 'failed', {'error': str(e)})
            return []

    def save_output_to_repo(
        self,
        source_dir: str,
        commit_message: str,
        branch: Optional[str] = None
    ) -> bool:
        """
        Save Artemis output to target repository

        Args:
            source_dir: Directory containing Artemis output
            commit_message: Commit message
            branch: Optional branch to commit to

        Returns:
            True if successful
        """
        try:
            # Switch to target branch if specified
            if branch:
                self._run_git_command(['checkout', branch])

            # Copy files from source to repo
            source_path = Path(source_dir)
            repo_path = Path(self.repo_config.local_path)

            if source_path.exists():
                # Copy files (excluding .git)
                for item in source_path.iterdir():
                    if item.name != '.git':
                        dest = repo_path / item.name
                        if item.is_file():
                            shutil.copy2(item, dest)
                        else:
                            shutil.copytree(item, dest, dirs_exist_ok=True)

            # Commit changes
            self.commit_changes(commit_message)

            self.logger.info(f"Saved output to repository: {commit_message}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to save output to repo: {e}")
            return False

    def _run_git_command(
        self,
        args: List[str],
        cwd: Optional[Path] = None,
        check: bool = True
    ) -> subprocess.CompletedProcess:
        """
        Run git command

        Args:
            args: Git command arguments
            cwd: Working directory (default: repo_config.local_path)
            check: Raise exception on error

        Returns:
            CompletedProcess result
        """
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

    def _log_operation(
        self,
        operation_type: str,
        status: str,
        details: Dict,
        error: Optional[str] = None
    ):
        """Log git operation"""
        operation = GitOperation(
            operation_type=operation_type,
            timestamp=datetime.utcnow().isoformat() + 'Z',
            status=status,
            details=details,
            error=error
        )
        self.operations_history.append(operation)

    def get_operations_summary(self) -> Dict:
        """
        Get summary of git operations

        Returns:
            Summary dictionary
        """
        total = len(self.operations_history)
        successful = len([op for op in self.operations_history if op.status == 'success'])
        failed = len([op for op in self.operations_history if op.status == 'failed'])

        return {
            'total_operations': total,
            'successful': successful,
            'failed': failed,
            'success_rate': f"{(successful/total*100):.1f}%" if total > 0 else "0%",
            'operations': [asdict(op) for op in self.operations_history]
        }

    def save_operations_log(self, output_path: Optional[str] = None) -> str:
        """
        Save operations log to file

        Args:
            output_path: Optional output path

        Returns:
            Path to saved log file
        """
        if not output_path:
            git_ops_dir = os.getenv("ARTEMIS_GIT_OPS_DIR", "../.artemis_data/git_operations")
            git_ops_dir = Path(git_ops_dir)
            git_ops_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = git_ops_dir / f"git_agent_log_{timestamp}.json"

        summary = self.get_operations_summary()
        summary['repository'] = self.repo_config.to_dict() if self.repo_config else None

        with open(output_path, 'w') as f:
            json.dump(summary, f, indent=2)

        self.logger.info(f"Operations log saved: {output_path}")
        return str(output_path)


# Example usage and testing
if __name__ == '__main__':
    # Example: Configure agent for a new project
    agent = GitAgent(verbose=True)

    # Configure target repository
    config = agent.configure_repository(
        name="my-awesome-project",
        local_path="/tmp/my-awesome-project",
        remote_url="git@github.com:username/my-awesome-project.git",
        branch_strategy="github_flow",
        auto_push=False
    )

    print(f"\n✅ Git Agent configured for: {config.name}")
    print(f"📁 Local path: {config.local_path}")
    print(f"🌿 Branch strategy: {config.branch_strategy}")

    # Show status
    status = agent.get_status()
    print(f"\n📊 Repository Status:")
    print(json.dumps(status, indent=2))
