#!/bin/bash
# Setup script for rbw-claude-code hooks
# Dynamically discovers and configures hooks from all plugins
# Works around Claude Code bug #16288 where plugin hooks are matched but not executed
# See: https://github.com/anthropics/claude-code/issues/16288
#
# Usage:
#   ./setup-hooks.sh           # Install to global ~/.claude/settings.json
#   ./setup-hooks.sh --project # Install to current project's .claude/settings.json

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
INSTALL_MODE="global"
CHECK_MODE="false"
for arg in "$@"; do
    case $arg in
        --project|-p)
            INSTALL_MODE="project"
            shift
            ;;
        --global|-g)
            INSTALL_MODE="global"
            shift
            ;;
        --check|-c)
            CHECK_MODE="true"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [--global|--project|--check]"
            echo ""
            echo "Options:"
            echo "  --global, -g   Install hooks to ~/.claude/settings.json (default)"
            echo "  --project, -p  Install hooks to <project>/.claude/settings.json"
            echo "  --check, -c    Check if hooks are in sync (exit 0=sync, 1=desync)"
            echo "  --help, -h     Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $arg${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Find project root (look for .git directory)
find_project_root() {
    local dir="$PWD"
    while [[ "$dir" != "/" ]]; do
        if [[ -d "$dir/.git" ]]; then
            echo "$dir"
            return 0
        fi
        dir="$(dirname "$dir")"
    done
    return 1
}

# Determine settings file path based on mode
if [[ "$INSTALL_MODE" == "project" ]]; then
    PROJECT_ROOT=$(find_project_root) || {
        echo -e "${RED}Error: Not in a git repository${NC}"
        echo "Run with --project from within a git project, or use --global"
        exit 1
    }
    SETTINGS_DIR="$PROJECT_ROOT/.claude"
    SETTINGS_FILE="$SETTINGS_DIR/settings.json"
    SCOPE_LABEL="PROJECT: $PROJECT_ROOT"
else
    SETTINGS_DIR="$HOME/.claude"
    SETTINGS_FILE="$SETTINGS_DIR/settings.json"
    SCOPE_LABEL="GLOBAL: ~/.claude/settings.json"
fi

BACKUP_FILE=""
TEMP_FILES=()

# Cleanup/rollback on error
cleanup() {
    local exit_code=$?
    # Clean up any temp files
    for tmp in "${TEMP_FILES[@]}"; do
        rm -f "$tmp" 2>/dev/null
    done
    # Rollback on error
    if [[ $exit_code -ne 0 && -n "$BACKUP_FILE" && -f "$BACKUP_FILE" ]]; then
        echo -e "${RED}Error occurred. Restoring settings from backup...${NC}"
        cp "$BACKUP_FILE" "$SETTINGS_FILE"
        echo -e "${GREEN}Settings restored from: $BACKUP_FILE${NC}"
    fi
    exit $exit_code
}
trap cleanup EXIT

# Enable nullglob to handle empty glob matches safely
shopt -s nullglob

# Quiet mode for check
if [[ "$CHECK_MODE" != "true" ]]; then
    echo -e "${GREEN}rbw-claude-code Hook Setup${NC}"
    echo "================================================"
    echo ""
    echo -e "${BLUE}Scope: ${SCOPE_LABEL}${NC}"
    echo ""
fi

# Detect marketplace path
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MARKETPLACE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Verify we're in the right directory
if [[ ! -f "$MARKETPLACE_ROOT/.claude-plugin/marketplace.json" ]]; then
    echo -e "${RED}Error: Cannot find marketplace.json${NC}"
    echo "Please run this script from the rbw-claude-code repository"
    exit 1
fi

if [[ "$CHECK_MODE" != "true" ]]; then
    echo "Marketplace path: $MARKETPLACE_ROOT"
    echo ""
fi

# Check for jq
if ! command -v jq &> /dev/null; then
    echo -e "${RED}Error: jq is required but not installed${NC}"
    echo "Install with: brew install jq (macOS) or apt install jq (Linux)"
    exit 1
fi

# Create settings directory if it doesn't exist
mkdir -p "$SETTINGS_DIR"

# Initialize settings file if it doesn't exist or is empty
if [[ ! -s "$SETTINGS_FILE" ]]; then
    echo '{}' > "$SETTINGS_FILE"
fi

# Backup existing settings (skip in check mode)
if [[ "$CHECK_MODE" != "true" ]]; then
    BACKUP_FILE="$SETTINGS_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    cp "$SETTINGS_FILE" "$BACKUP_FILE"
    echo -e "${YELLOW}Backed up existing settings to: $BACKUP_FILE${NC}"
    echo ""
fi

# Discover all hooks.json files
[[ "$CHECK_MODE" != "true" ]] && echo -e "${BLUE}Discovering hooks...${NC}"
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

if [[ "$CHECK_MODE" != "true" ]]; then
    echo "Found ${#HOOKS_FILES[@]} hook configuration(s)"
    echo ""
fi

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
    [[ "$CHECK_MODE" != "true" ]] && echo "  - $PLUGIN_NAME"
done

[[ "$CHECK_MODE" != "true" ]] && echo ""

# Aggregate all hooks into a single structure
[[ "$CHECK_MODE" != "true" ]] && echo -e "${BLUE}Aggregating hooks...${NC}"

