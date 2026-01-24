# CLAUDE.md Format

## Overview

CLAUDE.md is Claude Code's project instruction file. It automatically loads into context when starting a conversation in a directory containing this file.

## Key Differences from AGENTS.md

| Aspect | CLAUDE.md | AGENTS.md |
|--------|-----------|-----------|
| Tool | Claude Code only | Multi-tool standard |
| Format | Markdown | Markdown |
| YAML frontmatter | Not used | Optional |
| Auto-load | Yes | Depends on tool |
| Nesting | Supported | Supported |

## File Location

- Root: `CLAUDE.md` or `.claude/CLAUDE.md`
- Can be nested in subdirectories
- Closest file to working directory takes precedence

## Recommended Structure

```markdown
# Project Name

One-sentence description of what this project does.

## Build Commands

```bash
npm install
npm run build
npm test
```

## Code Conventions

For detailed conventions, see docs/CONVENTIONS.md

## Architecture

Brief high-level description. Let agent discover specifics.
```

## What Works Well

**Project context:**
- Repository purpose (what problem it solves)
- Technology stack summary
- Developer environment notes (pyenv, nvm, etc.)

**Process guidance:**
- Branch naming conventions
- Merge vs rebase preferences
- Testing expectations

**Unexpected behaviors:**
- Known quirks the agent should know
- Project-specific warnings

## What to Avoid

**Don't include:**
- Detailed file structure (stale quickly)
- Comprehensive style guides (move to separate files)
- Every possible coding rule (instruction budget)
- Auto-generated content (bloated)

## Progressive Disclosure Pattern

```markdown
## TypeScript

For TypeScript conventions, see docs/TYPESCRIPT.md

## Testing

For testing patterns, see docs/TESTING.md
```

Agent loads these only when working on relevant tasks.

## Monorepo Pattern

**Root CLAUDE.md:**
```markdown
# Monorepo Name

Brief description.

## Navigation

Use `ls packages/` to see available packages.
Each package has its own CLAUDE.md.

## Shared Tools

- Package manager: pnpm
- Run tests: pnpm test
```

**Package CLAUDE.md:**
```markdown
# Package Name

This package handles [specific responsibility].

## Local Commands

pnpm dev
pnpm test
```

## Integration with Skills

Claude Code skills can reference CLAUDE.md for project context. Skills provide specialized workflows while CLAUDE.md provides project grounding.

## Sources

- [Claude Code Documentation](https://code.claude.com/docs/en/skills)
- [Anthropic Engineering Blog](https://www.anthropic.com/engineering/claude-code-best-practices)
