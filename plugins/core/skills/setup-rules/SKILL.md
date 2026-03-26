---
name: setup-rules
description: This skill should be used when setting up Claude Code rules in a project by symlinking from rbw-claude-code templates, such as adding Python coding standards, anti-slop rules, or other shared rules.
---

# Setup Rules

Set up Claude Code rules in a project by creating symlinks to shared rule templates, maintaining consistent coding standards across multiple projects.

## Available Rule Sets

### Python Rules

| Rule | Description |
|------|-------------|
| `asyncio.md` | Structured concurrency, TaskGroup, fault isolation |
| `typing.md` | Modern type hints, Protocols, TypeVar |
| `architecture.md` | SOLID principles, dependency injection |
| `testing.md` | TDD, pytest patterns, fixtures |
| `prohibited.md` | Banned practices checklist |

### General Rules

| Rule | Description |
|------|-------------|
| `anti-slop.md` | Prevent AI-generated code slop |

## Setup

### Primary Method: Setup Script

```bash
bash ${CLAUDE_PLUGIN_ROOT}/skills/setup-rules/scripts/setup-rules.sh
```

The script interactively guides through selecting which rules to install.

### Manual Fallback

To link rules manually:

```bash
mkdir -p .claude/rules
RBW_CLAUDE_CODE="${HOME}/.claude/plugins/marketplaces/rbw-claude-code"

# All Python rules
for rule in asyncio typing architecture testing prohibited; do
  ln -sf "${RBW_CLAUDE_CODE}/templates/rules/python/${rule}.md" .claude/rules/
done

# Anti-slop
ln -sf "${RBW_CLAUDE_CODE}/templates/rules/anti-slop.md" .claude/rules/
```

To copy instead of symlink (for per-project customization), use `cp` instead of `ln -sf`.

## Overriding a Rule

To customize a specific rule while keeping others symlinked:

```bash
rm .claude/rules/asyncio.md
cp "${RBW_CLAUDE_CODE}/templates/rules/python/asyncio.md" .claude/rules/
# Edit .claude/rules/asyncio.md as needed
```

Symlinked rules automatically receive updates when rbw-claude-code is pulled. Copied rules require manual updates.
