#!/bin/bash
# SessionStart hook to detect hooks desync
# Runs setup-hooks.sh --check and warns if hooks need syncing

set -e

# Find the marketplace root (parent of plugins/core/hooks)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MARKETPLACE_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Check if setup-hooks.sh exists
SETUP_SCRIPT="$MARKETPLACE_ROOT/scripts/setup-hooks.sh"
if [[ ! -f "$SETUP_SCRIPT" ]]; then
    exit 0  # Silently exit if not in the marketplace repo
fi

# Detect if we should check project or global settings
# Check project first if we're in a git repo with .claude/settings.json
CHECK_MODE="--global"
if [[ -n "${CLAUDE_PROJECT_DIR:-}" ]]; then
    # Claude sets this env var for project context
    if [[ -f "$CLAUDE_PROJECT_DIR/.claude/settings.json" ]]; then
        CHECK_MODE="--project"
    fi
elif [[ -f ".claude/settings.json" ]]; then
    # Fallback: check current directory
    CHECK_MODE="--project"
fi

# Run the check (suppress stderr, we just want the result)
if ! "$SETUP_SCRIPT" --check "$CHECK_MODE" >/dev/null 2>&1; then
    echo ""
    echo "===================================================="
    echo "  rbw-claude-code: Hooks are out of sync!"
    echo "===================================================="
    echo ""
    echo "  Plugin hooks have changed. Run to update:"
    echo ""
    if [[ "$CHECK_MODE" == "--project" ]]; then
        echo "    $SETUP_SCRIPT --project"
    else
        echo "    $SETUP_SCRIPT"
    fi
    echo ""
    echo "===================================================="
    echo ""
fi
