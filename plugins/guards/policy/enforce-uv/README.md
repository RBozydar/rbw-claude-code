# enforce-uv

Block bare python/pip/pytest commands and enforce uv usage in Claude Code.

## What it does

This PreToolUse hook intercepts Bash commands and blocks:
- `python` / `python3` - suggests `uv run python`
- `pip install` / `pip3 install` - suggests `uv add`
- `pytest` - suggests `uv run pytest`
- `ruff` - suggests `uvx ruff`

## Installation

```bash
/plugin install enforce-uv
```

## Why use this?

When working in a uv-managed Python project, using bare `python` or `pip` commands can:
- Install packages outside the virtual environment
- Use the wrong Python version
- Create reproducibility issues

This hook ensures Claude Code uses uv for all Python operations.
