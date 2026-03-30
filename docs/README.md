# Developer Documentation

Guides for creating and contributing plugins to this marketplace.

## Guides

| Guide | Description |
|-------|-------------|
| [Creating Plugins](creating-plugins.md) | How to create a new plugin |
| [Codex Compatibility](codex-compatibility.md) | How this repo maps Claude plugins to Codex plugins |
| [Hooks](hooks.md) | Creating PreToolUse and PostToolUse hooks |
| [Commands](commands.md) | Creating slash commands |

## Quick Reference

### Plugin Structure

```
plugins/my-plugin/
├── .codex-plugin/
│   └── plugin.json      # Required for Codex marketplaces
├── .claude-plugin/
│   └── plugin.json      # Required for Claude Code
├── hooks/               # Hook scripts
├── commands/            # Slash command markdown files
├── skills/              # SKILL.md files
├── .mcp.json            # Optional Codex MCP config
├── settings.json        # Register hooks/commands
└── README.md            # Plugin documentation
```

### Validate Before Commit

```bash
claude plugin validate .
```

### Add to Marketplace

Edit `.claude-plugin/marketplace.json` for Claude Code or `.agents/plugins/marketplace.json` for Codex.

Claude Code example:

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
- [OpenAI Codex Plugin Docs](https://developers.openai.com/codex/plugins)
- [Anthropic Marketplace](https://github.com/anthropics/claude-code)