# Create a temporary file for aggregation
TEMP_FILE=$(mktemp)
TEMP_FILES+=("$TEMP_FILE")

# Write all resolved hooks to temp file (one per line for jq slurp)
for hook in "${RESOLVED_HOOKS[@]}"; do
    echo "$hook" >> "$TEMP_FILE"
done

# Aggregate hooks by event type
AGGREGATED=$(jq -s '
    reduce .[] as $item ({hooks: {SessionStart: [], PreToolUse: [], PostToolUse: []}};
        .hooks.SessionStart += ($item.hooks.SessionStart // []) |
        .hooks.PreToolUse += ($item.hooks.PreToolUse // []) |
        .hooks.PostToolUse += ($item.hooks.PostToolUse // [])
    )
' "$TEMP_FILE") || {
    echo -e "${RED}Error aggregating hooks${NC}"
    exit 1
}

# Validate hook scripts exist and fix permissions (skip detailed output in check mode)
if [[ "$CHECK_MODE" != "true" ]]; then
    echo -e "${BLUE}Validating hook scripts...${NC}"
    ERRORS=0
    FIXED=0

    while IFS= read -r cmd; do
        if [[ -n "$cmd" ]]; then
            # Strip surrounding quotes for file path check (they're there for shell escaping)
            cmd_path="${cmd#\"}"
            cmd_path="${cmd_path%\"}"
            if [[ ! -f "$cmd_path" ]]; then
                echo -e "${RED}Error: Script not found: $cmd_path${NC}"
                ((ERRORS++))
            elif [[ ! -x "$cmd_path" ]]; then
                # Auto-fix non-executable scripts
                if chmod +x "$cmd_path" 2>/dev/null; then
                    echo -e "${YELLOW}Fixed: Made executable: $cmd_path${NC}"
                    ((FIXED++))
                else
                    echo -e "${RED}Error: Cannot make executable: $cmd_path${NC}"
                    ((ERRORS++))
                fi
            fi
        fi
    done < <(echo "$AGGREGATED" | jq -r '.. | .command? // empty')

    if [[ $ERRORS -gt 0 ]]; then
        echo -e "${RED}  $ERRORS error(s) found - some hooks may not work${NC}"
    elif [[ $FIXED -gt 0 ]]; then
        echo -e "${GREEN}  Fixed $FIXED script(s), all validated${NC}"
    else
        echo "  All hook scripts validated"
    fi
    echo ""
fi

# Extract just the hooks object for merging
HOOKS_ONLY=$(echo "$AGGREGATED" | jq '.hooks')

# Check mode: compare current settings to what we would write
if [[ "$CHECK_MODE" == "true" ]]; then
    # Get current hooks from settings (normalized)
    CURRENT_HOOKS=$(jq -c '.hooks // {}' "$SETTINGS_FILE" 2>/dev/null | jq -S '.')
    # Get what we would write (normalized)
    NEW_HOOKS=$(echo "$HOOKS_ONLY" | jq -S '.')

    if [[ "$CURRENT_HOOKS" == "$NEW_HOOKS" ]]; then
        echo "SYNC_OK"
        exit 0
    else
        echo "SYNC_NEEDED"
        echo "Run: ./scripts/setup-hooks.sh $([ "$INSTALL_MODE" == "project" ] && echo "--project" || echo "--global")"
        exit 1
    fi
fi

# Merge hooks into existing settings (preserving other settings)
echo -e "${BLUE}Merging into settings...${NC}"
MERGED=$(jq --argjson hooks "$HOOKS_ONLY" '.hooks = $hooks' "$SETTINGS_FILE") || {
    echo -e "${RED}Error merging hooks into settings${NC}"
    exit 1
}

# Write to temp file first (atomic write)
TEMP_SETTINGS=$(mktemp)
TEMP_FILES+=("$TEMP_SETTINGS")
echo "$MERGED" | jq '.' > "$TEMP_SETTINGS" || {
    echo -e "${RED}Error writing settings${NC}"
    exit 1
}

# Move temp file to settings (atomic)
mv "$TEMP_SETTINGS" "$SETTINGS_FILE"

# Count hooks by type
SESSION_START=$(echo "$AGGREGATED" | jq '[.hooks.SessionStart[] | .hooks | length] | add // 0')
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
echo "  SessionStart:             $SESSION_START hook(s)"
echo "  PreToolUse (Bash):        $PRE_BASH hook(s)"
echo "  PreToolUse (Read):        $PRE_READ hook(s)"
echo "  PostToolUse (Write|Edit): $POST_WRITE_EDIT hook(s)"
echo "  PostToolUse (Write):      $POST_WRITE hook(s)"
echo ""

if [[ "$INSTALL_MODE" == "project" ]]; then
    echo -e "${YELLOW}Note: Project hooks only apply when working in this directory.${NC}"
    echo "For global hooks, run: ./scripts/setup-hooks.sh --global"
    echo ""
fi

echo -e "${YELLOW}Note: This is a workaround for Claude Code issue #16288${NC}"
echo "Plugin hooks should work natively once the bug is fixed."
echo ""
echo "To verify hooks are active, run: /hooks"
echo ""
echo -e "${GREEN}Backup saved at: $BACKUP_FILE${NC}"

# Clear the trap since we succeeded
trap - EXIT
