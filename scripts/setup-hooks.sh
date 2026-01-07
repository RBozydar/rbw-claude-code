#!/bin/bash
# Setup script for rbw-claude-code hooks
# Works around Claude Code bug where plugin hooks are matched but not executed
# See: https://github.com/anthropics/claude-code/issues/16288

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}rbw-claude-code Hook Setup${NC}"
echo "================================================"
echo ""

# Detect marketplace path
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MARKETPLACE_ROOT="$(dirname "$SCRIPT_DIR")"

# Verify we're in the right directory
if [[ ! -f "$MARKETPLACE_ROOT/.claude-plugin/marketplace.json" ]]; then
    echo -e "${RED}Error: Cannot find marketplace.json${NC}"
    echo "Please run this script from the rbw-claude-code repository"
    exit 1
fi

echo "Marketplace path: $MARKETPLACE_ROOT"
echo ""

# Check for jq
if ! command -v jq &> /dev/null; then
    echo -e "${RED}Error: jq is required but not installed${NC}"
    echo "Install with: brew install jq (macOS) or apt install jq (Linux)"
    exit 1
fi

# Settings file path
SETTINGS_FILE="$HOME/.claude/settings.json"

# Create .claude directory if it doesn't exist
mkdir -p "$HOME/.claude"

# Initialize settings file if it doesn't exist
if [[ ! -f "$SETTINGS_FILE" ]]; then
    echo '{}' > "$SETTINGS_FILE"
fi

# Generate hooks configuration
generate_hooks() {
    cat <<EOF
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "$MARKETPLACE_ROOT/plugins/enforce-uv/hooks/enforce_uv.py",
            "timeout": 30
          },
          {
            "type": "command",
            "command": "$MARKETPLACE_ROOT/plugins/conventional-commits/hooks/conventional_commits.py",
            "timeout": 10
          },
          {
            "type": "command",
            "command": "$MARKETPLACE_ROOT/plugins/git-safety-guard/hooks/git_safety_guard.py",
            "timeout": 10
          },
          {
            "type": "command",
            "command": "$MARKETPLACE_ROOT/plugins/safety-guard/hooks/safety_guard_bash.py",
            "timeout": 10
          }
        ]
      },
      {
        "matcher": "Read",
        "hooks": [
          {
            "type": "command",
            "command": "$MARKETPLACE_ROOT/plugins/protect-env/hooks/protect_env.py",
            "timeout": 10
          },
          {
            "type": "command",
            "command": "$MARKETPLACE_ROOT/plugins/safety-guard/hooks/safety_guard_read.py",
            "timeout": 10
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "$MARKETPLACE_ROOT/plugins/python-format/hooks/format_python.py",
            "timeout": 60
          },
          {
            "type": "command",
            "command": "$MARKETPLACE_ROOT/plugins/python-typecheck/hooks/typecheck.py",
            "timeout": 120
          }
        ]
      },
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "$MARKETPLACE_ROOT/plugins/test-reminder/hooks/test_reminder.py",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
EOF
}

# Backup existing settings
if [[ -f "$SETTINGS_FILE" ]]; then
    BACKUP_FILE="$SETTINGS_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    cp "$SETTINGS_FILE" "$BACKUP_FILE"
    echo -e "${YELLOW}Backed up existing settings to: $BACKUP_FILE${NC}"
fi

# Read existing settings
EXISTING_SETTINGS=$(cat "$SETTINGS_FILE")

# Generate new hooks
NEW_HOOKS=$(generate_hooks)

# Merge hooks into settings
# This preserves existing settings and adds/updates the hooks section
MERGED_SETTINGS=$(echo "$EXISTING_SETTINGS" | jq --argjson hooks "$(echo "$NEW_HOOKS" | jq '.hooks')" '.hooks = $hooks')

# Write merged settings
echo "$MERGED_SETTINGS" | jq '.' > "$SETTINGS_FILE"

echo ""
echo -e "${GREEN}Hooks configured successfully!${NC}"
echo ""
echo "The following hooks have been added to $SETTINGS_FILE:"
echo ""
echo "PreToolUse (Bash):"
echo "  - enforce-uv: Block bare python/pip/pytest commands"
echo "  - conventional-commits: Validate commit message format"
echo "  - git-safety-guard: Block destructive git commands"
echo "  - safety-guard: Block dangerous bash commands"
echo ""
echo "PreToolUse (Read):"
echo "  - protect-env: Block reading .env files"
echo "  - safety-guard: Block reading sensitive files"
echo ""
echo "PostToolUse (Write|Edit):"
echo "  - python-format: Auto-format Python with ruff"
echo "  - python-typecheck: Run type checking with pyright"
echo ""
echo "PostToolUse (Write):"
echo "  - test-reminder: Remind to add tests for new Python files"
echo ""
echo -e "${YELLOW}Note: This is a workaround for Claude Code issue #16288${NC}"
echo "Plugin hooks should work natively once the bug is fixed."
echo ""
echo "To verify hooks are active, run: /hooks"
