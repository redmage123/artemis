#!/usr/bin/env python3
"""
WHY: Handle all commit-related git operations
RESPONSIBILITY: Stage files, create commits, and manage commit history
PATTERNS: Single Responsibility Principle, Strategy Pattern
"""

from typing import Optional, List, Any, Callable
from pipeline_observer import EventType

from artemis_logger import ArtemisLogger
from artemis_exceptions import GitOperationError

from .config import RepositoryConfig
from .commit_formatter import CommitFormatterFactory, add_artemis_footer
from .models import CommitConvention, GIT_STATUS_SUCCESS, GIT_STATUS_FAILED


class CommitOperations:
    """
    WHY: Encapsulate all commit-related git operations
    RESPONSIBILITY: Create commits with proper formatting and staging
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

    def commit_changes(
        self,
        message: str,
        files: Optional[List[str]] = None,
        commit_type: Optional[str] = None,
        scope: Optional[str] = None
    ) -> str:
        """
        WHY: Create commits with consistent formatting
        RESPONSIBILITY: Stage files and create commit with formatted message
        PATTERNS: Strategy Pattern for formatting, guard clauses
        """
        # Use Formatter Pattern to format commit message
        convention = CommitConvention(self.repo_config.commit_convention)
        formatter = CommitFormatterFactory.create(convention)
        formatted_message = formatter.format(message, commit_type, scope)
        formatted_message = add_artemis_footer(formatted_message)

        try:
            # Stage files - use dispatch table pattern
            self._stage_files(files)

            # Create commit
            self.run_git_command(['commit', '-m', formatted_message])

            # Get commit hash
            result = self.run_git_command(['rev-parse', 'HEAD'])
            commit_hash = result.stdout.decode().strip()[:8]

            self.operation_logger(
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
            if self.notify_event:
                self.notify_event(
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
                # Note: push_changes will be called from parent orchestrator
                pass

            return commit_hash

        except Exception as e:
            self.operation_logger('commit', GIT_STATUS_FAILED, {'error': str(e)})

            # Notify observers of failure
            if self.notify_event:
                self.notify_event(
                    EventType.GIT_OPERATION_FAILED,
                    {
                        "operation": "commit",
                        "error": str(e),
                        "message": message
                    }
                )

            raise GitOperationError(f"Failed to commit changes: {e}")

    def _stage_files(self, files: Optional[List[str]]) -> None:
        """
        WHY: Stage files before committing
        RESPONSIBILITY: Add files to git staging area
        PATTERNS: Guard clauses for different cases
        """
        # Guard: Stage all files if none specified
        if not files:
            self.run_git_command(['add', '.'])
            return

        # Stage specific files
        self.run_git_command(['add'] + files)

    def get_uncommitted_changes(self) -> List[str]:
        """
        WHY: Check what files have been modified
        RESPONSIBILITY: Query git status for changed files
        PATTERNS: Single Responsibility Principle
        """
        try:
            result = self.run_git_command(['status', '--porcelain'])
            lines = result.stdout.decode().strip().split('\n')
            return [line.strip() for line in lines if line]

        except Exception as e:
            self.logger.error(f"Failed to get uncommitted changes: {e}")
            return []

    def get_commit_history(
        self,
        count: int = 10,
        branch: Optional[str] = None
    ) -> List[dict]:
        """
        WHY: Retrieve commit history for analysis
        RESPONSIBILITY: Query and parse git log
        PATTERNS: Guard clauses for parameter validation
        """
        try:
            args = ['log', f'-{count}', '--pretty=format:%H|%an|%ae|%ad|%s']

            if branch:
                args.append(branch)

            result = self.run_git_command(args)
            lines = result.stdout.decode().strip().split('\n')

            commits = []
            for line in lines:
                # Guard: Skip empty lines
                if not line:
                    continue

                parts = line.split('|')
                if len(parts) >= 5:
                    commits.append({
                        'hash': parts[0][:8],
                        'author_name': parts[1],
                        'author_email': parts[2],
                        'date': parts[3],
                        'message': parts[4]
                    })

            return commits

        except Exception as e:
            self.logger.error(f"Failed to get commit history: {e}")
            return []
