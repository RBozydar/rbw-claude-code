# Template: Minimal CLAUDE.md

Use this template for new projects. Fill in placeholders, delete unused sections.

---

```markdown
# {{PROJECT_NAME}}

{{One-sentence description of what this project does.}}

## Commands

```bash
{{package_manager}} install
{{package_manager}} run build
{{package_manager}} test
```

## Conventions

{{Only if you have documented conventions:}}
For code style, see docs/CONVENTIONS.md
```

---

## Template Notes

**Project description:**
- One sentence only
- Acts as a role prompt for the agent
- Example: "React component library for accessible data visualization."

**Package manager:**
- Omit if using npm (default)
- Specify if using pnpm, yarn, bun

**Conventions section:**
- Delete if no documented conventions exist
- Point to files, don't inline content
- Each convention topic gets its own file

**What NOT to include:**
- Detailed file paths
- Comprehensive style guides
- Auto-generated boilerplate
- "Write clean code" type guidance
