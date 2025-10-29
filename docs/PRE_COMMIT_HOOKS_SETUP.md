# Pre-Commit Hooks Setup for Artemis

## Overview

Artemis uses pre-commit hooks to enforce code quality standards defined in `claude.md`. This prevents code violations from being committed.

## Installation

### Option 1: Using pre-commit framework (Recommended)

```bash
# Install pre-commit (if not already installed)
pip install pre-commit

# Install the git hooks
pre-commit install

# Run on all files to test
pre-commit run --all-files
```

### Option 2: Manual Git Hook (Already Configured)

The git hook is already set up at `.git/hooks/pre-commit` and will run automatically on every commit.

## What Gets Checked

The pre-commit hooks check for **ALL** violations (not just critical):

1. **Nested If Statements** (depth >= 2) - CRITICAL
   - ❌ Blocks: Any nested if statements
   - ✅ Requires: Early return pattern

2. **Long If/Elif Chains** (3+ branches) - WARNING
   - ❌ Blocks: If/elif chains with 3+ branches
   - ✅ Requires: Strategy pattern or dict mapping

3. **TODO Comments** - INFO
   - ❌ Blocks: TODO/FIXME/XXX comments in production code
   - ✅ Requires: Resolve or move to issue tracker

4. **Code Formatting**
   - Black (line length: 100)
   - isort (import sorting)
   - Flake8 (linting)

5. **File Quality**
   - No trailing whitespace
   - Files end with newline
   - Valid YAML/JSON
   - No large files (>1MB)
   - No merge conflicts

## How It Works

### On Git Commit

```bash
git commit -m "Your commit message"
```

If violations are found:
```
🔍 Running Artemis code standards checks...
📝 Checking 15 Python files...

❌ CODE STANDARDS VIOLATION DETECTED

NESTED IF:
----------------------------------------------------------------------
📄 src/my_file.py
   Line 42 [CRITICAL]: Nested if at depth 2 - use early returns instead

Your commit has been blocked.
```

### Fixing Violations

1. Review the file and line number
2. Refactor using early return pattern:

```python
# ❌ BAD: Nested ifs
if condition1:
    if condition2:
        do_something()

# ✅ GOOD: Early returns
if not condition1:
    return
if not condition2:
    return
do_something()
```

3. See `REFACTORING_GUIDE.md` for detailed patterns
4. Commit again

### Bypassing Checks (NOT RECOMMENDED)

```bash
git commit --no-verify -m "Emergency fix"
```

**Only use this for true emergencies!**

**IMPORTANT:** The pre-commit hook now blocks ALL violations (critical, warning, and info), not just critical violations. This ensures complete adherence to claude.md coding standards.

## Manual Scanning

Run the scanner anytime without committing:

```bash
# Scan all files (all violations)
python3 src/code_standards_scanner.py --root src

# Critical violations only
python3 src/code_standards_scanner.py --root src --critical-only

# Specific directory
python3 src/code_standards_scanner.py --root src/stages

# Note: Pre-commit hook runs WITHOUT --critical-only flag,
# so it blocks ALL violations (critical, warning, and info)
```

## Pre-Commit Configuration

See `.pre-commit-config.yaml` for full configuration.

To update hooks:
```bash
pre-commit autoupdate
```

To run specific hook:
```bash
pre-commit run black --all-files
pre-commit run artemis-code-standards --all-files
```

## Troubleshooting

### Hook doesn't run
```bash
# Reinstall hooks
pre-commit install --install-hooks

# Check hook is executable
chmod +x .git/hooks/pre-commit
```

### False positives
If the scanner incorrectly flags code, please report it. The code standards scanner uses AST analysis and should be accurate.

### Performance
The scanner typically runs in < 2 seconds for the full codebase.

## Benefits

✅ **Prevents technical debt** - Catches violations before they enter the codebase
✅ **Consistent code quality** - Enforces claude.md standards automatically
✅ **Faster code review** - Reviewers don't need to check for basic violations
✅ **Self-documenting** - Clear error messages explain what to fix

## Next Steps

After setting up pre-commit hooks:
1. Read `claude.md` to understand all coding standards
2. Review `REFACTORING_GUIDE.md` for refactoring patterns
3. Run `pre-commit run --all-files` to check existing code
4. Fix any violations before committing new code
