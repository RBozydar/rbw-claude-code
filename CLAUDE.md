# CLAUDE.md

Instructions for Claude Code when working in this repository.

## Repository Overview

This is a Claude Code plugin marketplace containing AI-powered development
tools and Python workflow plugins.

## Available Plugins

| Plugin | Type | Description |
|--------|------|-------------|
| `core` | agents/commands/skills | Universal AI development tools |
| `python-backend` | agents/commands | Python-specific reviewers and commands |
| `enforce-uv` | hook | Block bare python/pip commands |
| `conventional-commits` | hook | Validate commit message format |
| `python-format` | hook | Auto-format with ruff |
| `python-typecheck` | hook | Type check after edits |
| `test-reminder` | hook | Remind about missing tests |
| `protect-env` | hook | Block reading .env files |
| `git-safety-guard` | hook | Block destructive git commands |
| `safety-guard` | hook | Block destructive file ops & supply chain attacks |
| `gh-api-guard` | hook | Allow only safe gh api commands |
| `gemini-model-guard` | hook | Block Gemini 2.x models, enforce Gemini 3 |

## Structure

```text
.claude-plugin/marketplace.json    # Marketplace registry
plugins/
  core/                            # AI-powered development tools
    agents/
      review/                      # Code review agents
      research/                    # Research agents
      workflow/                    # Workflow agents
    commands/
      workflows/                   # /workflows:plan, /workflows:work, etc.
    skills/                        # compound-docs, git-worktree, etc.
  python-backend/                  # Python-specific tools
    agents/
      review/                      # Python reviewers
      external-llm/                # Gemini agents
    commands/                      # /pytest-runner, /type-check
  <hook-plugin>/                   # Hook-based plugins
    .claude-plugin/plugin.json     # Plugin config with inline hooks
    hooks/                         # Hook scripts
```

## Plugin Types

### Agent Plugins (core, python-backend)

- Agents are markdown files with YAML frontmatter
- Organized by category: `agents/review/`, `agents/research/`, etc.
- Commands are markdown files in `commands/`
- Skills are directories with `SKILL.md` and optional references

### Hook Plugins (enforce-poetry, python-format, etc.)

- Python scripts with PEP 723 inline metadata
- Use `cchooks` library for context
- Hooks defined in `hooks/hooks.json`

## Hook Development Quick Reference

For full details, see the `create-hook` skill.

### Hook Events

| Event | Description |
|-------|-------------|
| `PreToolUse` | Block/validate before tool execution |
| `PostToolUse` | React after tool completes |
| `SessionStart` | Initialize on session start |
| `Stop` | Verify task completion |

### hooks.json Structure

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/hooks/my-hook.py",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

### Key Environment Variables

- `CLAUDE_PLUGIN_ROOT` - Plugin directory (always use for paths)
- `CLAUDE_PROJECT_DIR` - Current project root

### Hook Script Pattern

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

# Check safe patterns first, then blocked patterns
if is_blocked(command):
    c.output.exit_block("Reason for blocking")

c.output.exit_success()
```

## Conventions

### Plugin Naming

- Use kebab-case: `my-plugin-name`
- Be descriptive but concise

### Hook Scripts

```python
#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["cchooks"]
# ///

from cchooks import PreToolUseContext, create_context

c = create_context()
# ... logic ...
c.output.exit_success()  # or c.output.exit_block(message)
```

### Agent Files

```markdown
---
name: agent-name
description: When to use this agent...
---

Agent instructions here...
```

### Command Files

```markdown
---
name: command-name
description: What the command does
argument-hint: "[optional arguments]"
---

Command instructions here...
```

### Skill Directories

```text
skills/<skill-name>/
  SKILL.md           # Main skill file with YAML frontmatter
  references/        # Supporting documentation (optional)
  templates/         # Templates (optional)
  scripts/           # Executable scripts (optional)
```

## Adding a New Plugin

1. Create directory: `plugins/<plugin-name>/`
2. Create `.claude-plugin/plugin.json`:

   ```json
   {
     "name": "<plugin-name>",
     "version": "1.0.0",
     "description": "What it does",
     "hooks": {
       "PreToolUse": [
         {
           "matcher": "Bash",
           "hooks": [
             {
               "type": "command",
               "command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/script.py\"",
               "timeout": 10
             }
           ]
         }
       ]
     }
   }
   ```

3. Add components (hooks, agents, commands, skills)
4. Write `README.md`
5. Add to `.claude-plugin/marketplace.json`
6. Validate: `claude plugin validate .`

## Validation

Always run before committing:

```bash
claude plugin validate .
```

## Commit Format

Use conventional commits:

```text
feat(plugin-name): add new feature
fix(plugin-name): fix bug
docs: update documentation
```
