---
name: file-suggestion
description: This skill should be used when setting up fast file suggestions for Claude Code using ripgrep, jq, and fzf, or when improving file autocomplete performance or adding custom file suggestion behavior.
---

# File Suggestion Setup

Configure Claude Code's file suggestion feature with a custom script using ripgrep, jq, and fzf for fast fuzzy file matching.

## Prerequisites

Required tools: `ripgrep` (rg), `jq`, `fzf`. Install via the system package manager if not present.

## Setup

### 1. Install the script

A ready-to-use script is available at:

```
${CLAUDE_PLUGIN_ROOT}/skills/file-suggestion/scripts/file-suggestion.sh
```

Copy to the Claude config directory:

```bash
cp ${CLAUDE_PLUGIN_ROOT}/skills/file-suggestion/scripts/file-suggestion.sh ~/.claude/file-suggestion.sh
chmod +x ~/.claude/file-suggestion.sh
```

### 2. Configure Claude Code

Add to `~/.claude/settings.json`:

```json
{
  "fileSuggestion": {
    "type": "command",
    "command": "~/.claude/file-suggestion.sh"
  }
}
```

## Customization

### Include Gitignored Paths

Uncomment and customize the additional paths section in the script:

```bash
# Include .notes directory even if gitignored
[ -e .notes ] && rg --files --follow --hidden --no-ignore-vcs .notes 2>/dev/null
```

### Exclude Patterns

Add ripgrep glob patterns to exclude files:

```bash
rg --files --follow --hidden \
   --glob '!*.min.js' \
   --glob '!*.map' \
   --glob '!node_modules' \
   . 2>/dev/null
```

### Change Result Limit

Modify `head -15` in the script to return more or fewer results.
