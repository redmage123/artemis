#!/usr/bin/env python3
"""
WHY: Handle repository initialization, cloning, and configuration
RESPONSIBILITY: Manage repository lifecycle operations
PATTERNS: Single Responsibility Principle, guard clauses
"""

import subprocess
from pathlib import Path
from typing import Optional, List, Any

from artemis_logger import ArtemisLogger
from artemis_exceptions import GitOperationError, RepositoryNotFoundError

from .config import RepositoryConfig
from .models import GIT_REMOTE_ORIGIN, GIT_STATUS_SUCCESS, GIT_STATUS_FAILED


class RepositoryOperations:
    """
    WHY: Encapsulate all repository-level git operations
    RESPONSIBILITY: Initialize, clone, and manage repositories
    PATTERNS: Single Responsibility Principle, dependency injection
    """

    def __init__(
        self,
        repo_config: RepositoryConfig,
        logger: ArtemisLogger,
        operation_logger: Any
    ):
        """
        WHY: Inject dependencies for testability and flexibility
        RESPONSIBILITY: Store configuration and dependencies
        """
        self.repo_config = repo_config
        self.logger = logger
        self.operation_logger = operation_logger

    def ensure_repository(self) -> bool:
        """
        WHY: Guarantee repository exists before operations
        RESPONSIBILITY: Create or clone repository if needed
        PATTERNS: Guard clauses for validation
        """
        if not self.repo_config:
            raise ValueError("Repository configuration not set")

        repo_path = Path(self.repo_config.local_path)

        # Guard: Repository already exists
        if (repo_path / ".git").exists():
            self.logger.info(f"Repository exists: {repo_path}")
            return True

        # Guard: Cannot create missing repository
        if not self.repo_config.create_if_missing:
            raise RepositoryNotFoundError(f"Repository not found: {repo_path}")

        # Create or clone repository
        if self.repo_config.remote_url:
            return self._clone_repository()

        return self._init_repository()

    def _init_repository(self) -> bool:
        """
        WHY: Create new local git repository
        RESPONSIBILITY: Initialize git and set up default branch
        PATTERNS: Guard clauses, early returns
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

            self.operation_logger(
                'init_repository',
                GIT_STATUS_SUCCESS,
                {'path': str(repo_path), 'branch': default_branch}
            )

            self.logger.info(f"Initialized repository: {repo_path}")
            return True

        except Exception as e:
            self.operation_logger('init_repository', GIT_STATUS_FAILED, {'error': str(e)})
            raise GitOperationError(f"Failed to initialize repository: {e}")

    def _clone_repository(self) -> bool:
        """
        WHY: Clone repository from remote URL
        RESPONSIBILITY: Clone remote repository to local path
        PATTERNS: Guard clauses for validation
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

            self.operation_logger(
                'clone_repository',
                GIT_STATUS_SUCCESS,
                {
                    'url': self.repo_config.remote_url,
                    'path': str(repo_path)
                }
            )

            self.logger.info(f"Cloned repository: {self.repo_config.remote_url}")
            return True

        except Exception as e:
            self.operation_logger('clone_repository', GIT_STATUS_FAILED, {'error': str(e)})
            raise GitOperationError(f"Failed to clone repository: {e}")

    def get_current_branch(self) -> str:
        """
        WHY: Determine active branch for operations
        RESPONSIBILITY: Query git for current branch name
        """
        result = self._run_git_command(['rev-parse', '--abbrev-ref', 'HEAD'])
        return result.stdout.decode().strip()

    def get_status(self) -> dict:
        """
        WHY: Provide repository state information
        RESPONSIBILITY: Gather and return comprehensive status
        PATTERNS: Single Responsibility Principle
        """
        try:
            # Get current branch
            current_branch = self.get_current_branch()

            # Get uncommitted changes
            result = self._run_git_command(['status', '--porcelain'])
            uncommitted = len([l for l in result.stdout.decode().strip().split('\n') if l])

            # Get unpushed commits
            unpushed = 0
            if self.repo_config.remote_url:
                # Fetch quietly
                self._run_git_command(['fetch', 'origin'], check=False)

                result = self._run_git_command(
                    ['log', f'origin/{current_branch}..{current_branch}', '--oneline'],
                    check=False
                )
                unpushed = len([l for l in result.stdout.decode().strip().split('\n') if l])

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
