# Creating Plugins

Guide to creating new plugins for this marketplace.

## Quick Start

```bash
# Create plugin structure
mkdir -p plugins/my-plugin/.claude-plugin plugins/my-plugin/hooks

# Create plugin.json
cat > plugins/my-plugin/.claude-plugin/plugin.json << 'EOF'
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "What this plugin does"
}
EOF

# Create settings.json (register your hooks/commands)
cat > plugins/my-plugin/settings.json << 'EOF'
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PLUGIN_DIR/hooks/my_hook.py\"",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
EOF

# Create your hook
# (see hooks.md for details)

# Add to marketplace.json
# Edit .claude-plugin/marketplace.json and add your plugin to the plugins array

# Validate
claude plugin validate .
```

## Plugin Components

A plugin can contain any combination of:

| Component | Directory | Purpose |
|-----------|-----------|---------|
| Hooks | `hooks/` | Scripts that run before/after tool use |
| Commands | `commands/` | Slash commands (`/my-command`) |
| Skills | `skills/` | SKILL.md files with specialized knowledge |
| Agents | `agents/` | Custom subagent definitions |

## Required Files

### plugin.json

Minimal required fields:

```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "Brief description"
}
```

Optional fields:

```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "Brief description",
  "author": {
    "name": "Your Name",
    "email": "you@example.com"
  },
  "repository": "https://github.com/you/repo",
  "license": "MIT"
}
```

### settings.json

Registers hooks and commands. See [hooks.md](hooks.md) for hook configuration.

### README.md

Document your plugin:

```markdown
# my-plugin

Brief description.

## What it does

Detailed explanation.

## Installation

\`\`\`bash
/plugin install my-plugin
\`\`\`

## Requirements

- List any dependencies

## Configuration

Explain any configuration options.
```

## Adding to Marketplace

Edit `.claude-plugin/marketplace.json`:

```json
{
  "plugins": [
    // ... existing plugins ...
    {
      "name": "my-plugin",
      "description": "What it does",
      "source": "./plugins/my-plugin",
      "category": "development"
    }
  ]
}
```

Categories: `development`, `productivity`, `security`, `learning`

## Validation

Always validate before committing:

```bash
claude plugin validate .
```

This checks:
- JSON syntax
- Required fields
- Path references
- Hook configurations
