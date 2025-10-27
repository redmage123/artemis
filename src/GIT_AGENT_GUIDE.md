# Git Agent - Autonomous Build Master

The Git Agent acts as an autonomous build master for Artemis, managing all git operations for projects being created or refactored. It handles repository initialization, branching strategies, commits, and deployment workflows.

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Repository Configuration](#repository-configuration)
- [Branching Strategies](#branching-strategies)
- [Usage Examples](#usage-examples)
- [Integration with Artemis](#integration-with-artemis)
- [Environment Variables](#environment-variables)

## Overview

The Git Agent provides:

- **Repository Management**: Initialize, clone, or configure existing repositories
- **Branching Strategies**: GitFlow, GitHub Flow, or trunk-based development
- **Commit Management**: Conventional commits with automatic formatting
- **Workflow Automation**: Auto-push, auto-pull, PR/MR creation
- **Build Master Operations**: Tag creation, branch cleanup, merge management

## Key Features

### 1. Repository Initialization

The Git Agent can:
- Create new repositories locally
- Clone existing repositories from GitHub/GitLab
- Configure existing repositories
- Set up remote tracking automatically

### 2. Branching Strategies

**GitHub Flow** (Default for GitHub projects)
```
main
  └─ feature/card-123-user-authentication
  └─ feature/card-124-api-integration
```

**GitFlow** (Default for GitLab projects)
```
main
  └─ develop
      ├─ feature/user-authentication
      ├─ release/v1.2.0
      └─ hotfix/critical-bug-fix
```

**Trunk-Based Development**
```
main
  └─ card-123-quick-fix
  └─ card-124-small-feature
```

### 3. Conventional Commits

Automatically formats commits following conventions:

```
feat(auth): add OAuth2 authentication
fix(api): resolve connection timeout issue
docs(readme): update installation instructions
refactor(core): simplify error handling

🤖 Generated with Artemis Autonomous Pipeline
```

### 4. Automation Features

- **Auto-push**: Automatically push after commits (configurable)
- **Auto-pull**: Pull latest before operations (configurable)
- **Branch cleanup**: Remove merged branches
- **Tag creation**: Semantic versioning support
- **PR/MR creation**: Create pull/merge requests on completion

## Repository Configuration

### Local Development

For developing projects locally without remote repository:

```yaml
# conf/repository/local_dev.yaml
name: my-project
local_path: ../../.artemis_data/target_repo
remote_url: null
branch_strategy: github_flow
auto_push: false
create_if_missing: true
```

**Environment Variables:**
```bash
export ARTEMIS_TARGET_REPO_NAME="my-awesome-project"
export ARTEMIS_TARGET_REPO_PATH="/path/to/local/repo"
```

**CLI Usage:**
```bash
python artemis_orchestrator.py \
  card_id=card-001 \
  repository=local_dev \
  repository.name=my-project
```

### GitHub Remote

For working with GitHub repositories:

```yaml
# conf/repository/github_remote.yaml
name: ${ARTEMIS_TARGET_REPO_NAME}
local_path: ../../.artemis_data/target_repo
remote_url: ${ARTEMIS_TARGET_REPO_URL}
branch_strategy: github_flow
auto_push: false
create_pr_on_complete: true
```

**Environment Variables:**
```bash
export ARTEMIS_TARGET_REPO_NAME="my-project"
export ARTEMIS_TARGET_REPO_PATH="../../.artemis_data/my-project"
export ARTEMIS_TARGET_REPO_URL="git@github.com:username/my-project.git"
export ARTEMIS_AUTO_PUSH=false
export ARTEMIS_CREATE_PR=true
```

**CLI Usage:**
```bash
python artemis_orchestrator.py \
  card_id=card-001 \
  repository=github_remote \
  repository.name=my-project \
  repository.remote_url=git@github.com:username/my-project.git
```

### GitLab Remote

For working with GitLab repositories:

```yaml
# conf/repository/gitlab_remote.yaml
name: ${ARTEMIS_TARGET_REPO_NAME}
local_path: ../../.artemis_data/target_repo
remote_url: ${ARTEMIS_TARGET_REPO_URL}
branch_strategy: gitflow
auto_push: false
create_mr_on_complete: true
```

**Environment Variables:**
```bash
export ARTEMIS_TARGET_REPO_NAME="my-project"
export ARTEMIS_TARGET_REPO_PATH="../../.artemis_data/my-project"
export ARTEMIS_TARGET_REPO_URL="git@gitlab.com:username/my-project.git"
export ARTEMIS_CREATE_MR=true
```

## Branching Strategies

### GitHub Flow

Best for: Continuous deployment, simple workflows

```python
from git_agent import GitAgent, RepositoryConfig

agent = GitAgent()
config = agent.configure_repository(
    name="web-app",
    local_path="/path/to/web-app",
    remote_url="git@github.com:user/web-app.git",
    branch_strategy="github_flow"
)

# Create feature branch from main
branch = agent.create_feature_branch(
    feature_name="user-authentication",
    card_id="card-123"
)
# Creates: feature/card-123-user-authentication
```

### GitFlow

Best for: Release-based workflows, larger teams

```python
agent = GitAgent()
config = agent.configure_repository(
    name="enterprise-app",
    local_path="/path/to/enterprise-app",
    remote_url="git@gitlab.com:org/enterprise-app.git",
    branch_strategy="gitflow"
)

# Create feature branch from develop
branch = agent.create_feature_branch(
    feature_name="payment-integration",
    card_id="card-456"
)
# Creates: feature/card-456-payment-integration
```

### Trunk-Based Development

Best for: Small teams, rapid iteration

```python
agent = GitAgent()
config = agent.configure_repository(
    name="microservice",
    local_path="/path/to/microservice",
    branch_strategy="trunk_based"
)

# Create short-lived branch from main
branch = agent.create_feature_branch(
    feature_name="add-caching",
    card_id="card-789"
)
# Creates: card-789-add-caching
```

## Usage Examples

### Basic Workflow

```python
from git_agent import GitAgent, RepositoryConfig

# Initialize agent
agent = GitAgent(verbose=True)

# Configure target repository
config = agent.configure_repository(
    name="my-app",
    local_path="/path/to/my-app",
    remote_url="git@github.com:username/my-app.git",
    branch_strategy="github_flow",
    auto_push=False
)

# Create feature branch
branch = agent.create_feature_branch(
    feature_name="api-endpoints",
    card_id="card-001"
)

# ... Artemis develops the feature ...

# Commit changes with conventional commit
commit_hash = agent.commit_changes(
    message="add REST API endpoints for user management",
    commit_type="feat",
    scope="api"
)

# Push to remote
agent.push_changes(set_upstream=True)

# Get repository status
status = agent.get_status()
print(f"Branch: {status['branch']}")
print(f"Unpushed commits: {status['unpushed_commits']}")
```

### Working with Existing Repository

```python
# Configure existing repository
agent = GitAgent()
config = agent.configure_repository(
    name="existing-project",
    local_path="/path/to/existing-project",
    remote_url="git@github.com:username/existing-project.git",
    create_if_missing=False  # Don't create if doesn't exist
)

# Pull latest changes
agent.pull_changes(rebase=True)

# Create feature branch
branch = agent.create_feature_branch("refactor-auth")

# ... Make changes ...

# Commit and push
agent.commit_changes(
    message="simplify authentication logic",
    commit_type="refactor",
    scope="auth"
)
agent.push_changes()
```

### Automated Workflow

```python
# Enable auto-push for CI/CD pipeline
agent = GitAgent()
config = agent.configure_repository(
    name="automated-project",
    local_path="/tmp/automated-project",
    remote_url="git@github.com:bot/automated-project.git",
    auto_push=True  # Automatically push after commits
)

# Create branch
branch = agent.create_feature_branch("automated-fix")

# Commit (will auto-push)
agent.commit_changes(
    message="fix critical bug in payment processor",
    commit_type="fix",
    scope="payments"
)
# Changes automatically pushed!

# Create tag for release
agent.create_tag(
    tag_name="v1.2.3",
    message="Release version 1.2.3",
    push=True
)
```

### Save Artemis Output to Repository

```python
# Configure target repository
agent = GitAgent()
config = agent.configure_repository(
    name="target-project",
    local_path="/path/to/target-project",
    remote_url="git@github.com:username/target-project.git"
)

# Create feature branch
branch = agent.create_feature_branch("artemis-generated-feature")

# Save Artemis output to repository
agent.save_output_to_repo(
    source_dir="/tmp/artemis-output/card-001",
    commit_message="implement user authentication feature",
    branch=branch
)

# Push changes
agent.push_changes()
```

## Integration with Artemis

### In Development Stage

```python
# src/stages/development_stage.py

from git_agent import GitAgent

class DevelopmentStage(PipelineStage):
    def __init__(self, config, git_agent: GitAgent):
        self.config = config
        self.git_agent = git_agent

    def execute(self, card: Dict, context: Dict) -> Dict:
        # Create feature branch
        branch = self.git_agent.create_feature_branch(
            feature_name=card['title'],
            card_id=card['id']
        )

        # ... Develop code ...

        # Commit changes
        self.git_agent.commit_changes(
            message=f"implement {card['title']}",
            commit_type="feat"
        )

        return {"status": "success", "branch": branch}
```

### In ArtemisOrchestrator

```python
# src/artemis_orchestrator.py

from git_agent import GitAgent, RepositoryConfig
from hydra import compose, initialize

@hydra.main(config_path="conf", config_name="config", version_base=None)
def main(cfg):
    # Initialize Git Agent with config
    git_agent = GitAgent(verbose=cfg.logging.verbose)

    # Configure from Hydra config
    repo_config = git_agent.configure_repository(
        name=cfg.repository.name,
        local_path=cfg.repository.local_path,
        remote_url=cfg.repository.remote_url,
        branch_strategy=cfg.repository.branch_strategy,
        auto_push=cfg.repository.auto_push
    )

    # Pass git_agent to stages
    orchestrator = ArtemisOrchestrator(
        card_id=cfg.card_id,
        git_agent=git_agent,
        ...
    )

    # Run pipeline
    orchestrator.run_full_pipeline()

    # Save git operations log
    git_agent.save_operations_log()
```

## Environment Variables

### Repository Configuration

```bash
# Repository identification
export ARTEMIS_TARGET_REPO_NAME="my-project"
export ARTEMIS_TARGET_REPO_PATH="/path/to/repo"
export ARTEMIS_TARGET_REPO_URL="git@github.com:username/my-project.git"

# Automation settings
export ARTEMIS_AUTO_PUSH=false
export ARTEMIS_AUTO_PULL=true
export ARTEMIS_CREATE_PR=true
export ARTEMIS_CREATE_MR=true

# Artifact storage
export ARTEMIS_ARTIFACT_PATH="../.artemis_data/artifacts"
```

### Complete Example

```bash
# Set up environment
export ARTEMIS_TARGET_REPO_NAME="awesome-api"
export ARTEMIS_TARGET_REPO_PATH="/home/user/projects/awesome-api"
export ARTEMIS_TARGET_REPO_URL="git@github.com:username/awesome-api.git"
export ARTEMIS_AUTO_PUSH=false
export ARTEMIS_CREATE_PR=true

# Run Artemis with GitHub remote repository
python artemis_orchestrator.py \
  card_id=card-001 \
  repository=github_remote
```

## Git Operations Log

All git operations are tracked and can be exported:

```python
# Get operations summary
summary = agent.get_operations_summary()
print(f"Total operations: {summary['total_operations']}")
print(f"Success rate: {summary['success_rate']}")

# Save log
log_file = agent.save_operations_log()
print(f"Log saved to: {log_file}")
```

**Example Log:**
```json
{
  "total_operations": 15,
  "successful": 14,
  "failed": 1,
  "success_rate": "93.3%",
  "repository": {
    "name": "my-project",
    "local_path": "/path/to/my-project",
    "remote_url": "git@github.com:username/my-project.git",
    "branch_strategy": "github_flow"
  },
  "operations": [
    {
      "operation_type": "init_repository",
      "timestamp": "2025-10-26T10:30:00Z",
      "status": "success",
      "details": {"path": "/path/to/my-project"}
    },
    {
      "operation_type": "create_feature_branch",
      "timestamp": "2025-10-26T10:31:00Z",
      "status": "success",
      "details": {
        "branch": "feature/card-001-api-endpoints",
        "feature": "api-endpoints"
      }
    }
  ]
}
```

## Protected Branches

Protected branches prevent accidental force pushes:

```yaml
# In repository config
protected_branches:
  - main
  - master
  - production
  - develop
```

Force push to protected branches will be blocked:

```python
agent.push_changes(branch="main", force=True)
# ❌ Error: Cannot force push to protected branch: main
```

## Branch Cleanup

Automatically clean up merged branches:

```python
# Clean up local merged branches
deleted = agent.cleanup_merged_branches()
print(f"Deleted {len(deleted)} branches")

# Also delete from remote
deleted = agent.cleanup_merged_branches(delete_remote=True)

# Exclude specific branches
deleted = agent.cleanup_merged_branches(
    exclude_branches=["staging", "qa"]
)
```

## Best Practices

1. **Use Environment Variables**: Configure repositories via environment variables for flexibility
2. **Conventional Commits**: Always use commit types (feat, fix, docs, etc.) for clarity
3. **Branch Naming**: Include card IDs in branch names for traceability
4. **Auto-push Carefully**: Only enable auto-push for trusted automated workflows
5. **Review Operations Log**: Check git operations log for audit trail
6. **Protected Branches**: Always configure protected branches for critical branches
7. **Cleanup Regularly**: Run branch cleanup after completing features

## Troubleshooting

### Repository Not Found

```python
# Ensure create_if_missing is enabled
config = agent.configure_repository(
    name="my-project",
    local_path="/path/to/my-project",
    create_if_missing=True  # Will create if doesn't exist
)
```

### Authentication Issues

```bash
# Ensure SSH keys are set up
ssh-add ~/.ssh/id_rsa

# Or use HTTPS with credentials
export ARTEMIS_TARGET_REPO_URL="https://username:token@github.com/username/repo.git"
```

### Push Rejected

```python
# Pull latest changes first
agent.pull_changes(rebase=True)

# Then push
agent.push_changes()
```

## Summary

The Git Agent provides Artemis with autonomous build master capabilities:

✅ **Repository Management**: Initialize, clone, configure repositories
✅ **Branching Strategies**: GitHub Flow, GitFlow, trunk-based development
✅ **Conventional Commits**: Automatic formatting and best practices
✅ **Workflow Automation**: Auto-push, auto-pull, PR/MR creation
✅ **Operations Tracking**: Complete audit trail of all git operations
✅ **Integration Ready**: Seamless integration with ArtemisOrchestrator

The Git Agent acts as Artemis's interface to version control, ensuring all code generation and refactoring is properly tracked, branched, and integrated into target repositories.
