# Workflow: Refactor Bloated Instruction File

<required_reading>
**Read these reference files:**
1. references/common-problems.md
2. references/progressive-disclosure.md
3. references/claude-md-format.md
</required_reading>

<process>
## Step 1: Read Current File

```bash
# Read the file
cat CLAUDE.md  # or AGENTS.md
```

Identify:
- Total line count
- Major sections
- Types of content

## Step 2: Find Contradictions

Analyze for conflicting instructions:

**Common contradiction patterns:**
- "Always use X" vs "Never use X"
- "Prefer A" vs "Use B instead"
- Different coding standards in different sections

For each contradiction found, note:
- The conflicting statements
- Line numbers
- What decision is needed

**If contradictions found**, present them to user:

"Found conflicting instructions. Which version do you want?"

Example:
```
Conflict 1:
- Line 45: "Always use const"
- Line 112: "Use let for variables that change"

Which should we keep?
1. Always use const (strict)
2. Use let when value changes (flexible)
```

Wait for user decision before proceeding.

## Step 3: Identify Essentials

Extract content that belongs in root:

**Must keep in root:**
- One-sentence project description
- Package manager
- Non-standard build/test commands
- Critical warnings (if any)

**Everything else is a candidate for extraction.**

## Step 4: Group Remaining Content

Categorize remaining instructions:

| Category | Examples | Target File |
|----------|----------|-------------|
| Language conventions | TypeScript rules, ESLint config | docs/TYPESCRIPT.md |
| Testing patterns | Jest setup, coverage rules | docs/TESTING.md |
| API design | REST conventions, error handling | docs/API.md |
| Git workflow | Branch naming, commit format | docs/GIT.md |
| Architecture | Module structure, patterns | docs/ARCHITECTURE.md |

## Step 5: Identify Deletions

Mark for removal:
- Redundant instructions (agent knows this)
- Vague guidance ("write clean code")
- Overly obvious rules
- Stale file paths
- Duplicate content

Present deletion candidates to user:

"These instructions are redundant or vague. Remove them?"

```markdown
- "Use descriptive variable names" (obvious)
- "Write clean, maintainable code" (vague)
- "Handle errors appropriately" (obvious)
```

## Step 6: Create Progressive Disclosure Files

```bash
mkdir -p docs
```

For each category with substantial content:

```bash
# Create category file
cat > docs/TYPESCRIPT.md << 'EOF'
# TypeScript Conventions

[Extracted TypeScript content here]
EOF
```

## Step 7: Rewrite Root File

Create minimal root file:

```markdown
# [Project Name]

[One-sentence description]

## Commands

```bash
[Essential commands]
```

## Conventions

- TypeScript: docs/TYPESCRIPT.md
- Testing: docs/TESTING.md
- [Other categories as needed]

## Notes

[Any critical warnings - only if truly essential]
```

## Step 8: Validate Refactor

**Before/After comparison:**

| Metric | Before | After |
|--------|--------|-------|
| Root lines | X | Y |
| Root words | X | Y |
| Total files | 1 | N |
| Contradictions | X | 0 |

**Checks:**
- [ ] Root file under 300 words
- [ ] No contradictions remain
- [ ] No redundant instructions
- [ ] No stale file paths
- [ ] Progressive disclosure pointers work
- [ ] All extracted files exist

## Step 9: Present Result

Show:
1. New root file content
2. Files created in docs/
3. What was deleted
4. Before/after metrics

Ask: "Apply these changes?"

Options:
1. **Apply all** - Make all changes
2. **Review each** - Go through changes one by one
3. **Adjust** - Modify the plan before applying

</process>

<success_criteria>
Refactor is complete when:
- [ ] All contradictions resolved (user decided)
- [ ] Root file under 300 words
- [ ] Detailed content moved to docs/
- [ ] Redundant instructions removed
- [ ] No stale file paths remain
- [ ] Progressive disclosure structure works
- [ ] User approved final result
</success_criteria>
