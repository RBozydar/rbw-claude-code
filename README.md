# rbw-claude-code

A Claude Code plugin marketplace with Python development and productivity plugins.

## Installation

Add this marketplace to Claude Code:

```bash
/plugin marketplace add RBozydar/rbw-claude-code
```

Then browse and install plugins:

```bash
/plugin menu
```

## Available Plugins

| Plugin | Description |
|--------|-------------|
| [enforce-uv](plugins/enforce-uv) | Block bare python/pip/pytest commands, enforce uv usage |
| [conventional-commits](plugins/conventional-commits) | Validate git commit messages follow conventional format |
| [python-format](plugins/python-format) | Auto-format Python files with ruff after edits |
| [python-typecheck](plugins/python-typecheck) | Run type checking after Python file edits |
| [test-reminder](plugins/test-reminder) | Remind to add tests when creating new Python files |

## Plugin Details

### enforce-uv

Ensures Claude Code uses `uv` for all Python operations. Blocks bare `python`, `pip`, `pytest` commands with suggestions to use `uv run` or `uvx`.

### conventional-commits

Validates commit messages follow the [Conventional Commits](https://www.conventionalcommits.org/) specification. Blocks commits without proper format like `feat:`, `fix:`, `docs:`, etc.

### python-format

Runs `uvx ruff format` automatically after any Python file is written or edited. Non-blocking - shows warnings but allows operation to proceed.

### python-typecheck

Runs `uvx pyright` automatically after any Python file is written or edited. Shows type errors without blocking.

### test-reminder

Gently reminds you to add tests when creating new Python modules. Checks for `test_<module>.py` in common locations.

## Requirements

- Claude Code with plugin support
- `uv` installed for python-format and python-typecheck plugins

## License

MIT
