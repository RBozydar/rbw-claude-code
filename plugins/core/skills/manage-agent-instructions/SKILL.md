---
name: manage-agent-instructions
description: This skill manages CLAUDE.md and AGENTS.md files that configure AI coding agent behavior. Use when creating, auditing, refactoring, or syncing agent instruction files.
---

<essential_principles>
## Core Principles

These principles apply to ALL agent instruction files (CLAUDE.md, AGENTS.md).

### 1. Minimal Root File

The root instruction file should be as small as possible. Every token loads on every request regardless of relevance.

**Absolute minimum content:**
- One-sentence project description (acts as role prompt)
- Package manager (if not npm)
- Non-standard build/test commands

Everything else belongs in progressive disclosure files.

### 2. Progressive Disclosure

Agents navigate documentation hierarchies efficiently. Structure knowledge in layers:

```
Level 1: Root file (~100-300 words)
Level 2: docs/CONVENTIONS.md, docs/TYPESCRIPT.md, etc.
Level 3: Nested references within those files
```

Load context only when needed for the current task.

### 3. Describe Capabilities, Not Paths

File paths change constantly. Documentation that says "auth logic lives in src/auth/handlers.ts" becomes stale and poisons context.

Instead: "Authentication is handled by the AuthService module" and let the agent discover current paths.

Domain concepts (organization vs workspace vs group) are more stable than file paths.

### 4. No Instruction Bloat

Avoid the feedback loop:
1. Agent does something wrong
2. Add rule to prevent it
3. Repeat hundreds of times
4. File becomes unmaintainable "ball of mud"

Curate ruthlessly. Remove:
- Redundant instructions (agent already knows)
- Vague guidance ("write clean code")
- Contradicting rules
- Auto-generated boilerplate

### 5. Tool-Specific Files

Claude Code uses CLAUDE.md, not AGENTS.md. For multi-tool support:

```bash
# Option A: Symlink (both tools read same content)
ln -s AGENTS.md CLAUDE.md

# Option B: Redirect (AGENTS.md points to CLAUDE.md)
# AGENTS.md content: "See CLAUDE.md for instructions"
```

### 6. Monorepo Strategy

Nested instruction files merge with root level:

| Level | Content |
|-------|---------|
| Root | Monorepo purpose, navigation, shared tools |
| Package | Package purpose, specific stack, local conventions |

Keep each level focused on its scope. Don't duplicate.
</essential_principles>

<intake>
What would you like to do?

1. Create new instruction file
2. Audit existing file
3. Refactor bloated file
4. Sync CLAUDE.md/AGENTS.md
5. Add nested package instructions

**Wait for response before proceeding.**
</intake>

<routing>
| Response | Workflow |
|----------|----------|
| 1, "create", "new", "initialize" | `workflows/create-instructions.md` |
| 2, "audit", "review", "check" | `workflows/audit-instructions.md` |
| 3, "refactor", "shrink", "fix", "clean" | `workflows/refactor-instructions.md` |
| 4, "sync", "symlink", "both" | `workflows/sync-files.md` |
| 5, "nested", "package", "monorepo" | `workflows/nested-instructions.md` |

**After reading the workflow, follow it exactly.**
</routing>

<quick_reference>
## File Format Quick Reference

**YAML frontmatter (optional for AGENTS.md, not used by CLAUDE.md):**
```yaml
---
project: "Project name"
package_manager: "pnpm"
---
```

**Recommended sections:**
```markdown
# Project Name

One-sentence description.

## Build Commands

npm run build
npm test

## Code Conventions

See docs/CONVENTIONS.md
```

**Progressive disclosure pattern:**
```markdown
## TypeScript

For TypeScript conventions, see docs/TYPESCRIPT.md
```

**Monorepo root:**
```markdown
# Monorepo Name

Brief description. Navigate with `ls packages/` to see available packages.

Each package has its own CLAUDE.md with specific instructions.
```
</quick_reference>

<reference_index>
## Domain Knowledge

All in `references/`:

- [agents-md-standard.md](./references/agents-md-standard.md) - AGENTS.md open standard details
- [claude-md-format.md](./references/claude-md-format.md) - Claude Code specific CLAUDE.md format
- [progressive-disclosure.md](./references/progressive-disclosure.md) - Structuring knowledge hierarchies
- [common-problems.md](./references/common-problems.md) - Anti-patterns and how to fix them
</reference_index>

<workflows_index>
## Workflows

All in `workflows/`:

| Workflow | Purpose |
|----------|---------|
| create-instructions.md | Create new CLAUDE.md or AGENTS.md from scratch |
| audit-instructions.md | Analyze existing file for problems |
| refactor-instructions.md | Fix bloated/problematic instruction files |
| sync-files.md | Keep CLAUDE.md and AGENTS.md in sync |
| nested-instructions.md | Add package-level instructions in monorepos |
</workflows_index>

<success_criteria>
A well-managed instruction file:
- Root file under 500 words
- Uses progressive disclosure for detailed content
- Describes capabilities, not file paths
- Has no contradicting instructions
- Loads only relevant context per task
- Works across intended tools (Claude Code, Cursor, etc.)
</success_criteria>
