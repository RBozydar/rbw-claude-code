# python-typecheck

Run type checking with pyright after Claude Code edits Python files.

## What it does

This PostToolUse hook runs `uvx pyright` on any Python file after it's written or edited.

## Installation

```bash
/plugin install python-typecheck
```

## Requirements

- `uv` must be installed and available in PATH
- No other configuration needed - pyright is run via uvx

## Behavior

After any Write or Edit operation on a `.py` file:
1. Runs `uvx pyright <file>`
2. Reports type check results
3. Shows any type errors found
4. Always allows the operation to proceed (non-blocking)

## Note

For large projects, consider configuring pyright with a `pyrightconfig.json` to customize type checking behavior.
