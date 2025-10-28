#!/usr/bin/env python3
"""
BACKWARD COMPATIBILITY WRAPPER

WHY: Maintain compatibility with existing code using git_agent
RESPONSIBILITY: Re-export all components from git_agent_pkg
PATTERNS: Facade pattern, backward compatibility wrapper

This module has been refactored and modularized into git_agent_pkg/.
All imports are preserved for backward compatibility.

New code should import from git_agent_pkg directly:
    from git_agent_pkg import GitAgent, RepositoryConfig
"""

# Re-export all public components from the package
from git_agent_pkg import (
    # Core classes
    GitAgent,
    RepositoryConfig,

    # Models and enums
    BranchStrategy,
    CommitConvention,
    GitOperation,
    GIT_REMOTE_ORIGIN,
    GIT_STATUS_SUCCESS,
    GIT_STATUS_FAILED,
    ARTEMIS_FOOTER,

    # Strategy handlers
    BranchStrategyHandler,
    GitFlowStrategyHandler,
    GitHubFlowStrategyHandler,
    TrunkBasedStrategyHandler,
    BranchStrategyFactory,

    # Commit formatters
    CommitMessageFormatter,
    ConventionalCommitFormatter,
    PlainCommitFormatter,
    CommitFormatterFactory,

    # Operations classes (for advanced usage)
    RepositoryOperations,
    BranchOperations,
    CommitOperations,
    RemoteOperations,
    OperationsLogger,
)

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

    # Operations classes
    'RepositoryOperations',
    'BranchOperations',
    'CommitOperations',
    'RemoteOperations',
    'OperationsLogger',
]


# Example usage remains the same
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
    import json
    print(json.dumps(status, indent=2))
