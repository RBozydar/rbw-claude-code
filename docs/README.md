# Developer Documentation

Guides for creating and contributing plugins to this marketplace.

## Guides

| Guide | Description |
|-------|-------------|
| [Creating Plugins](creating-plugins.md) | How to create a new plugin |
| [Hooks](hooks.md) | Creating PreToolUse and PostToolUse hooks |
| [Commands](commands.md) | Creating slash commands |

## Quick Reference

### Plugin Structure

```
plugins/my-plugin/
├── .claude-plugin/
│   └── plugin.json      # Required: name, version, description
├── hooks/               # Hook scripts
├── commands/            # Slash command markdown files
├── skills/              # SKILL.md files
├── settings.json        # Register hooks/commands
└── README.md            # Plugin documentation
```

### Validate Before Commit

```bash
claude plugin validate .
```

### Add to Marketplace

Edit `.claude-plugin/marketplace.json`:

```json
{
  "plugins": [
    {
      "name": "my-plugin",
      "description": "What it does",
      "source": "./plugins/my-plugin",
      "category": "development"
    }
  ]
}
```

## External Resources

- [Official Claude Code Plugin Docs](https://code.claude.com/docs/en/plugin-marketplaces)
- [Anthropic Marketplace](https://github.com/anthropics/claude-code)
