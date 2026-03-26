---
name: skill-creator
description: Guide for creating or updating a Claude Code skill. Use this skill when defining a new skill, restructuring an existing one, deciding what belongs in SKILL.md vs bundled resources, or improving a skill that under-triggers, over-prescribes, or lacks high-signal guidance.
license: Complete terms in LICENSE.txt
---

# Skill Creator

This skill provides guidance for creating effective skills.

## Core Mental Model

Treat a skill as a folder-based capability, not just a markdown note. A strong skill gives Claude non-obvious knowledge, reusable tools, and just enough structure to execute well without being railroaded.

Optimize for the delta from Claude's default behavior:
- Add information Claude would not reliably infer on its own
- Add gotchas, edge cases, and failure patterns
- Add reusable scripts, templates, and references when they save turns or improve reliability
- Keep the top-level skill lean and use the filesystem for progressive disclosure

A mediocre skill restates obvious steps.
A strong skill changes what Claude can do or how reliably it can do it.

## What High-Value Skills Usually Do

Most strong skills fall primarily into one category. Prefer a clean primary category instead of blending several unrelated ones.

1. Library and API reference
   - Explain how to use an internal or external library, SDK, CLI, or framework correctly
   - Focus on footguns, edge cases, unsupported patterns, and working examples

2. Product verification
   - Explain how to test or verify behavior using tools like Playwright, tmux, screenshots, videos, or assertions
   - Often worth extra investment because verification quality compounds across many tasks

3. Data fetching and analysis
   - Connect Claude to dashboards, SQL systems, warehouse schemas, observability stacks, or canonical joins
   - Include identifiers, lookup tables, and common analysis workflows

4. Business process and team automation
   - Automate recurring operational workflows like standups, recap posts, ticket creation, or status reporting
   - May benefit from durable logs or prior-run artifacts for consistency

5. Code scaffolding and templates
   - Generate boilerplate or project structure for recurring implementation patterns
   - Usually pair well with assets and scripts

6. Code quality and review
   - Enforce review checklists, testing expectations, style guidance, or quality gates

7. CI/CD and deployment
   - Handle deploy workflows, flaky CI retries, PR checks, gradual rollout steps, and rollback procedures

8. Runbooks
   - Map symptoms or alerts to investigation steps, tools, dashboards, and report formats

9. Infrastructure operations
   - Support routine maintenance and operational tasks with explicit guardrails

If a proposed skill does not fit any of these categories, verify that it is still a real repeatable capability instead of a one-off note.

## Anatomy of a Skill

Every skill consists of a required SKILL.md file and optional bundled resources:

```text
skill-name/
├── SKILL.md
├── scripts/      # executable helpers
├── references/   # detailed docs loaded on demand
├── assets/       # templates, boilerplate, images, sample files
├── config.json   # optional user/team-specific configuration
└── logs/ or data/ if truly needed for local state
```

Use the folder structure deliberately:
- Put concise trigger and workflow guidance in SKILL.md
- Put long API details, schemas, and reference material in references/
- Put deterministic helpers in scripts/
- Put boilerplate and output resources in assets/
- Put user- or team-specific configuration in config.json when needed

When persistent writable data is required across upgrades, prefer `${CLAUDE_PLUGIN_DATA}` instead of storing state directly inside the shipped skill folder.

## Progressive Disclosure

Design the skill so Claude reads only what is needed:

1. Frontmatter is always visible
2. SKILL.md is loaded when the skill triggers
3. References, scripts, and assets are discovered and loaded only when useful

This means:
- Keep SKILL.md high-signal and relatively lean
- Move detailed reference material out of the main file
- Tell Claude what files exist and when to use them
- Avoid duplicating the same information in multiple places

Good pattern:
- SKILL.md says that detailed API signatures live in `references/api.md`
- SKILL.md says a reusable helper exists at `scripts/fetch_metrics.py`
- Claude pulls those in only when the task actually needs them

## Description Field: Write for Triggering, Not for Marketing

The description field is for the model, not for a human catalog page.
It should describe when the skill should trigger.

Write descriptions that mention:
- The kinds of requests that should activate the skill
- Important file types, systems, or domains involved
- Failure modes the skill helps with
- Whether the skill is for creation, debugging, verification, migration, review, or operations

Prefer trigger-oriented wording like:
- "Use this skill when..."
- "Guide for creating or updating... when..."
- "Apply when working with..."

Avoid vague summaries like:
- "Helpful skill for PDFs"
- "Utilities for data work"

## Gotchas Are Mandatory

A gotchas section is often the highest-signal part of the skill.

Include:
- Known failure patterns Claude has hit before
- Tool-specific footguns
- Misleading docs or defaults
- Incompatible approaches
- Cases where the obvious solution is wrong in this environment

If the skill is mostly knowledge, prioritize gotchas over generic explanation.
Start small if needed: one excellent gotcha is more valuable than pages of boilerplate.

## Avoid Railroading

Give Claude the information and tools it needs without forcing an unnecessarily rigid sequence.

Bad:
- "Always use tool A, then tool B, then grep, then rewrite the file in exactly this order"

Better:
- "Tool A is useful for retrieving live dashboard state; tool B is useful for historical comparison; use whichever combination best fits the failure mode"

Use structure where it protects correctness or safety, but avoid over-constraining normal reasoning.

## Prefer Scripts Over Repeated Prose

If Claude keeps rewriting the same helper logic, move that logic into scripts.
Use scripts when they provide:
- Deterministic reliability
- Faster execution
- Lower token usage
- Easier composition across tasks
- Better verification through assertions

