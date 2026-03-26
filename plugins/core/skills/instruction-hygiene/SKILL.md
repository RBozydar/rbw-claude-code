---
name: instruction-hygiene
description: Audit and trim Claude Code instruction setups that have grown bloated over time. Use when outputs feel worse, rules have accreted across CLAUDE.md/skills/context files, or you want a recurring setup hygiene check.
---

<essential_principles>
## Core Principles

### 1. Audit the whole setup, not just one file
Instruction rot rarely lives only in `CLAUDE.md`. Check all active instruction sources you can access:
- root `CLAUDE.md`
- nested `CLAUDE.md` files
- skill files
- context or docs folders used as prompt scaffolding
- any extra instruction files loaded by workflow

### 2. Score every rule against the same five filters
For each instruction, ask:
1. Is this something Claude already does by default?
2. Does this contradict another rule elsewhere?
3. Does this duplicate something already covered?
4. Does it look like a bandaid for one bad output?
5. Is it vague enough that it could be interpreted differently every time?

Rules that fail any filter are candidates for removal or rewrite.

### 3. Prefer fewer, sharper instructions
A short, specific setup beats a long defensive one. Keep durable constraints, project facts, and non-obvious workflows. Cut vague style rules, generic quality advice, duplicated reminders, and stale one-off patches.

### 4. Report before editing
Do not silently rewrite instruction systems. First produce:
- a cut list with one-line reasons
- any contradictions or overlaps
- a proposed cleaned version of the root instruction file

Then let the user review before destructive edits.

### 5. Validate by task outcomes, not by aesthetics
After trimming, test the leaner setup on the user's 3 most common tasks. If outputs stay the same or improve, leave the deleted rules out. If one specific behavior regresses, add back only the minimum rule that restores it.

### 6. Treat setup hygiene as recurring maintenance
Instruction creep comes back. When useful, generate a reusable prompt or scheduled task so the setup gets re-audited regularly.
</essential_principles>

<intake>
What would you like to do?

1. Audit my current instruction setup
2. Propose a trimmed version of my setup
3. Generate a recurring audit prompt/task

Wait for the user's choice before proceeding.
</intake>

<routing>
| Response | Workflow |
|----------|----------|
| 1, "audit", "inspect", "review" | `workflows/run-setup-audit.md` |
| 2, "trim", "clean", "refactor", "rewrite" | `workflows/trim-and-validate.md` |
| 3, "schedule", "recurring", "weekly", "automation" | `workflows/schedule-recurring-audit.md` |

After reading the workflow, follow it exactly.
</routing>

<reference_index>
## References

- `references/five-filters.md` - The five audit filters and how to apply them consistently
- `templates/weekly-audit-prompt.md` - Reusable recurring audit prompt
</reference_index>

<workflows_index>
## Workflows

- `workflows/run-setup-audit.md` - Inspect the full setup and produce an audit report
- `workflows/trim-and-validate.md` - Draft a leaner setup, then validate it on common tasks
- `workflows/schedule-recurring-audit.md` - Create a reusable or scheduled recurring hygiene audit
</workflows_index>

<success_criteria>
Instruction hygiene work is complete when:
- The full active instruction surface was identified
- Each rule was evaluated with the five filters
- Redundant, conflicting, vague, and bandaid rules were flagged
- A cleaned-up root instruction file was proposed or produced
- The trimmed setup was validated on common tasks or a clear validation plan was given
- A reusable recurring audit prompt exists if the user wants ongoing hygiene
</success_criteria>
