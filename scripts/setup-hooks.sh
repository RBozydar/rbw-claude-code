#!/bin/bash
# Setup script for rbw-claude-code hooks
# Dynamically discovers and configures hooks from all plugins
# Works around Claude Code bug #16288 where plugin hooks are matched but not executed
# See: https://github.com/anthropics/claude-code/issues/16288

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Settings file path
SETTINGS_FILE="$HOME/.claude/settings.json"
BACKUP_FILE=""

# Cleanup/rollback on error
cleanup() {
    local exit_code=$?
    if [[ $exit_code -ne 0 && -n "$BACKUP_FILE" && -f "$BACKUP_FILE" ]]; then
        echo -e "${RED}Error occurred. Restoring settings from backup...${NC}"
        cp "$BACKUP_FILE" "$SETTINGS_FILE"
        echo -e "${GREEN}Settings restored from: $BACKUP_FILE${NC}"
    fi
    exit $exit_code
}
trap cleanup EXIT

echo -e "${GREEN}rbw-claude-code Hook Setup${NC}"
echo "================================================"
echo ""

# Detect marketplace path
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MARKETPLACE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

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

# Create .claude directory if it doesn't exist
mkdir -p "$HOME/.claude"

# Initialize settings file if it doesn't exist or is empty
if [[ ! -s "$SETTINGS_FILE" ]]; then
    echo '{}' > "$SETTINGS_FILE"
fi

# Backup existing settings
BACKUP_FILE="$SETTINGS_FILE.backup.$(date +%Y%m%d_%H%M%S)"
cp "$SETTINGS_FILE" "$BACKUP_FILE"
echo -e "${YELLOW}Backed up existing settings to: $BACKUP_FILE${NC}"
echo ""