Examples:
- `scripts/rotate_pdf.py`
- `scripts/run_signup_flow.py`
- `scripts/assert_invoice_state.py`
- `scripts/fetch_events.py`

Do not stop at describing what a helper should do when the helper can be shipped directly.

## Verification Skills Deserve Extra Care

Verification skills are especially valuable because they improve trust in Claude's output.
When relevant, include:
- Browser or CLI driving scripts
- Assertions on expected state after each step
- Screenshot or video capture
- Logs or structured result output for review

A good verification skill does not merely say "test the feature". It gives Claude a repeatable way to prove the feature works.

## Configuration, State, and Hooks

Use configuration and state intentionally.

### Configuration

Store user- or team-specific constants in `config.json` when needed, such as:
- Slack channel IDs
- environment names
- dashboard identifiers
- ticket schema enums

### State

Only persist state when it materially improves outcomes, such as:
- prior workflow results
- log files used for consistency across recurring reports
- cached identifiers or mappings

Prefer `${CLAUDE_PLUGIN_DATA}` for durable writable state.

### Hooks

Use hooks when they provide meaningful leverage, but prefer on-demand hooks tied to the skill instead of globally annoying restrictions.
Examples:
- A careful production skill that blocks risky commands only during production work
- A logging hook that records skill usage to measure adoption or under-triggering

## Skill Creation Process

Follow this process in order unless there is a clear reason to skip a step.

### Step 1: Collect Trigger Examples

Understand how the skill should actually be invoked.
Gather or propose concrete examples such as:
- what users would say
- what files or systems are involved
- what successful output looks like
- what commonly goes wrong today

Ask only a few focused questions at a time.
A skill is ready to design once there is a clear picture of the recurring task and its trigger patterns.

### Step 2: Choose the Skill Category and Delta

Identify the primary category from the list above.
Then identify the delta from Claude's default capabilities:
- What does Claude currently get wrong?
- What knowledge is missing?
- What repetitive work should be packaged?
- What verification or safety guardrails are needed?

If there is no meaningful delta, the task may not need a skill.

### Step 3: List Reusable Components

For each representative example, decide what should live in:
- SKILL.md
- scripts/
- references/
- assets/
- config.json
- `${CLAUDE_PLUGIN_DATA}`

Use this rule of thumb:
- Put guidance in SKILL.md
- Put detail in references/
- Put deterministic helpers in scripts/
- Put reusable output materials in assets/
- Put install- or user-specific values in config

### Step 4: Initialize the Skill

When creating a new skill from scratch, initialize the folder first.
From the repository root, run:

```bash
uv run python plugins/core/skills/skill-creator/scripts/init_skill.py <skill-name> --path <output-directory>
```

This script creates:
- the skill directory
- a starter SKILL.md
- example `scripts/`, `references/`, and `assets/` directories

Delete any example files that are not actually useful.

### Step 5: Write the Actual Skill

When editing SKILL.md, optimize for usefulness to another Claude instance.

Include:
1. A trigger-oriented frontmatter description
2. A short overview of what the skill enables
3. The main workflow or decision structure
4. Explicit references to bundled resources and when to use them
5. A gotchas section
6. Verification guidance when applicable

Write instructions in clear, direct, imperative language.
Focus on non-obvious procedural knowledge and concrete guidance.

### Step 6: Keep the Skill Lean

Remove filler, duplicated explanation, and obvious advice.
Move long reference material into `references/`.
If the skill starts feeling bloated, split detail out instead of expanding SKILL.md indefinitely.

### Step 7: Validate and Package

Before packaging, validate the finished skill.
From the repository root, run:

```bash
uv run python plugins/core/skills/skill-creator/scripts/quick_validate.py <path/to/skill-folder>
```

To package a distributable zip, run:

```bash
uv run python plugins/core/skills/skill-creator/scripts/package_skill.py <path/to/skill-folder>
```

Optional output directory:

```bash
uv run python plugins/core/skills/skill-creator/scripts/package_skill.py <path/to/skill-folder> ./dist
```

### Step 8: Test and Iterate

The best skills improve through real use.
After a skill is used:
1. Observe where Claude struggled
2. Add or refine gotchas
3. Add helper scripts if Claude keeps redoing the same work
4. Clarify trigger wording if the skill under-triggers or over-triggers
5. Move bulky detail into references if context usage becomes noisy
6. Add hooks or persistent state only when repeated pain justifies them

Treat iteration as part of the design, not as cleanup.

## Review Checklist for Existing Skills

When updating an existing skill, check for these failure modes:
- Description summarizes the skill but does not say when it should trigger
- SKILL.md restates obvious advice instead of adding high-signal knowledge
- No gotchas section exists
- Detailed docs are stuffed into SKILL.md instead of references/
- Claude is told exactly which tools to use in a rigid sequence without justification
- Repeated helper logic is described but not shipped as a script
- The skill mixes too many categories and feels unfocused
- Persistent state is stored in the wrong place
- Hooks are global and annoying instead of skill-scoped and purposeful
- No guidance exists for measuring whether the skill is actually helping

## Success Criteria

A skill is successful when:
- It triggers for the right requests
- It changes Claude's behavior in a useful way
- It contains non-obvious knowledge, especially gotchas
- It uses progressive disclosure to stay lean
- It ships reusable helpers when helpers are warranted
- It leaves Claude flexible enough to adapt to the task
- It becomes more effective as real-world edge cases are learned
