# Common Problems and Solutions

## Problem 1: Ball of Mud

**Symptoms:**
- File grows over months
- Contradicting instructions
- Nobody maintains it
- Agent performance degrades

**Cause:**
Natural feedback loop:
1. Agent does something wrong
2. Add rule to prevent it
3. Repeat hundreds of times
4. File becomes unmaintainable

**Solution:**
Run the refactor workflow. Extract, deduplicate, apply progressive disclosure.

---

## Problem 2: Auto-Generated Content

**Symptoms:**
- Generic boilerplate
- Irrelevant sections
- "Useful for most scenarios" padding
- Excessive verbosity

**Cause:**
Initialization scripts prioritize comprehensiveness over restraint.

**Solution:**
Delete auto-generated content. Write minimal, focused instructions manually.

---

## Problem 3: Stale File Paths

**Symptoms:**
- Agent looks in wrong places
- Confident but incorrect navigation
- "File not found" errors

**Cause:**
Documentation says "auth logic lives in src/auth/handlers.ts" but file moved.

**Solution:**
Describe capabilities, not paths:
- Bad: "Authentication in src/auth/handlers.ts"
- Good: "AuthService module handles authentication"

---

## Problem 4: Instruction Budget Exceeded

**Symptoms:**
- Agent ignores some instructions
- Inconsistent behavior
- Later instructions not followed

**Cause:**
Frontier models follow ~150-200 instructions reliably. Smaller models fewer.

**Solution:**
- Reduce total instruction count
- Move detailed instructions to progressive disclosure files
- Prioritize critical instructions in root

---

## Problem 5: Contradicting Instructions

**Symptoms:**
- Agent behavior varies
- Different developers added conflicting opinions
- No single source of truth

**Cause:**
Multiple contributors without coordination.

**Solution:**
1. Identify all contradictions
2. Decide which version to keep (ask stakeholders)
3. Remove duplicates
4. Single source of truth per topic

---

## Problem 6: Redundant Instructions

**Symptoms:**
- Telling agent things it already knows
- Obvious guidance ("use descriptive names")
- Model-level capabilities documented

**Cause:**
Overestimating what needs explicit instruction.

**Solution:**
Remove:
- "Write clean code"
- "Use meaningful variable names"
- "Handle errors appropriately"
- Basic language features

Keep only project-specific deviations from defaults.

---

## Problem 7: Tool Fragmentation

**Symptoms:**
- Different files for different tools
- Duplicated content
- Maintenance burden

**Cause:**
- Cursor uses .cursor/rules/
- Claude Code uses CLAUDE.md
- Copilot uses .github/copilot-instructions.md
- AGENTS.md is cross-tool standard

**Solution:**
Choose primary file, symlink or redirect others:
```bash
ln -s CLAUDE.md AGENTS.md
```

Or use AGENTS.md as primary with tool-specific overrides.

---

## Problem 8: Monorepo Duplication

**Symptoms:**
- Same instructions in multiple package CLAUDE.md files
- Inconsistent updates
- Maintenance burden

**Cause:**
Copy-paste without considering hierarchy.

**Solution:**
- Root: shared conventions
- Package: package-specific only
- Reference root from packages when needed

---

## Quick Diagnostic Checklist

| Check | Problem If |
|-------|------------|
| Line count | > 500 lines |
| File paths | Mentioned directly |
| Instruction count | > 150 distinct rules |
| Last update | > 3 months ago |
| Contradictions | Any present |
| Vague guidance | "Write clean code" etc. |
| Auto-generated | Init scripts used |
| Tool-specific | Multiple similar files |

Score 3+ problems: refactor needed.