# Discover all hooks.json files
echo -e "${BLUE}Discovering hooks...${NC}"
HOOKS_FILES=()
for hooks_file in "$MARKETPLACE_ROOT"/plugins/*/hooks/hooks.json; do
    if [[ -f "$hooks_file" ]]; then
        HOOKS_FILES+=("$hooks_file")
    fi
done

if [[ ${#HOOKS_FILES[@]} -eq 0 ]]; then
    echo -e "${RED}No hooks.json files found in plugins${NC}"
    exit 1
fi

echo "Found ${#HOOKS_FILES[@]} hook configuration(s)"
echo ""

# Process each hooks.json and collect resolved hooks
RESOLVED_HOOKS=()
DISCOVERED_PLUGINS=()

for hooks_file in "${HOOKS_FILES[@]}"; do
    # Get plugin directory (parent of hooks/)
    PLUGIN_DIR="$(dirname "$(dirname "$hooks_file")")"
    PLUGIN_NAME="$(basename "$PLUGIN_DIR")"

    # Resolve ${CLAUDE_PLUGIN_ROOT} to absolute path
    resolved=$(jq --arg root "$PLUGIN_DIR" \
        'walk(if type == "string" then gsub("\\$\\{CLAUDE_PLUGIN_ROOT\\}"; $root) else . end)' \
        "$hooks_file") || {
        echo -e "${RED}Error parsing $hooks_file${NC}"
        exit 1
    }

    RESOLVED_HOOKS+=("$resolved")
    DISCOVERED_PLUGINS+=("$PLUGIN_NAME")
    echo "  - $PLUGIN_NAME"
done

echo ""

# Aggregate all hooks into a single structure
echo -e "${BLUE}Aggregating hooks...${NC}"

# Create a temporary file for aggregation
TEMP_FILE=$(mktemp)

# Write all resolved hooks to temp file (one per line for jq slurp)
for hook in "${RESOLVED_HOOKS[@]}"; do
    echo "$hook" >> "$TEMP_FILE"
done

# Aggregate hooks by event type
AGGREGATED=$(jq -s '
    reduce .[] as $item ({hooks: {PreToolUse: [], PostToolUse: []}};
        .hooks.PreToolUse += ($item.hooks.PreToolUse // []) |
        .hooks.PostToolUse += ($item.hooks.PostToolUse // [])
    )
' "$TEMP_FILE") || {
    echo -e "${RED}Error aggregating hooks${NC}"
    rm -f "$TEMP_FILE"
    exit 1
}

rm -f "$TEMP_FILE"

# Validate hook scripts exist
echo -e "${BLUE}Validating hook scripts...${NC}"
WARNINGS=0

while IFS= read -r cmd; do
    if [[ -n "$cmd" ]]; then
        if [[ ! -f "$cmd" ]]; then
            echo -e "${YELLOW}Warning: Script not found: $cmd${NC}"
            ((WARNINGS++))
        elif [[ ! -x "$cmd" ]]; then
            echo -e "${YELLOW}Warning: Script not executable: $cmd${NC}"
            ((WARNINGS++))
        fi
    fi
done < <(echo "$AGGREGATED" | jq -r '.. | .command? // empty')

if [[ $WARNINGS -eq 0 ]]; then
    echo "  All hook scripts validated"
else
    echo -e "${YELLOW}  $WARNINGS warning(s) found${NC}"
fi
echo ""

# Extract just the hooks object for merging
HOOKS_ONLY=$(echo "$AGGREGATED" | jq '.hooks')

# Merge hooks into existing settings (preserving other settings)
echo -e "${BLUE}Merging into settings...${NC}"
MERGED=$(jq --argjson hooks "$HOOKS_ONLY" '.hooks = $hooks' "$SETTINGS_FILE") || {
    echo -e "${RED}Error merging hooks into settings${NC}"
    exit 1
}

# Write to temp file first (atomic write)
TEMP_SETTINGS=$(mktemp)
echo "$MERGED" | jq '.' > "$TEMP_SETTINGS" || {
    echo -e "${RED}Error writing settings${NC}"
    rm -f "$TEMP_SETTINGS"
    exit 1
}

# Move temp file to settings (atomic)
mv "$TEMP_SETTINGS" "$SETTINGS_FILE"

# Count hooks by type
PRE_BASH=$(echo "$AGGREGATED" | jq '[.hooks.PreToolUse[] | select(.matcher == "Bash") | .hooks | length] | add // 0')
PRE_READ=$(echo "$AGGREGATED" | jq '[.hooks.PreToolUse[] | select(.matcher == "Read") | .hooks | length] | add // 0')
POST_WRITE_EDIT=$(echo "$AGGREGATED" | jq '[.hooks.PostToolUse[] | select(.matcher == "Write|Edit") | .hooks | length] | add // 0')
POST_WRITE=$(echo "$AGGREGATED" | jq '[.hooks.PostToolUse[] | select(.matcher == "Write") | .hooks | length] | add // 0')

echo ""
echo -e "${GREEN}Hooks configured successfully!${NC}"
echo ""
echo "Configured hooks from ${#DISCOVERED_PLUGINS[@]} plugins:"
for plugin in "${DISCOVERED_PLUGINS[@]}"; do
    echo "  - $plugin"
done
echo ""
echo "Hook summary:"
echo "  PreToolUse (Bash):       $PRE_BASH hook(s)"
echo "  PreToolUse (Read):       $PRE_READ hook(s)"
echo "  PostToolUse (Write|Edit): $POST_WRITE_EDIT hook(s)"
echo "  PostToolUse (Write):     $POST_WRITE hook(s)"
echo ""
echo -e "${YELLOW}Note: This is a workaround for Claude Code issue #16288${NC}"
echo "Plugin hooks should work natively once the bug is fixed."
echo ""
echo "To verify hooks are active, run: /hooks"
echo ""
echo -e "${GREEN}Backup saved at: $BACKUP_FILE${NC}"

# Clear the trap since we succeeded
trap - EXIT
