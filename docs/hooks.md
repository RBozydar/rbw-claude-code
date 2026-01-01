# Creating Hooks

Hooks are scripts that run before or after Claude Code uses a tool.

## Hook Types

| Type | When it runs | Use case |
|------|--------------|----------|
| `PreToolUse` | Before tool execution | Validate, block, or modify |
| `PostToolUse` | After tool execution | Format, lint, notify |

## Hook Script Template

```python
#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["cchooks"]
# ///
"""Description of what this hook does."""

from cchooks import PreToolUseContext, create_context  # or PostToolUseContext


c = create_context()
assert isinstance(c, PreToolUseContext)  # or PostToolUseContext

# Your logic here
# Access tool info via:
#   c.tool_name - name of the tool (Bash, Write, Edit, etc.)
#   c.tool_input - dict of tool parameters

# Exit options:
c.output.exit_success()           # Allow operation to proceed
c.output.exit_block("reason")     # Block operation with message (PreToolUse only)
```

## Registering Hooks

In your plugin's `settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PLUGIN_DIR/hooks/my_hook.py\"",
            "timeout": 30
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
            "command": "\"$CLAUDE_PLUGIN_DIR/hooks/format.py\"",
            "timeout": 60
          }
        ]
      }
    ]
  }
}
```

## Matcher Patterns

| Pattern | Matches |
|---------|---------|
| `Bash` | Bash tool only |
| `Write` | Write tool only |
| `Write\|Edit` | Write OR Edit |
| `*` | All tools |

## Context Properties

### PreToolUseContext

```python
c.tool_name      # str: "Bash", "Write", "Edit", etc.
c.tool_input     # dict: tool parameters
```

For Bash:
```python
c.tool_input.get("command", "")  # The bash command
```

For Write/Edit:
```python
c.tool_input.get("file_path", "")  # Path being written/edited
```

### PostToolUseContext

Same as PreToolUseContext, plus:
```python
c.tool_output    # str: output from the tool (if any)
```

## Examples

### Block dangerous commands (PreToolUse)

```python
#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["cchooks"]
# ///

from cchooks import PreToolUseContext, create_context

c = create_context()
assert isinstance(c, PreToolUseContext)

if c.tool_name != "Bash":
    c.output.exit_success()

command = c.tool_input.get("command", "")

if "rm -rf /" in command:
    c.output.exit_block("Blocked: dangerous command")

c.output.exit_success()
```

### Auto-format after edit (PostToolUse)

```python
#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["cchooks"]
# ///

import subprocess
from cchooks import PostToolUseContext, create_context

c = create_context()
assert isinstance(c, PostToolUseContext)

if c.tool_name not in ("Write", "Edit"):
    c.output.exit_success()

file_path = c.tool_input.get("file_path", "")

if file_path.endswith(".py"):
    subprocess.run(["uvx", "ruff", "format", file_path], check=False)
    print(f"Formatted: {file_path}")

c.output.exit_success()
```

## Best Practices

1. **Be specific with matchers** - Don't use `*` unless necessary
2. **Set reasonable timeouts** - 10-30s for quick checks, 60-120s for linting
3. **Always exit** - Call `exit_success()` or `exit_block()`
4. **Non-blocking by default** - PostToolUse hooks should warn, not fail
5. **Use uvx for tools** - No local installation required
