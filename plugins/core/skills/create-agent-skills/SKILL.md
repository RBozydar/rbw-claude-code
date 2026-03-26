---
name: create-agent-skills
description: This skill should be used when working with SKILL.md files, authoring new skills, improving existing skills, or understanding skill structure and best practices. It provides expert guidance for creating, writing, building, and refining Claude Code skills.
---

<essential_principles>

Skills are modular, filesystem-based capabilities that provide domain expertise on demand. This skill teaches how to create effective skills.

**Skills are prompts.** All prompting best practices apply. Be clear, be direct, use XML structure. Assume Claude is smart -- only add context Claude does not have.

**SKILL.md is always loaded.** When a skill is invoked, Claude reads SKILL.md. Essential principles go in SKILL.md (cannot be skipped), workflow-specific content goes in workflows/, reusable knowledge goes in references/.

**Router pattern for complex skills:**
```
skill-name/
├── SKILL.md              # Router + principles
├── workflows/            # Step-by-step procedures (FOLLOW)
├── references/           # Domain knowledge (READ)
├── templates/            # Output structures (COPY + FILL)
└── scripts/              # Reusable code (EXECUTE)
```

SKILL.md asks what to do, routes to workflow, workflow specifies which references to read.

**Pure XML structure.** Use semantic XML tags (`<objective>`, `<process>`, `<success_criteria>`), not markdown headings in the skill body. Keep markdown formatting within content (bold, lists, code blocks).

**Progressive disclosure.** SKILL.md under 500 lines. Split detailed content into reference files. Load only what is needed for the current workflow.

</essential_principles>

<intake>

What needs to be done?

1. Create new skill
2. Audit/modify existing skill
3. Add component (workflow/reference/template/script)
4. Get guidance

Wait for response before proceeding.

</intake>

<routing>

| Response | Action |
|----------|--------|
| 1, "create", "new", "build" | Ask: "Task-execution skill or domain expertise skill?" then route to appropriate create workflow |
| 2, "audit", "modify", "existing" | Ask: "Path to skill?" then route to appropriate workflow |
| 3, "add", "component" | Ask: "Add what? (workflow/reference/template/script)" then route to workflows/add-{type}.md |
| 4, "guidance", "help" | workflows/get-guidance.md |

**Intent-based routing (if user provides clear intent without menu selection):**
- "audit", "check", "review" → workflows/audit-skill.md
- "verify content" → workflows/verify-skill.md
- "domain expertise", "knowledge base" → workflows/create-domain-expertise-skill.md
- "create skill for X" → workflows/create-new-skill.md
- "upgrade to router" → workflows/upgrade-to-router.md

After reading the workflow, follow it exactly.

</routing>

<quick_reference>

**Simple skill (single file):**
```yaml
---
name: skill-name
description: What it does and when to use it (third person).
---
```
```xml
<objective>What this skill does</objective>
<process>Step-by-step procedure</process>
<success_criteria>How to know it worked</success_criteria>
```

**Complex skill (router pattern):**
```
SKILL.md:     <essential_principles> + <intake> + <routing>
workflows/:   <required_reading> + <process> + <success_criteria>
references/:  Domain knowledge, patterns, examples
templates/:   Output structures to copy and fill
scripts/:     Executable code to run as-is
```

</quick_reference>

<templates_index>

**Templates** in `templates/`:

| Template | Use Case |
|----------|----------|
| [simple-skill.md](./templates/simple-skill.md) | Single-file skill template |
| [router-skill.md](./templates/router-skill.md) | Multi-workflow router skill template |

</templates_index>

<reference_index>

**References** in `references/`:

- **Structure:** [recommended-structure.md](./references/recommended-structure.md), [skill-structure.md](./references/skill-structure.md)
- **Principles:** [core-principles.md](./references/core-principles.md), [be-clear-and-direct.md](./references/be-clear-and-direct.md), [use-xml-tags.md](./references/use-xml-tags.md)
- **Patterns:** [common-patterns.md](./references/common-patterns.md), [workflows-and-validation.md](./references/workflows-and-validation.md)
- **Assets:** [using-templates.md](./references/using-templates.md), [using-scripts.md](./references/using-scripts.md)
- **Advanced:** [executable-code.md](./references/executable-code.md), [api-security.md](./references/api-security.md), [iteration-and-testing.md](./references/iteration-and-testing.md)

</reference_index>

<workflows_index>

**Workflows** in `workflows/`:

| Workflow | Purpose |
|----------|---------|
| create-new-skill.md | Build a skill from scratch |
| create-domain-expertise-skill.md | Build exhaustive domain knowledge base |
| audit-skill.md | Analyze skill against best practices |
| verify-skill.md | Check if content is still accurate |
| add-workflow.md | Add a workflow to existing skill |
| add-reference.md | Add a reference to existing skill |
| add-template.md | Add a template to existing skill |
| add-script.md | Add a script to existing skill |
| upgrade-to-router.md | Convert simple skill to router pattern |
| get-guidance.md | Help decide what kind of skill to build |

</workflows_index>

<yaml_requirements>

Required frontmatter fields:
```yaml
---
name: skill-name          # lowercase-with-hyphens, matches directory
description: ...          # What it does AND when to use it (third person)
---
```

Naming conventions: `create-*`, `manage-*`, `setup-*`, `generate-*`, `build-*`

</yaml_requirements>

<success_criteria>

A well-structured skill:
- Has valid YAML frontmatter with third-person description
- Uses pure XML structure (no markdown headings in body)
- Has essential principles inline in SKILL.md
- Routes to appropriate workflows based on user intent
- Keeps SKILL.md under 500 lines
- Asks minimal clarifying questions only when truly needed

</success_criteria>
