# Workflow: Sync CLAUDE.md and AGENTS.md

<required_reading>
**Read these reference files:**
1. references/agents-md-standard.md
2. references/claude-md-format.md
</required_reading>

<process>
## Step 1: Check Current State

```bash
# Check what exists
ls -la CLAUDE.md AGENTS.md 2>/dev/null

# Check if either is a symlink
file CLAUDE.md AGENTS.md 2>/dev/null

# Check content similarity if both exist
if [ -f CLAUDE.md ] && [ -f AGENTS.md ]; then
  diff CLAUDE.md AGENTS.md
fi
```

## Step 2: Determine Sync Strategy

Based on findings, present options:

**If neither exists:**
"No instruction files found. Would you like to create them?"
→ Route to create-instructions workflow

**If only one exists:**
"Found [file]. Create the other as:"
1. **Symlink** - AGENTS.md → CLAUDE.md (or vice versa)
2. **Copy** - Duplicate content (separate maintenance)
3. **Redirect** - Second file just points to first

**If both exist with different content:**
"Both files exist with different content."
1. **Merge into CLAUDE.md** - Combine, use symlink for AGENTS.md
2. **Merge into AGENTS.md** - Combine, use symlink for CLAUDE.md
3. **Keep separate** - Maintain different content per tool

**If symlink already exists:**
"Files already synced via symlink. Nothing to do."

## Step 3: Execute Sync Strategy

### Option A: Symlink (Recommended)

```bash
# Determine primary (usually CLAUDE.md for Claude Code users)
PRIMARY="CLAUDE.md"
SECONDARY="AGENTS.md"

# Remove secondary if it exists
rm -f "$SECONDARY"

# Create symlink
ln -s "$PRIMARY" "$SECONDARY"

# Verify
ls -la CLAUDE.md AGENTS.md
```

### Option B: Redirect

Create minimal redirect file:

```bash
cat > AGENTS.md << 'EOF'
# Agent Instructions

For AI coding agent instructions, see [CLAUDE.md](./CLAUDE.md).

This project uses CLAUDE.md as the primary instruction file.
EOF
```

### Option C: Merge

If both files have unique content:

1. Read both files
2. Identify unique content in each
3. Merge non-conflicting content
4. Present conflicts for user decision
5. Write merged content to primary
6. Create symlink for secondary

## Step 4: Handle Tool-Specific Overrides

If user needs tool-specific differences:

```markdown
# AGENTS.md (if not symlinking)

[Shared content]

## Tool-Specific Notes

### Cursor
[Cursor-specific instructions if needed]

### Codex
[Codex-specific instructions if needed]
```

Alternatively, use .cursor/rules/ for Cursor-specific content alongside shared AGENTS.md.

## Step 5: Verify Sync

```bash
# Verify symlink works
cat AGENTS.md | head -5

# Verify both point to same content
md5sum CLAUDE.md AGENTS.md 2>/dev/null || shasum CLAUDE.md AGENTS.md

# Check symlink target
readlink AGENTS.md 2>/dev/null || echo "Not a symlink"
```

## Step 6: Document Setup

Add note to README or development docs:

```markdown
## AI Agent Instructions

This project uses CLAUDE.md for AI coding agent instructions.
AGENTS.md is symlinked to CLAUDE.md for cross-tool compatibility.

To modify instructions, edit CLAUDE.md only.
```

</process>

<success_criteria>
Sync is complete when:
- [ ] Both files exist (or are documented as unnecessary)
- [ ] Sync strategy chosen and executed
- [ ] Content is consistent across files
- [ ] Symlink verified working (if used)
- [ ] No duplicate maintenance required
- [ ] Setup documented for future contributors
</success_criteria>
