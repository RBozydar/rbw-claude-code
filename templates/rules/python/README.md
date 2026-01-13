# Python Rules

Modular rules for Python projects. Symlink these to your `.claude/rules/` directory to enforce consistent coding standards.

## Installation

```bash
# Create rules directory if it doesn't exist
mkdir -p ~/.claude/rules

# Symlink all Python rules
ln -s /path/to/rbw-claude-code/templates/rules/python/*.md ~/.claude/rules/

# Or symlink specific rules
ln -s /path/to/rbw-claude-code/templates/rules/python/asyncio.md ~/.claude/rules/
ln -s /path/to/rbw-claude-code/templates/rules/python/typing.md ~/.claude/rules/
```

## Available Rules

| Rule | Focus |
|------|-------|
| `asyncio.md` | Structured concurrency, TaskGroup, fault isolation |
| `typing.md` | Type hints, Protocols, modern syntax |
| `architecture.md` | SOLID principles, dependency injection |
| `testing.md` | TDD, pytest patterns, fixtures |
| `prohibited.md` | Banned practices and anti-patterns |

## Usage

Each rule is designed to be:
- **Self-contained** - Can be used independently
- **Non-overlapping** - Minimal duplication between rules
- **Focused** - One concern per file

## Customization

Copy any rule and modify for your project:

```bash
cp /path/to/rbw-claude-code/templates/rules/python/asyncio.md \
   ~/.claude/rules/my-asyncio.md
```

Then edit `my-asyncio.md` to match your project's needs.
