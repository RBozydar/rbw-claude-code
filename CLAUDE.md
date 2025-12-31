# CLAUDE.md

Instructions for Claude Code when working in this repository.

## Repository Overview

This is a Claude Code plugin marketplace containing composable plugins for Python development workflows.

## Structure

```
.claude-plugin/marketplace.json    # Marketplace registry
plugins/
  <plugin-name>/
    .claude-plugin/plugin.json     # Plugin metadata
    hooks/                         # Hook scripts
    commands/                      # Slash commands (optional)
    skills/                        # Skills (optional)
    agents/                        # Subagents (optional)
    settings.json                  # Hook/command registrations
    README.md                      # Plugin documentation
```

## Conventions

### Plugin Naming
- Use kebab-case: `my-plugin-name`
- Be descriptive but concise
- Prefix with language/tool when specific: `python-format`, `rails-routes`

### Hook Scripts
- Use `#!/usr/bin/env -S uv run --script` shebang
- Include dependencies in PEP 723 inline metadata
- Always use `cchooks` library for context
- Exit with `c.output.exit_success()` or `c.output.exit_block(message)`

### Settings.json
- Use `$CLAUDE_PLUGIN_DIR` for paths (resolves to plugin directory)
- Set reasonable timeouts (10-120 seconds)
- Use specific matchers: `Bash`, `Write|Edit`, etc.

### Documentation
- Each plugin needs a README.md
- Include: what it does, installation, requirements, behavior

## Adding a New Plugin

1. Create directory: `plugins/<plugin-name>/`
2. Create `.claude-plugin/plugin.json`:
   ```json
   {
     "name": "<plugin-name>",
     "version": "1.0.0",
     "description": "What it does"
   }
   ```
3. Add hooks/commands/skills as needed
4. Create `settings.json` to register components
5. Write `README.md`
6. Add to `.claude-plugin/marketplace.json` plugins array
7. Validate: `claude plugin validate .`

## Validation

Always run before committing:
```bash
claude plugin validate .
```

## Commit Format

Use conventional commits:
```
feat(plugin-name): add new feature
fix(plugin-name): fix bug
docs: update documentation
```
