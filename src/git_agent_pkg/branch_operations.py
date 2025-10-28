#!/usr/bin/env python3
"""
WHY: Handle all branch-related git operations
RESPONSIBILITY: Create, switch, merge, and manage branches
PATTERNS: Single Responsibility Principle, guard clauses
"""

import subprocess
from pathlib import Path
from typing import Optional, List, Any, Callable
from pipeline_observer import EventType, PipelineEvent

from artemis_logger import ArtemisLogger
from artemis_exceptions import GitOperationError

from .config import RepositoryConfig
from .branch_strategy import BranchStrategyFactory
from .models import BranchStrategy, GIT_REMOTE_ORIGIN, GIT_STATUS_SUCCESS, GIT_STATUS_FAILED


class BranchOperations:
    """
    WHY: Encapsulate all branch-related git operations
    RESPONSIBILITY: Manage feature branches, merging, and cleanup
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

    def create_feature_branch(
        self,
        feature_name: str,
        card_id: Optional[str] = None
    ) -> str:
        """
        WHY: Create branch following configured branching strategy
        RESPONSIBILITY: Build branch name and create branch
        PATTERNS: Strategy Pattern, guard clauses
        """
        # Use Strategy Pattern to determine branch details
        strategy = BranchStrategy(self.repo_config.branch_strategy)
        strategy_handler = BranchStrategyFactory.create(strategy)

        base_branch = strategy_handler.get_base_branch(self.repo_config.default_branch)
        branch_name = self._build_branch_name(strategy_handler, feature_name, card_id)

        try:
            # Ensure on base branch and up to date
            self.run_git_command(['checkout', base_branch])

            if self.repo_config.remote_url:
                self.run_git_command(['pull', GIT_REMOTE_ORIGIN, base_branch])

            # Create and checkout feature branch
            self.run_git_command(['checkout', '-b', branch_name])

            self.operation_logger(
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
            if self.notify_event:
                self.notify_event(
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
            self.operation_logger('create_feature_branch', GIT_STATUS_FAILED, {'error': str(e)})

            # Notify observers of failure
            if self.notify_event:
                self.notify_event(
                    EventType.GIT_OPERATION_FAILED,
                    {
                        "operation": "create_feature_branch",
                        "error": str(e),
                        "feature_name": feature_name
                    },
                    card_id=card_id
                )

            raise GitOperationError(f"Failed to create feature branch: {e}")

    def cleanup_merged_branches(
        self,
        delete_remote: bool = False,
        exclude_branches: Optional[List[str]] = None
    ) -> List[str]:
        """
        WHY: Remove branches that have been merged to maintain clean history
        RESPONSIBILITY: Identify and delete merged branches
        PATTERNS: Guard clauses, safe deletion with protections
        """
        base_branch = self.repo_config.default_branch
        protected = exclude_branches or []
        protected.extend([base_branch, 'develop', 'main', 'master'])

        try:
            # Get merged branches
            result = self.run_git_command(['branch', '--merged', base_branch])
            branches = result.stdout.decode().strip().split('\n')

            deleted = []
            for branch in branches:
                branch = branch.strip().replace('* ', '')

                # Guard: Skip if branch is empty or protected
                if not branch:
                    continue
                if branch in protected:
                    continue

                try:
                    self.run_git_command(['branch', '-d', branch])
                    deleted.append(branch)

                    # Delete remote branch if requested
                    if delete_remote and self.repo_config.remote_url:
                        self.run_git_command(
                            ['push', 'origin', '--delete', branch],
                            check=False
                        )
                except Exception:
                    # Continue with other branches even if one fails
                    pass

            self.operation_logger(
                'cleanup_branches',
                GIT_STATUS_SUCCESS,
                {'deleted': deleted, 'count': len(deleted)}
            )

            self.logger.info(f"Cleaned up {len(deleted)} merged branches")
            return deleted

        except Exception as e:
            self.operation_logger('cleanup_branches', GIT_STATUS_FAILED, {'error': str(e)})
            return []

    def create_tag(
        self,
        tag_name: str,
        message: Optional[str] = None,
        push: bool = True
    ) -> bool:
        """
        WHY: Mark specific commits with version tags
        RESPONSIBILITY: Create and optionally push git tags
        PATTERNS: Guard clauses for validation
        """
        try:
            args = ['tag']

            # Add annotated tag if message provided
            if message:
                args.extend(['-a', tag_name, '-m', message])
            else:
                args.append(tag_name)

            self.run_git_command(args)

            # Push tag to remote if configured
            if push and self.repo_config.remote_url:
                self.run_git_command(['push', 'origin', tag_name])

            self.operation_logger(
                'create_tag',
                GIT_STATUS_SUCCESS,
                {'tag': tag_name, 'pushed': push}
            )

            self.logger.info(f"Created tag: {tag_name}")
            return True

        except Exception as e:
            self.operation_logger('create_tag', GIT_STATUS_FAILED, {'error': str(e)})
            return False

    def _sanitize_branch_name(self, name: str) -> str:
        """
        WHY: Ensure branch names follow git conventions
        RESPONSIBILITY: Clean and normalize branch names
        PATTERNS: Single Responsibility Principle
        """
        return name.lower().replace(' ', '-').replace('_', '-')

    def _build_branch_name(
        self,
        strategy_handler: Any,
        feature_name: str,
        card_id: Optional[str] = None
    ) -> str:
        """
        WHY: Construct branch name following strategy conventions
        RESPONSIBILITY: Combine prefix, card ID, and feature name
        PATTERNS: Strategy Pattern delegation
        """
        prefix = strategy_handler.get_branch_prefix()
        name = f"{card_id}-{feature_name}" if card_id else feature_name
        return self._sanitize_branch_name(f"{prefix}{name}")
