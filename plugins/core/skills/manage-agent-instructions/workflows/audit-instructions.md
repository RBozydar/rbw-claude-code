# Workflow: Audit Existing Instruction File

<required_reading>
**Read these reference files:**
1. references/common-problems.md
2. references/progressive-disclosure.md
</required_reading>

<process>
## Step 1: Locate Files

```bash
# Find all instruction files
find . -name "CLAUDE.md" -o -name "AGENTS.md" -o -name "copilot-instructions.md" 2>/dev/null | head -20

# Check common locations
ls -la CLAUDE.md AGENTS.md .claude/CLAUDE.md .github/copilot-instructions.md .cursor/rules/*.md 2>/dev/null
```

If multiple files found, ask which to audit.

## Step 2: Read and Analyze

Read the target file and run these checks:

### Size Check
```bash
wc -l [file]
wc -w [file]
```

| Metric | Good | Warning | Problem |
|--------|------|---------|---------|
| Lines | <100 | 100-300 | >300 |
| Words | <300 | 300-800 | >800 |

### Content Analysis

Count and categorize:
1. **Instructions** - Direct rules ("always use X", "never do Y")
2. **File paths** - Specific paths mentioned
3. **Redundant guidance** - Things agent already knows
4. **Build commands** - Essential operational info
5. **Project context** - Description, purpose

### Contradiction Detection

Look for:
- Conflicting rules (A says X, B says opposite)
- Overlapping guidance (same thing stated differently)
- Contradicting examples

### Staleness Check

- Are file paths still valid?
- Do commands still work?
- Is stack description current?

## Step 3: Generate Audit Report

Structure the report:

```markdown
## Audit Report: [filename]

### Summary
- Lines: X (Good/Warning/Problem)
- Words: X (Good/Warning/Problem)
- Instruction count: X
- File paths mentioned: X
- Contradictions found: X

### Issues Found

#### Critical
[List critical issues - contradictions, stale paths, etc.]

#### Moderate
[List moderate issues - bloat, redundancy]

#### Minor
[List minor issues - style, organization]

### Recommendations

1. [Most important action]
2. [Second priority]
3. [Third priority]

### Progressive Disclosure Opportunities

Content that should move to separate files:
- [Topic] -> docs/[TOPIC].md
- [Topic] -> docs/[TOPIC].md
```

## Step 4: Detailed Findings

For each issue found, provide:
- **What**: The specific problem
- **Where**: Line numbers or quotes
- **Why**: Why it's a problem
- **Fix**: How to resolve it

## Step 5: Present Options

After presenting the report:

"Based on this audit, what would you like to do?"

Options:
1. **Run refactor workflow** - Automatically fix the issues
2. **Manual fixes** - I'll guide you through fixing specific issues
3. **Export report** - Save this audit for later action
4. **Done** - Just needed the analysis

</process>

<success_criteria>
Audit is complete when:
- [ ] File located and read
- [ ] Size metrics calculated
- [ ] Instruction count determined
- [ ] File paths identified
- [ ] Contradictions found (or confirmed none)
- [ ] Staleness checked
- [ ] Report generated with clear recommendations
- [ ] User has clear next steps
</success_criteria>
