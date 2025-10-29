#!/bin/bash
# Install Git hooks for Artemis
#
# WHY: Automates installation of pre-commit validation hooks
# PATTERNS: Automation, idempotent operations (safe to run multiple times)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
HOOKS_SRC="$SCRIPT_DIR/hooks"
HOOKS_DEST="$REPO_ROOT/.git/hooks"

echo "🔧 Installing Artemis Git hooks..."
echo ""

# Guard: Verify we're in a git repository
if [ ! -d "$REPO_ROOT/.git" ]; then
    echo "❌ Error: Not in a git repository"
    echo "   Current directory: $REPO_ROOT"
    exit 1
fi

# Guard: Verify hooks source directory exists
if [ ! -d "$HOOKS_SRC" ]; then
    echo "❌ Error: Hooks directory not found"
    echo "   Expected: $HOOKS_SRC"
    exit 1
fi

# Install each hook
for hook_file in "$HOOKS_SRC"/*; do
    # Guard: Skip if not a file
    if [ ! -f "$hook_file" ]; then
        continue
    fi

    hook_name=$(basename "$hook_file")
    dest_path="$HOOKS_DEST/$hook_name"

    echo "📝 Installing $hook_name..."

    # Backup existing hook if present
    if [ -f "$dest_path" ] && [ ! -L "$dest_path" ]; then
        backup_path="$dest_path.backup.$(date +%Y%m%d_%H%M%S)"
        echo "   ⚠️  Backing up existing hook to: $(basename "$backup_path")"
        mv "$dest_path" "$backup_path"
    fi

    # Remove old symlink if present
    if [ -L "$dest_path" ]; then
        rm "$dest_path"
    fi

    # Create symlink
    ln -s "$hook_file" "$dest_path"
    chmod +x "$hook_file"

    echo "   ✅ Installed: $hook_name"
done

echo ""
echo "✅ Git hooks installed successfully!"
echo ""
echo "Installed hooks:"
for hook_file in "$HOOKS_SRC"/*; do
    if [ -f "$hook_file" ]; then
        echo "  - $(basename "$hook_file")"
    fi
done
echo ""
echo "These hooks will now run automatically before each commit."
echo "To bypass hooks (NOT RECOMMENDED): git commit --no-verify"
echo ""

exit 0
