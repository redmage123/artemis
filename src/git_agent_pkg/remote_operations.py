#!/usr/bin/env python3
"""
WHY: Handle all remote repository operations
RESPONSIBILITY: Push, pull, fetch, and sync with remote repositories
PATTERNS: Single Responsibility Principle, guard clauses
"""

import shutil
from pathlib import Path
from typing import Optional, Any, Callable

from artemis_logger import ArtemisLogger
from artemis_exceptions import GitOperationError
from pipeline_observer import EventType

from .config import RepositoryConfig
from .models import GIT_REMOTE_ORIGIN, GIT_STATUS_SUCCESS, GIT_STATUS_FAILED


class RemoteOperations:
    """
    WHY: Encapsulate all remote repository operations
    RESPONSIBILITY: Manage push, pull, fetch, and remote sync
    PATTERNS: Single Responsibility Principle, dependency injection
    """

    def __init__(
        self,
        repo_config: RepositoryConfig,
        logger: ArtemisLogger,
        operation_logger: Any,
        git_command_runner: Callable,
        event_notifier: Optional[Callable] = None
    ):
        """
        WHY: Inject dependencies for testability and flexibility
        RESPONSIBILITY: Store configuration and dependencies
        """
        self.repo_config = repo_config
        self.logger = logger
        self.operation_logger = operation_logger
        self.run_git_command = git_command_runner
        self.notify_event = event_notifier

    def push_changes(
        self,
        branch: Optional[str] = None,
        force: bool = False,
        set_upstream: bool = True
    ) -> bool:
        """
        WHY: Publish local commits to remote repository
        RESPONSIBILITY: Push commits with proper flags and tracking
        PATTERNS: Guard clauses for validation
        """
        # Guard: No remote URL configured
        if not self.repo_config.remote_url:
            self.logger.warning("No remote URL configured, skipping push")
            return False

        try:
            # Get current branch if not specified
            if not branch:
                result = self.run_git_command(['rev-parse', '--abbrev-ref', 'HEAD'])
                branch = result.stdout.decode().strip()

            # Build push command using dispatch table pattern
            args = self._build_push_args(branch, force, set_upstream)

            # Notify observers - push started
            if self.notify_event:
                self.notify_event(
                    EventType.GIT_PUSH_STARTED,
                    {
                        "branch": branch,
                        "remote": "origin",
                        "force": force
                    }
                )

            self.run_git_command(args)

            self.operation_logger(
                'push',
                GIT_STATUS_SUCCESS,
                {'branch': branch, 'force': force}
            )

            self.logger.info(f"Pushed changes to: {branch}")

            # Notify observers - push completed
            if self.notify_event:
                self.notify_event(
                    EventType.GIT_PUSH_COMPLETED,
                    {
                        "branch": branch,
                        "remote": "origin",
                        "force": force
                    }
                )

            return True

        except Exception as e:
            self.operation_logger('push', GIT_STATUS_FAILED, {'error': str(e)})

            # Notify observers of failure
            if self.notify_event:
                self.notify_event(
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
        WHY: Fetch and merge/rebase changes from remote
        RESPONSIBILITY: Update local branch with remote changes
        PATTERNS: Guard clauses for validation
        """
        # Guard: No remote URL configured
        if not self.repo_config.remote_url:
            self.logger.warning("No remote URL configured, skipping pull")
            return False

        try:
            # Get current branch if not specified
            if not branch:
                result = self.run_git_command(['rev-parse', '--abbrev-ref', 'HEAD'])
                branch = result.stdout.decode().strip()

            # Build pull command
            args = ['pull', 'origin', branch]
            if rebase:
                args.append('--rebase')

            self.run_git_command(args)

            self.operation_logger(
                'pull',
                GIT_STATUS_SUCCESS,
                {'branch': branch, 'rebase': rebase}
            )

            self.logger.info(f"Pulled changes from: {branch}")
            return True

        except Exception as e:
            self.operation_logger('pull', GIT_STATUS_FAILED, {'error': str(e)})
            raise GitOperationError(f"Failed to pull changes: {e}")

    def fetch_updates(self, prune: bool = True) -> bool:
        """
        WHY: Download remote refs and objects without merging
        RESPONSIBILITY: Update remote tracking branches
        PATTERNS: Guard clauses for validation
        """
        # Guard: No remote URL configured
        if not self.repo_config.remote_url:
            return False

        try:
            args = ['fetch', 'origin']
            if prune:
                args.append('--prune')

            self.run_git_command(args)

            self.operation_logger('fetch', GIT_STATUS_SUCCESS, {'prune': prune})
            self.logger.info("Fetched updates from remote")
            return True

        except Exception as e:
            self.operation_logger('fetch', GIT_STATUS_FAILED, {'error': str(e)})
            return False

    def save_output_to_repo(
        self,
        source_dir: str,
        commit_message: str,
        branch: Optional[str] = None,
        commit_callback: Optional[Callable] = None
    ) -> bool:
        """
        WHY: Copy Artemis output files to repository
        RESPONSIBILITY: Transfer files and create commit
        PATTERNS: Guard clauses, callback pattern
        """
        try:
            # Switch to target branch if specified
            if branch:
                self.run_git_command(['checkout', branch])

            # Copy files from source to repo
            source_path = Path(source_dir)
            repo_path = Path(self.repo_config.local_path)

            # Guard: Source directory must exist
            if not source_path.exists():
                self.logger.warning(f"Source directory does not exist: {source_dir}")
                return False

            # Copy files (excluding .git)
            self._copy_files_to_repo(source_path, repo_path)

            # Commit changes using callback
            if commit_callback:
                commit_callback(commit_message)

            self.logger.info(f"Saved output to repository: {commit_message}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to save output to repo: {e}")
            return False

    def _build_push_args(
        self,
        branch: str,
        force: bool,
        set_upstream: bool
    ) -> list:
        """
        WHY: Build push command arguments consistently
        RESPONSIBILITY: Construct git push arguments
        PATTERNS: Builder pattern for command construction
        """
        args = ['push']

        if set_upstream:
            args.extend(['-u', 'origin', branch])
        else:
            args.extend(['origin', branch])

        if force:
            args.append('--force')

        return args

    def _copy_files_to_repo(
        self,
        source_path: Path,
        repo_path: Path
    ) -> None:
        """
        WHY: Copy files while excluding git metadata
        RESPONSIBILITY: Transfer files from source to repository
        PATTERNS: Guard clauses for file filtering
        """
        for item in source_path.iterdir():
            # Guard: Skip .git directory
            if item.name == '.git':
                continue

            dest = repo_path / item.name

            if item.is_file():
                shutil.copy2(item, dest)
            else:
                shutil.copytree(item, dest, dirs_exist_ok=True)
