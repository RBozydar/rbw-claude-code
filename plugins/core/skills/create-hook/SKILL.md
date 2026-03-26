---
name: create-hook
description: This skill should be used when building PreToolUse, PostToolUse, SessionStart, or other hook types for Claude Code plugins. It provides patterns, security best practices, and configuration guidance.
---

# Hook Development Guide

Create Claude Code hooks that intercept events in the lifecycle and can validate, modify, or block operations.

## Hook Types

1. **Command Hooks** (recommended) -- Execute a script for deterministic checks
2. **Prompt Hooks** -- Use LLM reasoning for context-aware decisions
3. **Agent Hooks** (v2.1.0+) -- Leverage agent capabilities for complex workflows

## Hook Events

| Event | Trigger | Common Uses |
|-------|---------|-------------|
| `PreToolUse` | Before any tool executes | Block dangerous commands, validate inputs |
| `PostToolUse` | After tool completes | Format code, run linters, log results |
| `SessionStart` | When session begins | Check environment, load config |
| `SessionEnd` | When session ends | Cleanup, save state |
| `Stop` | When agent stops | Verify task completion |
| `SubagentStop` | When subagent stops | Validate subagent work |
| `UserPromptSubmit` | When user sends message | Process user input |
| `PreCompact` | Before context compression | Preserve critical info |
| `Notification` | System notifications | React to events |
| `PermissionRequest` | Permission dialogs (v2.1.0) | Custom permission handling |

## Configuration

### hooks.json Format

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/hooks/check-bash.py",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

**Matchers:** `"Bash"`, `"Edit"`, `"Read"` (case-sensitive tool names), or `"*"` for all.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `CLAUDE_PLUGIN_ROOT` | Plugin directory (always use for portable paths) |
| `CLAUDE_PROJECT_DIR` | Current project root |
| `CLAUDE_ENV_FILE` | Persist variables from SessionStart |

## Writing Command Hooks

Copy and customize a template from `templates/`:

| Template | Purpose |
|----------|---------|
| `templates/pretooluse-bash.py` | PreToolUse hook for Bash commands |
| `templates/pretooluse-read.py` | PreToolUse hook for file reads |
| `templates/posttooluse-edit.py` | PostToolUse hook for formatting |
| `templates/sessionstart.sh` | SessionStart initialization |

```bash
cp ${CLAUDE_PLUGIN_ROOT}/skills/create-hook/templates/pretooluse-bash.py \
   plugins/my-hook/hooks/my-hook.py
chmod +x plugins/my-hook/hooks/my-hook.py
```

### Essential Patterns

**Always check safe patterns before blocking (allowlist-first):**

```python
SAFE_PATTERNS = [r"rm\s+-rf\s+/tmp/"]
BLOCKED_PATTERNS = [(r"rm\s+-rf\s+", "rm -rf is destructive")]

for pattern in SAFE_PATTERNS:
    if re.search(pattern, command):
        c.output.exit_success()

for pattern, reason in BLOCKED_PATTERNS:
    if re.search(pattern, command):
        c.output.exit_block(reason)
```

**Exit methods:**
- `c.output.exit_success()` -- allow operation
- `c.output.exit_block("reason")` -- block with message
- `c.output.exit_modify({"command": modified})` -- modify input (PreToolUse only)

**Early exit when hook doesn't apply:**
```python
if c.tool_name != "Bash":
    c.output.exit_success()
```

## Creating a New Hook Plugin

1. Create directory structure:
   ```bash
   mkdir -p plugins/my-hook/.claude-plugin plugins/my-hook/hooks
   ```

2. Create `plugins/my-hook/.claude-plugin/plugin.json`:
   ```json
   {"name": "my-hook", "version": "1.0.0", "description": "What this hook does"}
   ```

3. Create `plugins/my-hook/hooks/hooks.json` with event matchers (see Configuration above)

4. Copy and customize a template from this skill's `templates/` directory

5. Validate: `claude plugin validate .`

## Debugging

Test hooks directly by piping JSON input:

```bash
echo '{"tool_name": "Bash", "tool_input": {"command": "rm -rf /"}}' | \
  python plugins/my-hook/hooks/my-hook.py
```

Validate hooks.json: `cat plugins/my-hook/hooks/hooks.json | jq .`

## Reference Examples

Existing hooks in this repository:
- Block destructive commands: `plugins/guards/security/safety-guard/`
- Enforce commit format: `plugins/guards/policy/conventional-commits/`
- Format on save: `plugins/guards/quality/python-format/`
- Protect sensitive files: `plugins/guards/security/protect-env/`
