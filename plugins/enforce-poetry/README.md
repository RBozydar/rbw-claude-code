# enforce-poetry

Block bare python/pip/pytest commands and enforce poetry usage in Claude Code.

## What it does

This PreToolUse hook intercepts Bash commands and blocks:
- `python` / `python3` - suggests `poetry run python`
- `pip install` / `pip3 install` - suggests `poetry add`
- `pytest` - suggests `poetry run pytest`
- `ruff` - suggests `poetry run ruff`

## Installation

```bash
/plugin install enforce-poetry
```

## Why use this?

When working in a poetry-managed Python project, using bare `python` or `pip` commands can:
- Install packages outside the virtual environment
- Use the wrong Python version
- Create reproducibility issues

This hook ensures Claude Code uses poetry for all Python operations.
