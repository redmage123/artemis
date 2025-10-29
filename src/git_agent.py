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
from git_agent_pkg import GitAgent, RepositoryConfig, BranchStrategy, CommitConvention, GitOperation, GIT_REMOTE_ORIGIN, GIT_STATUS_SUCCESS, GIT_STATUS_FAILED, ARTEMIS_FOOTER, BranchStrategyHandler, GitFlowStrategyHandler, GitHubFlowStrategyHandler, TrunkBasedStrategyHandler, BranchStrategyFactory, CommitMessageFormatter, ConventionalCommitFormatter, PlainCommitFormatter, CommitFormatterFactory, RepositoryOperations, BranchOperations, CommitOperations, RemoteOperations, OperationsLogger
__all__ = ['GitAgent', 'RepositoryConfig', 'BranchStrategy', 'CommitConvention', 'GitOperation', 'GIT_REMOTE_ORIGIN', 'GIT_STATUS_SUCCESS', 'GIT_STATUS_FAILED', 'ARTEMIS_FOOTER', 'BranchStrategyHandler', 'GitFlowStrategyHandler', 'GitHubFlowStrategyHandler', 'TrunkBasedStrategyHandler', 'BranchStrategyFactory', 'CommitMessageFormatter', 'ConventionalCommitFormatter', 'PlainCommitFormatter', 'CommitFormatterFactory', 'RepositoryOperations', 'BranchOperations', 'CommitOperations', 'RemoteOperations', 'OperationsLogger']
if __name__ == '__main__':
    agent = GitAgent(verbose=True)
    config = agent.configure_repository(name='my-awesome-project', local_path='/tmp/my-awesome-project', remote_url='git@github.com:username/my-awesome-project.git', branch_strategy='github_flow', auto_push=False)
    
    logger.log(f'\n✅ Git Agent configured for: {config.name}', 'INFO')
    
    logger.log(f'📁 Local path: {config.local_path}', 'INFO')
    
    logger.log(f'🌿 Branch strategy: {config.branch_strategy}', 'INFO')
    status = agent.get_status()
    
    logger.log(f'\n📊 Repository Status:', 'INFO')
    import json
    
    logger.log(json.dumps(status, indent=2), 'INFO')