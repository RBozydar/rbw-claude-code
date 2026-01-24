# Workflow: Create New Instruction File

<required_reading>
**Read these reference files:**
1. references/claude-md-format.md (for CLAUDE.md)
2. references/agents-md-standard.md (for AGENTS.md)
3. references/progressive-disclosure.md
</required_reading>

<process>
## Step 1: Determine File Type

Ask using AskUserQuestion:

"Which instruction file should I create?"

Options:
1. **CLAUDE.md** - For Claude Code specifically
2. **AGENTS.md** - Open standard for multiple tools
3. **Both (synced)** - Primary CLAUDE.md with symlinked AGENTS.md

## Step 2: Gather Project Context

**If user provided context**, extract:
- Project name and purpose
- Technology stack
- Package manager
- Build/test commands
- Any specific conventions mentioned

**If context missing**, ask:

"Tell me about your project in 1-2 sentences. What does it do?"

Follow up only if essential info missing:
- "What package manager do you use?" (if not obvious)
- "Any non-standard build commands?"

## Step 3: Check for Existing Files

```bash
# Check for existing instruction files
ls -la CLAUDE.md AGENTS.md .claude/CLAUDE.md 2>/dev/null || echo "No existing files"

# Check for monorepo structure
ls -d packages/* apps/* 2>/dev/null || echo "Not a monorepo"
```

If existing files found, ask:
"Found existing [file]. Replace it or merge with new content?"

## Step 4: Create Minimal Root File

**For CLAUDE.md:**

```markdown
# [Project Name]

[One-sentence description from Step 2]

## Commands

```bash
[package manager] install
[package manager] run build
[package manager] test
```

## Conventions

[Only if user specified any - otherwise omit this section]
```

**For AGENTS.md:**

Same structure. The open standard uses plain markdown without YAML frontmatter requirements.

## Step 5: Create Progressive Disclosure Structure (if needed)

If user mentioned specific conventions or the project is complex:

```bash
mkdir -p docs
```

Create placeholder files:
- `docs/CONVENTIONS.md` - Code style
- `docs/ARCHITECTURE.md` - System design
- `docs/TESTING.md` - Test patterns

Only create files user actually needs. Don't generate boilerplate.

## Step 6: Create Symlink (if "Both" selected)

```bash
# Primary: CLAUDE.md
# Symlink: AGENTS.md -> CLAUDE.md
ln -s CLAUDE.md AGENTS.md
```

## Step 7: Validate

Check:
- [ ] Root file under 300 words
- [ ] No detailed file paths (describe capabilities instead)
- [ ] Essential commands present
- [ ] Progressive disclosure pointers if conventions exist
- [ ] Symlink works (if created)

## Step 8: Present Result

Show the created file(s) and explain:
- What was created
- How progressive disclosure works
- How to add more content later

</process>

<success_criteria>
Creation is complete when:
- [ ] Appropriate file type created (CLAUDE.md, AGENTS.md, or both)
- [ ] Root file is minimal (~100-300 words)
- [ ] Project description is one sentence
- [ ] Build commands are documented
- [ ] Progressive disclosure structure exists (if needed)
- [ ] No file paths documented (describe capabilities)
- [ ] User understands how to extend it
</success_criteria>
