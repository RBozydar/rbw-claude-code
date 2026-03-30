# Codex Compatibility

This repository now ships a parallel Codex marketplace alongside the existing Claude Code marketplace.

## What Codex requires

Codex loads repo marketplaces from `.agents/plugins/marketplace.json` and expects each installable plugin to provide a manifest at `.codex-plugin/plugin.json`.

Current Codex plugin docs describe these plugin surfaces:

- `skills/`
- `.mcp.json`
- `.app.json`

That means this repository can expose skill-bearing plugins to Codex today, but the hook-only guard plugins remain Claude-specific until Codex exposes equivalent plugin components or those behaviors are repackaged behind skills or MCP servers.

## What this repo now exposes to Codex

The repo marketplace at `.agents/plugins/marketplace.json` currently includes:

- `core`
- `python-backend`
- `deep-research-plus`

These plugins now ship `.codex-plugin/plugin.json` manifests, and the plugins that need MCP setup also ship `.mcp.json`.

## Avoiding drift

Do not hand-maintain a second Codex copy of the instruction tree.

The repo now supports a generated Codex workflow from the canonical Claude plugin source:

```bash
convert plugins/core --to codex -o /path/to/project
```

That Codex target:

- copies existing `skills/` into `.codex/skills/` with Codex-specific syntax rewrites
- generates Codex skills from Claude `agents/`
- generates Codex prompts plus backing skills from Claude `commands/`
- writes MCP configuration into `.codex/config.toml`

This keeps the source of truth in the Claude plugin markdown and emits Codex artifacts mechanically.

## What stays Claude-only for now

These plugins are not listed in the Codex marketplace because they are primarily hook plugins:

- `enforce-uv`
- `conventional-commits`
- `gemini-model-guard`
- `python-format`
- `python-typecheck`
- `test-reminder`
- `clean-code-guard`
- `safety-guard`
- `git-safety-guard`
- `gh-api-guard`
- `protect-env`

They still work through the Claude marketplace and `.claude-plugin` manifests.

## Maintaining dual compatibility

When adding a new plugin that should work in both ecosystems:

1. Keep the Claude manifest at `.claude-plugin/plugin.json`.
2. Add a Codex manifest at `.codex-plugin/plugin.json`.
3. Add the plugin to `.agents/plugins/marketplace.json` only if it has meaningful Codex-native surfaces such as `skills`, `apps`, or `mcpServers`.
4. Keep Codex paths relative to the plugin root and start them with `./`.
5. If the plugin is hook-only, leave it Claude-only until there is a real Codex equivalent.
