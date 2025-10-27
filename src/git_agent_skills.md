# Git Agent - Skills

## Agent Overview
**File**: `git_agent.py`
**Purpose**: Autonomous Git operations manager and build master
**Single Responsibility**: Handle all Git workflows for the Artemis pipeline

## Core Skills

### 1. Repository Management
- **Initialization**: Create new Git repositories
- **Cloning**: Clone remote repositories
- **Configuration**: Set user name, email, remote URLs
- **Submodule Management**: Handle Git submodules
- **Target Repository**: Configure output repository location

### 2. Branch Strategies
- **GitFlow**: `main`, `develop`, `feature/*`, `release/*`, `hotfix/*`
- **GitHub Flow**: `main`, `feature/*`
- **Trunk-Based Development**: `main` with short-lived branches
- **Custom Strategies**: Configurable branch patterns

### 3. Commit Management
- **Conventional Commits**: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
- **Semantic Commits**: Similar to conventional with semantic versioning hints
- **Custom Conventions**: User-defined commit formats
- **Artemis Footer**: Auto-appends "🤖 Generated with Artemis" signature

### 4. Branch Operations
- **Create Branches**: Feature, release, hotfix branches
- **Switch Branches**: Checkout existing branches
- **Merge Branches**: Fast-forward and recursive merge strategies
- **Delete Branches**: Local and remote branch cleanup
- **Branch Listing**: List all local and remote branches

### 5. Remote Operations
- **Push**: Push commits to remote with auto-retry
- **Pull**: Pull latest changes with conflict detection
- **Fetch**: Fetch remote updates without merging
- **Remote Management**: Add, remove, rename remotes
- **Force Push Protection**: Prevents accidental force pushes

### 6. Pull Request Management
- **PR Creation**: Create PRs with title, description, reviewers
- **PR Merging**: Merge PRs with squash/rebase/merge strategies
- **PR Status**: Check PR merge status and conflicts
- **Auto-Push**: Optional automatic push to remote

### 7. Status and History
- **Status Checking**: Modified, staged, untracked files
- **Commit History**: View commit log with filtering
- **Diff Viewing**: Changes between commits/branches
- **Blame**: Track line-by-line authorship

### 8. Conflict Resolution
- **Conflict Detection**: Identifies merge conflicts
- **Conflict Reporting**: Detailed conflict information
- **Manual Resolution**: Guides through conflict resolution
- **Abort Merge**: Cancel problematic merges

## Branch Strategy Handlers

### GitFlow Strategy
- Base branch: `develop`
- Feature prefix: `feature/`
- Release prefix: `release/`
- Hotfix prefix: `hotfix/`

### GitHub Flow Strategy
- Base branch: `main`
- Feature prefix: `feature/`
- No release branches (continuous deployment)

### Trunk-Based Strategy
- Base branch: `main`
- Short-lived feature branches
- Frequent integration

## Commit Conventions

### Conventional Commits
```
feat: Add user authentication
fix: Resolve login timeout issue
docs: Update API documentation
refactor: Simplify payment processing
test: Add unit tests for cart module
chore: Update dependencies
```

### With Artemis Footer
```
feat: Add user authentication

Implemented JWT-based authentication with role-based access control

🤖 Generated with Artemis Autonomous Pipeline
```

## Configuration

**Repository Config**:
```python
RepositoryConfig(
    name="my-project",
    local_path="/path/to/repo",
    remote_url="https://github.com/user/repo.git",
    branch_strategy="github_flow",
    default_branch="main",
    commit_convention="conventional",
    auto_push=False,
    create_if_missing=True
)
```

## Dependencies

- `artemis_logger`: Logging operations
- `artemis_exceptions`: Error handling
- `pipeline_observer`: Event notifications
- Native `subprocess` for Git commands

## Usage Patterns

```python
# Initialize Git agent
git = GitAgent(
    repo_path="/path/to/repo",
    logger=logger,
    branch_strategy="github_flow"
)

# Create feature branch
git.create_branch("feature/user-auth")

# Commit changes
git.commit(
    message="feat: Add user authentication",
    file_patterns=["src/auth/*"]
)

# Push to remote
git.push(branch="feature/user-auth")

# Create pull request
pr_url = git.create_pull_request(
    title="Add User Authentication",
    description="Implements JWT-based auth",
    source_branch="feature/user-auth",
    target_branch="main"
)
```

## Design Patterns

- **Strategy Pattern**: Pluggable branch strategies
- **Builder Pattern**: Repository configuration
- **Command Pattern**: Git operations as commands
- **Template Method**: Standard Git workflows

## Error Handling

- **GitOperationError**: General Git operation failures
- **RepositoryNotFoundError**: Missing repository
- **Conflict Detection**: Merge and rebase conflicts
- **Auto-Retry**: Transient network failures

## Integration Points

- **Development Stage**: Commits generated code
- **Integration Stage**: Merges feature branches
- **Deployment Stage**: Tags releases
- **Pipeline Observer**: Publishes Git events

## Safety Features

- **Pre-commit Validation**: Checks before committing
- **Force Push Protection**: Prevents data loss
- **Conflict Alerts**: Warns about merge conflicts
- **Branch Protection**: Respects protected branches
- **Dry-Run Mode**: Test operations without execution

## Operation Tracking

- **Operation Log**: Records all Git operations
- **Timestamps**: When operations occurred
- **Status**: Success/failure tracking
- **Error Details**: Detailed failure information
- **Statistics**: Operation counts and timings
