---
name: compound-docs
description: This skill should be used when a problem has been solved and needs to be captured as categorized documentation with YAML frontmatter for searchable institutional knowledge.
allowed-tools:
  - Read
  - Write
  - Bash
  - Grep
preconditions:
  - Problem has been solved (not in-progress)
  - Solution has been verified working
---

# compound-docs

Automatically document solved problems to build searchable institutional knowledge with category-based organization and enum-validated problem types.

## Overview

This skill captures problem solutions immediately after confirmation, creating structured documentation that serves as a searchable knowledge base for future sessions.

**Organization:** Single-file architecture -- each problem documented as one markdown file in its symptom category directory (e.g., `docs/solutions/performance-issues/n-plus-one-briefs.md`). Files use YAML frontmatter for metadata and searchability.

## 7-Step Process

### Step 1: Detect Confirmation

Auto-invoke after phrases like "that worked", "it's fixed", "working now", "problem solved", "that did it". Also invocable via `/doc-fix` command.

**Non-trivial problems only** -- document when multiple investigation attempts were needed, debugging was tricky, the solution was non-obvious, or future sessions would benefit. Skip simple typos, obvious syntax errors, and trivial fixes.

### Step 2: Gather Context

Extract from conversation history:

- **Module name**: Which module had the problem
- **Symptom**: Observable error/behavior (exact error messages)
- **Investigation attempts**: What didn't work and why
- **Root cause**: Technical explanation of actual problem
- **Solution**: What fixed it (code/config changes)
- **Prevention**: How to avoid in future
- **Environment details**: Rails version, stage (0-6 or post-implementation), file/line references

**Blocking requirement:** If critical context is missing (module name, exact error, stage, or resolution steps), request the missing details and wait for a response before proceeding.

### Step 3: Check Existing Docs

Search `docs/solutions/` for similar issues by error message keywords and symptom category.

**If a similar issue is found:** Present options -- create new doc with cross-reference (recommended), update existing doc (only if same root cause), or other. Wait for user response.

**If no similar issue found:** Proceed directly to Step 4.

### Step 4: Generate Filename

Format: `[sanitized-symptom]-[module]-[YYYYMMDD].md`

Sanitization: lowercase, replace spaces with hyphens, remove special characters except hyphens, truncate to < 80 chars.

### Step 5: Validate YAML Schema

All docs require validated YAML frontmatter. Load [references/schema.yaml](./references/schema.yaml) and classify the problem against the enum values defined in [yaml-schema.md](./references/yaml-schema.md). Ensure all required fields are present and match allowed values exactly.

**Block if validation fails** -- show specific errors, present retry with corrected values, do not proceed until valid.

### Step 6: Create Documentation

Determine category from `problem_type` using the category mapping in [yaml-schema.md](./references/yaml-schema.md).

Create the documentation file using the template from [assets/resolution-template.md](./assets/resolution-template.md), populated with context from Step 2 and validated YAML frontmatter from Step 5.

```bash
mkdir -p "docs/solutions/${CATEGORY}"
# Write documentation to docs/solutions/${CATEGORY}/${FILENAME}
```

### Step 7: Cross-Reference and Critical Pattern Detection

If similar issues were found in Step 3, add cross-references to both documents.

If this represents a common pattern (3+ similar issues), add an entry to `docs/solutions/patterns/common-solutions.md`.

**Critical pattern detection:** If the issue has severity `critical`, affects multiple modules or foundational stages, and has a non-obvious solution, suggest adding to Required Reading in the decision menu. Do not auto-promote -- the user decides.

When the user selects "Add to Required Reading", use the template from [assets/critical-pattern-template.md](./assets/critical-pattern-template.md) to structure the pattern entry.

## Decision Menu After Capture

After successful documentation, present options and wait for user response:

1. **Continue workflow** -- return to calling skill/workflow
2. **Add to Required Reading** -- promote to critical patterns (for patterns that must be followed every time)
3. **Link related issues** -- connect to similar problems
4. **Add to existing skill** -- add to a learning skill
5. **Create new skill** -- extract into new learning skill
6. **View documentation** -- display what was captured
7. **Other**

## Integration Points

- **Invoked by:** `/compound` command, manual invocation, or auto-detection of confirmation phrases
- **Invokes:** None (terminal skill)
- **Prerequisite:** All context needed for documentation should be present in conversation history

## Success Criteria

- YAML frontmatter validated against [references/schema.yaml](./references/schema.yaml)
- File created in `docs/solutions/[category]/[filename].md`
- Enum values match schema exactly
- Code examples included in solution section
- Cross-references added if related issues found
- User presented with decision menu

## References

- [references/schema.yaml](./references/schema.yaml) -- authoritative YAML schema definition
- [references/yaml-schema.md](./references/yaml-schema.md) -- schema documentation with category mapping
- [references/quality-guidelines.md](./references/quality-guidelines.md) -- documentation quality standards
- [references/example-scenario.md](./references/example-scenario.md) -- walkthrough of the full 7-step process
- [assets/resolution-template.md](./assets/resolution-template.md) -- documentation file template
- [assets/critical-pattern-template.md](./assets/critical-pattern-template.md) -- critical pattern entry template
