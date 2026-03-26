---
name: manage-agent-instructions
description: This skill should be used when creating, auditing, refactoring, or syncing CLAUDE.md and AGENTS.md files that configure AI coding agent behavior.
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

Structure knowledge in layers:

```
Level 1: Root file (~100-300 words)
Level 2: docs/CONVENTIONS.md, docs/TYPESCRIPT.md, etc.
Level 3: Nested references within those files
```

Load context only when needed for the current task.

### 3. Describe Capabilities, Not Paths

File paths change constantly. Instead of "auth logic lives in src/auth/handlers.ts", write "Authentication is handled by the AuthService module" and let the agent discover current paths.

### 4. No Instruction Bloat

Curate ruthlessly. Remove redundant instructions (agent already knows), vague guidance ("write clean code"), contradicting rules, and auto-generated boilerplate.

### 5. Tool-Specific Files

Claude Code uses CLAUDE.md, not AGENTS.md. For multi-tool support, symlink or redirect between them.

### 6. Monorepo Strategy

| Level | Content |
|-------|---------|
| Root | Monorepo purpose, navigation, shared tools |
| Package | Package purpose, specific stack, local conventions |

Keep each level focused on its scope. Avoid duplication.

</essential_principles>

<intake>

What needs to be done?

1. Create new instruction file
2. Audit existing file
3. Refactor bloated file
4. Sync CLAUDE.md/AGENTS.md
5. Add nested package instructions

Wait for response before proceeding.

</intake>

<routing>

| Response | Workflow |
|----------|----------|
| 1, "create", "new" | `workflows/create-instructions.md` |
| 2, "audit", "review" | `workflows/audit-instructions.md` |
| 3, "refactor", "shrink", "clean" | `workflows/refactor-instructions.md` |
| 4, "sync", "symlink" | `workflows/sync-files.md` |
| 5, "nested", "package", "monorepo" | `workflows/nested-instructions.md` |

After reading the workflow, follow it exactly.

</routing>

<templates_index>

## Templates

Ready-to-use templates in `templates/`:

| Template | Use Case |
|----------|----------|
| [minimal-claude-md.md](./templates/minimal-claude-md.md) | Standard project CLAUDE.md |
| [package-claude-md.md](./templates/package-claude-md.md) | Package-level instructions in a monorepo |
| [monorepo-root.md](./templates/monorepo-root.md) | Root-level monorepo instructions |

</templates_index>

<reference_index>

## References

All in `references/`:

- [agents-md-standard.md](./references/agents-md-standard.md) -- AGENTS.md open standard details
- [claude-md-format.md](./references/claude-md-format.md) -- Claude Code specific CLAUDE.md format
- [progressive-disclosure.md](./references/progressive-disclosure.md) -- structuring knowledge hierarchies
- [common-problems.md](./references/common-problems.md) -- anti-patterns and how to fix them

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

</success_criteria>
