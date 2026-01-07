# Plan: Create Poetry Variant Branch

## Overview
Create a `poetry-variant` branch where the `enforce-uv` plugin becomes `enforce-poetry`, suggesting poetry commands instead of uv commands for the user's project.

**Key decision:** Hook scripts still use `uv run --script` (PEP 723) for running themselves. Only the *enforcement suggestions* change to poetry. This means users still need uv installed to run hooks, but Claude will suggest poetry commands for their project work.

## Scope Summary

| Category | Changes |
|----------|---------|
| Hook shebangs | **No changes** - keep `uv run --script` |
| python-format/typecheck | **No changes** - keep `uvx ruff/pyright` |
| enforce-uv plugin | **Rename to enforce-poetry** - change suggestions |
| Documentation | Update references to reflect poetry variant |
| Marketplace | Update plugin listing |

## Files Requiring Changes

### 1. Rename enforce-uv → enforce-poetry

**Delete:** `plugins/enforce-uv/` (entire directory)
**Create:** `plugins/enforce-poetry/`

#### `plugins/enforce-poetry/.claude-plugin/plugin.json`
```json
{
  "name": "enforce-poetry",
  "version": "1.0.0",
  "description": "Block bare python/pip/pytest commands, enforce poetry usage",
  "hooks": "./hooks/hooks.json"
}
```

#### `plugins/enforce-poetry/hooks/hooks.json`
- Update script path: `enforce_uv.py` → `enforce_poetry.py`

#### `plugins/enforce-poetry/hooks/enforce_poetry.py`
- Skip commands starting with `poetry ` instead of `uv ` or `uvx `
- Update pattern suggestions:

| Blocked Command | New Suggestion |
|-----------------|----------------|
| `python` | `poetry run python` |
| `python3` | `poetry run python` |
| `pip install` | `poetry add` |
| `pip3 install` | `poetry add` |
| `pytest` | `poetry run pytest` |
| `ruff` | `poetry run ruff` |

#### `plugins/enforce-poetry/README.md`
- Update title, description, and all command examples

### 2. Documentation Updates

| File | Lines | Changes |
|------|-------|---------|
| `README.md` | 33 | `enforce-uv` → `enforce-poetry` in table |
| `README.md` | 103-106 | Update enforce section heading and description |
| `README.md` | 156 | Keep uv requirement (still needed for hooks) |
| `CLAUDE.md` | 16 | Update plugin table entry |
| `.claude-plugin/marketplace.json` | 25-26 | Update plugin name and description |

### 3. Command Documentation

Update these files to show poetry as primary:

| File | Current | Change |
|------|---------|--------|
| `plugins/python-backend/commands/pytest-runner.md:42` | uv first, poetry second | Swap order |
| `plugins/python-backend/commands/type-check.md:41-43` | uv first, poetry second | Swap order |
| `plugins/core/commands/workflows/work.md:133,162,165` | uv examples | Use poetry examples |

## Implementation Steps

1. `git checkout -b poetry-variant` from main
2. Delete `plugins/enforce-uv/` directory
3. Create `plugins/enforce-poetry/` with modified files
4. Update `README.md` references
5. Update `CLAUDE.md` plugin table
6. Update `.claude-plugin/marketplace.json`
7. Update command docs to prefer poetry
8. Commit and push branch
9. Back on main: Update marketplace.json to offer both variants via branch refs

## Main Branch Marketplace Update (After poetry-variant exists)

Add both variants to `.claude-plugin/marketplace.json`:
```json
{
  "name": "enforce-uv",
  "description": "Block bare python/pip/pytest commands, enforce uv usage",
  "source": "./plugins/enforce-uv"
},
{
  "name": "enforce-poetry",
  "description": "Block bare python/pip/pytest commands, enforce poetry usage",
  "source": {
    "source": "github",
    "repo": "RBozydar/rbw-claude-code#poetry-variant"
  }
}
```

## File Count

- **1** plugin directory to rename/recreate (4 files)
- **3** documentation files to update
- **1** marketplace config
- **3** command docs

**Total: 11 files**
