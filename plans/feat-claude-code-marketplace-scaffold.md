# feat: Claude Code Marketplace Scaffold

## Overview

Transform this repository into a Claude Code plugin marketplace with composable, single-purpose plugins. Start with 5 existing Python hooks, split into focused plugins following Anthropic's pattern.

## Problem Statement

Current state:
- `.claude/hooks/` - 5 Python hooks bundled together
- `.claude/settings.example.json` - Hook configurations
- Hooks depend on `make fmt`/`make typecheck` (not portable)

Issues:
- Not installable via marketplace
- Monolithic - users can't pick individual hooks
- Makefile dependency breaks for users without compatible Makefile

## Proposed Structure

```
rbw-claude-code/
├── .claude-plugin/
│   └── marketplace.json
├── plugins/
│   ├── enforce-uv/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── hooks/enforce_uv.py
│   │   ├── settings.json
│   │   └── README.md
│   ├── conventional-commits/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── hooks/conventional_commits.py
│   │   ├── settings.json
│   │   └── README.md
│   ├── python-format/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── hooks/format_python.py      # Fixed: uses uvx ruff directly
│   │   ├── settings.json
│   │   └── README.md
│   ├── python-typecheck/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── hooks/typecheck.py          # Fixed: uses uvx pyright directly
│   │   ├── settings.json
│   │   └── README.md
│   └── test-reminder/
│       ├── .claude-plugin/plugin.json
│       ├── hooks/test_reminder.py
│       ├── settings.json
│       └── README.md
├── README.md
└── .gitignore
```

## Implementation Tasks

### 1. Create Marketplace Foundation

- [ ] Create `.claude-plugin/marketplace.json`
- [ ] Create `plugins/` directory
- [ ] Update root README.md

### 2. Create Composable Plugins

For each of the 5 plugins:

**enforce-uv** (no changes needed - already self-contained)
- [ ] Create plugin structure
- [ ] Move hook
- [ ] Add plugin.json and settings.json

**conventional-commits** (no changes needed - already self-contained)
- [ ] Create plugin structure
- [ ] Move hook
- [ ] Add plugin.json and settings.json

**python-format** (FIX: remove Makefile dependency)
- [ ] Create plugin structure
- [ ] Rewrite hook to use `uvx ruff format` directly instead of `make fmt`
- [ ] Add plugin.json and settings.json

**python-typecheck** (FIX: remove Makefile dependency)
- [ ] Create plugin structure
- [ ] Rewrite hook to use `uvx pyright` or `uvx mypy` directly instead of `make typecheck`
- [ ] Add plugin.json and settings.json

**test-reminder** (no changes needed - already self-contained)
- [ ] Create plugin structure
- [ ] Move hook
- [ ] Add plugin.json and settings.json

### 3. Cleanup

- [ ] Remove `.claude/hooks/`
- [ ] Remove `.claude/settings.example.json`
- [ ] Validate: `claude plugin validate .`

## Key Files

### marketplace.json

```json
{
  "name": "rbw-claude-code",
  "version": "1.0.0",
  "description": "Python development and productivity plugins for Claude Code",
  "owner": {
    "name": "RBozydar"
  },
  "plugins": [
    {
      "name": "enforce-uv",
      "description": "Block bare python/pip/pytest commands, enforce uv usage",
      "source": "./plugins/enforce-uv",
      "category": "development"
    },
    {
      "name": "conventional-commits",
      "description": "Validate git commit messages follow conventional format",
      "source": "./plugins/conventional-commits",
      "category": "productivity"
    },
    {
      "name": "python-format",
      "description": "Auto-format Python files with ruff after edits",
      "source": "./plugins/python-format",
      "category": "development"
    },
    {
      "name": "python-typecheck",
      "description": "Run type checking after Python file edits",
      "source": "./plugins/python-typecheck",
      "category": "development"
    },
    {
      "name": "test-reminder",
      "description": "Remind to add tests when creating new Python files",
      "source": "./plugins/test-reminder",
      "category": "development"
    }
  ]
}
```

### Example plugin.json (enforce-uv)

```json
{
  "name": "enforce-uv",
  "version": "1.0.0",
  "description": "Block bare python/pip/pytest commands, enforce uv usage"
}
```

### Fixed format_python.py (self-contained)

```python
#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["cchooks"]
# ///
"""PostToolUse hook to auto-format Python files with ruff."""

import subprocess
from cchooks import PostToolUseContext, create_context

c = create_context()
assert isinstance(c, PostToolUseContext)

if c.tool_name in ("Write", "Edit") and c.tool_input.get("file_path", "").endswith(".py"):
    file_path = c.tool_input["file_path"]

    # Use uvx ruff directly - no Makefile dependency
    result = subprocess.run(
        ["uvx", "ruff", "format", file_path],
        check=False, capture_output=True, text=True
    )

    if result.returncode == 0:
        print(f"Formatted: {file_path}")
    else:
        print(f"Format warning: {result.stderr}")

c.output.exit_success()
```

### Fixed typecheck.py (self-contained)

```python
#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["cchooks"]
# ///
"""PostToolUse hook to run type checking after Python file edits."""

import subprocess
from cchooks import PostToolUseContext, create_context

c = create_context()
assert isinstance(c, PostToolUseContext)

if c.tool_name in ("Write", "Edit") and c.tool_input.get("file_path", "").endswith(".py"):
    file_path = c.tool_input["file_path"]

    # Use uvx pyright directly - no Makefile dependency
    result = subprocess.run(
        ["uvx", "pyright", file_path],
        check=False, capture_output=True, text=True
    )

    if result.returncode == 0:
        print("Type check passed")
    else:
        print(f"Type errors:\n{result.stdout}")

c.output.exit_success()
```

## Acceptance Criteria

- [ ] `/plugin marketplace add RBozydar/rbw-claude-code` works
- [ ] All 5 plugins appear in `/plugin menu`
- [ ] Each plugin can be installed independently
- [ ] Hooks work without requiring user's Makefile
- [ ] `claude plugin validate .` passes

## References

- [Official Marketplace Docs](https://code.claude.com/docs/en/plugin-marketplaces)
- [Anthropic Marketplace](https://github.com/anthropics/claude-code/blob/main/.claude-plugin/marketplace.json)
