#!/usr/bin/env python3
"""
WHY: Provide unified package interface for git_agent
RESPONSIBILITY: Export all public classes and functions
PATTERNS: Facade pattern for package exports
"""

# Core classes
from .git_agent import GitAgent
from .config import RepositoryConfig

# Models and enums
from .models import (
    BranchStrategy,
    CommitConvention,
    GitOperation,
    GIT_REMOTE_ORIGIN,
    GIT_STATUS_SUCCESS,
    GIT_STATUS_FAILED,
    ARTEMIS_FOOTER
)

# Strategy classes (for advanced usage)
from .branch_strategy import (
    BranchStrategyHandler,
    GitFlowStrategyHandler,
    GitHubFlowStrategyHandler,
    TrunkBasedStrategyHandler,
    BranchStrategyFactory
)

from .commit_formatter import (
    CommitMessageFormatter,
    ConventionalCommitFormatter,
    PlainCommitFormatter,
    CommitFormatterFactory,
    add_artemis_footer
)

# Operations classes (for advanced usage)
from .repo_operations import RepositoryOperations
from .branch_operations import BranchOperations
from .commit_operations import CommitOperations
from .remote_operations import RemoteOperations
from .operations_logger import OperationsLogger

__all__ = [
    # Core
    'GitAgent',
    'RepositoryConfig',

    # Models and enums
    'BranchStrategy',
    'CommitConvention',
    'GitOperation',
    'GIT_REMOTE_ORIGIN',
    'GIT_STATUS_SUCCESS',
    'GIT_STATUS_FAILED',
    'ARTEMIS_FOOTER',

    # Strategy handlers
    'BranchStrategyHandler',
    'GitFlowStrategyHandler',
    'GitHubFlowStrategyHandler',
    'TrunkBasedStrategyHandler',
    'BranchStrategyFactory',

    # Commit formatters
    'CommitMessageFormatter',
    'ConventionalCommitFormatter',
    'PlainCommitFormatter',
    'CommitFormatterFactory',
    'add_artemis_footer',

    # Operations classes
    'RepositoryOperations',
    'BranchOperations',
    'CommitOperations',
    'RemoteOperations',
    'OperationsLogger',
]
