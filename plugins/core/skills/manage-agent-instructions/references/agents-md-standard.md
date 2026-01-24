# AGENTS.md Open Standard

## Overview

AGENTS.md is an open format for guiding AI coding agents, created through collaboration between OpenAI, Google, and other major players. Stewarded by the Agentic AI Foundation under the Linux Foundation.

## Design Philosophy

**Radical simplicity:**
- Single file
- Plain markdown
- Optional metadata
- Human-first
- Tool-agnostic

No directory structure requirements, no special syntax, no custom extensions - just markdown.

## File Location

- Place at repository root
- Nested files in subprojects take precedence (closest file wins)
- Used by 60,000+ open-source projects

## Tool Support

| Tool | Native Support | Notes |
|------|----------------|-------|
| Codex (OpenAI) | Yes | Original creator |
| Jules | Yes | Full support |
| Cursor | Partial | Uses .cursor/rules/ primarily |
| VS Code Copilot | Yes | Via .github/copilot-instructions.md fallback |
| Claude Code | **No** | Uses CLAUDE.md instead |

## Recommended Content

**Keep minimal. Absolute essentials:**

1. One-sentence project description
2. Package manager (if not npm)
3. Non-standard build commands

**Everything else goes in progressive disclosure files.**

## Hierarchical Structure

Place AGENTS.md in each package:

```
repo/
├── AGENTS.md              # Root: monorepo purpose, shared tools
├── packages/
│   ├── api/
│   │   └── AGENTS.md      # Package: API-specific conventions
│   └── web/
│       └── AGENTS.md      # Package: Web-specific conventions
```

Agents read the nearest file in the directory tree. The closest one takes precedence.

## Precedence Rules

1. Explicit user prompts override everything
2. Closest AGENTS.md to edited files takes priority
3. Root AGENTS.md provides defaults

## What NOT to Include

- File paths (change too frequently)
- Auto-generated content (bloated and generic)
- Redundant instructions (agent already knows)
- Vague guidance ("write clean code")

## Cross-Tool Compatibility

To support both AGENTS.md and CLAUDE.md:

```bash
# Option 1: Symlink
ln -s AGENTS.md CLAUDE.md

# Option 2: Primary + redirect
# AGENTS.md points to CLAUDE.md:
# "For AI coding instructions, see CLAUDE.md"
```

## Sources

- [agents.md](https://agents.md/) - Official specification
- [AI Hero Guide](https://www.aihero.dev/a-complete-guide-to-agents-md) - Best practices
- [PRPM Deep Dive](https://prpm.dev/blog/agents-md-deep-dive) - Technical details
