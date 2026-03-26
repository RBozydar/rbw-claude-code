---
name: create-rule
description: This skill should be used when developing custom rules for coding standards, conventions, or guidelines that Claude should follow. It covers rule structure, types, and best practices.
---

# Create Rules

Develop effective Claude Code rules. Rules are markdown files in `.claude/rules/` that provide persistent instructions Claude follows during a session.

## What Rules Are For

- Coding standards and conventions
- Project-specific guidelines
- Language or framework patterns
- Prohibited practices
- Style preferences

**Not for:** one-time instructions (tell Claude directly), dynamic content (use commands/skills), or tool configurations (use hooks).

## Rule Structure

```markdown
# Rule Name

Brief description of what this rule enforces.

## Guidelines
Clear, actionable rules with examples.

## Checklist (optional)
- [ ] Quick verification items
```

**Key principles:** Be specific (vague rules get ignored), show examples (good vs bad), stay focused (one topic per file), be actionable (guide decisions).

## Rule Types

### Standards Rules

Define coding standards. Copy and customize `templates/standards.md`:

```bash
cp ${CLAUDE_PLUGIN_ROOT}/skills/create-rule/templates/standards.md .claude/rules/my-standards.md
```

Use for: naming conventions, preferred patterns, type inference rules.

### Prohibited Rules

List things to avoid. Copy and customize `templates/prohibited.md`:

```bash
cp ${CLAUDE_PLUGIN_ROOT}/skills/create-rule/templates/prohibited.md .claude/rules/my-prohibited.md
```

Use for: banned patterns with good/bad examples, quick checklists.

### Style Rules

Define formatting preferences. Copy and customize `templates/style.md`:

```bash
cp ${CLAUDE_PLUGIN_ROOT}/skills/create-rule/templates/style.md .claude/rules/my-style.md
```

Use for: import ordering, comment conventions, formatting preferences.

### Architecture Rules

Define structural patterns for service layers, dependency direction, module organization.

## Best Practices

**Do:** Use tables for quick reference, include code examples for every guideline, group related items, provide a checklist, keep rules under 200 lines.

**Do not:** Write walls of text, be vague ("write good code"), include too many topics in one file, repeat what other rules cover.

## Templates

All templates are available at:

```
${CLAUDE_PLUGIN_ROOT}/skills/create-rule/templates/
├── standards.md   # Coding standards template
├── prohibited.md  # Prohibited patterns template
└── style.md       # Style guide template
```

## Contributing Rules

To add a rule to rbw-claude-code:

1. Create the rule in `templates/rules/` or a subdirectory
2. Follow the structure of existing rules
3. Test by symlinking to a project
