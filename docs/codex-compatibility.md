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
- `linux-hyprland`

These plugins now ship `.codex-plugin/plugin.json` manifests, and the plugins that need MCP setup also ship `.mcp.json`.

For subagents specifically, the repo also generates project-scoped Codex custom
agents under `.codex/agents/` from the Claude agent markdown. Those files are
generated artifacts, not hand-maintained copies.

For Claude slash commands specifically, the repo also generates project-scoped
Codex custom prompts under `.codex/prompts/` from the Claude command markdown.
Those prompts are invocable as `/prompts:<name>` in Codex, for example
`/prompts:workflows-review`.

Regenerate both with:

```bash
uv run python scripts/generate_codex_agents.py
```

Install them into your Codex home with:

```bash
./scripts/install-codex-agents.sh
```

This installs generated agents into `~/.codex/agents/` and generated prompts
into `~/.codex/prompts/`.

## Avoiding drift

Do not hand-maintain a second Codex copy of the instruction tree.

The repo now supports a generated Codex workflow from the canonical Claude plugin source:

```bash
uv run python scripts/generate_codex_agents.py
```

That Codex workflow:

- generates `.codex/agents/*.toml` from Claude `agents/`
- generates `.codex/prompts/*.md` from Claude `commands/`
- enforces collision checks and blocks reserved built-in Codex agent names
- rewrites common Claude `Task(...)` / `AskUserQuestion` patterns into Codex agent phrasing
- rewrites known Claude slash-command references like `/workflows:review` into Codex prompt references like `/prompts:workflows-review`
- carries plugin-level MCP configuration into generated agent files when present

Install the generated Codex artifacts with:

```bash
./scripts/install-codex-agents.sh
```

This keeps the source of truth in the Claude markdown and emits Codex artifacts mechanically.

## Prompt caveat

OpenAI's Codex docs currently describe custom prompts as deprecated and
recommend skills for reusable prompts instead. This repository still generates
custom prompts because they remain the closest Codex-native equivalent to
Claude's explicit slash-command entrypoints.

For long-term shared workflow packaging, Codex skills remain the more stable
surface. For command-like explicit invocation parity, custom prompts are still
useful today.

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
