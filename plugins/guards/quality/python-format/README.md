# python-format

Auto-format Python files with ruff after Claude Code edits them.

## What it does

This PostToolUse hook runs `uvx ruff format` on any Python file after it's written or edited.

## Installation

```bash
/plugin install python-format
```

## Requirements

- `uv` must be installed and available in PATH
- No other configuration needed - ruff is run via uvx

## Behavior

After any Write or Edit operation on a `.py` file:
1. Runs `uvx ruff format <file>`
2. Reports success or any formatting warnings
3. Always allows the operation to proceed (non-blocking)
