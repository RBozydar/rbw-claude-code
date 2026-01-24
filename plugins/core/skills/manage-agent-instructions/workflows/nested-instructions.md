# Workflow: Add Nested Package Instructions

<required_reading>
**Read these reference files:**
1. references/progressive-disclosure.md
2. references/claude-md-format.md
</required_reading>

<process>
## Step 1: Identify Monorepo Structure

```bash
# Find package directories
ls -d packages/* apps/* modules/* 2>/dev/null

# Check for existing nested instruction files
find . -name "CLAUDE.md" -o -name "AGENTS.md" 2>/dev/null | grep -v "^./CLAUDE.md" | grep -v "^./AGENTS.md"

# Check root file exists
cat CLAUDE.md 2>/dev/null | head -10
```

## Step 2: Understand Package Purpose

Ask user or infer from package.json/directory:

"Which package needs instructions?"

For the selected package:
```bash
# Get package info
cat packages/[name]/package.json 2>/dev/null | head -20

# Check package structure
ls packages/[name]/
```

## Step 3: Determine Content Split

**Root level should have:**
- Monorepo purpose
- How to navigate between packages
- Shared tools (pnpm workspaces, etc.)
- Cross-cutting concerns

**Package level should have:**
- Package purpose
- Package-specific tech stack
- Local build/test commands
- Package-specific conventions

**Never duplicate** - if it's in root, don't repeat in package.

## Step 4: Create/Update Root File

If root doesn't mention monorepo structure:

```markdown
# [Monorepo Name]

[One-sentence description of the whole system]

## Navigation

This is a monorepo. Explore with:
```bash
ls packages/  # or ls apps/
```

Each package has its own CLAUDE.md with specific instructions.

## Shared Tools

- Package manager: pnpm
- Run all tests: pnpm test
- Build all: pnpm build
```

## Step 5: Create Package Instruction File

For the selected package:

```bash
cat > packages/[name]/CLAUDE.md << 'EOF'
# [Package Name]

[One-sentence description of this package's responsibility]

## Commands

```bash
pnpm dev      # Start development
pnpm test     # Run tests
pnpm build    # Build for production
```

## Stack

[Package-specific technology, e.g., "Node.js GraphQL API using Prisma"]

## Conventions

[Only package-specific conventions not covered by root]
For shared conventions, see root CLAUDE.md.
EOF
```

## Step 6: Handle AGENTS.md Sync

If using both CLAUDE.md and AGENTS.md:

```bash
# Create symlink in package
cd packages/[name]
ln -s CLAUDE.md AGENTS.md
```

## Step 7: Verify Hierarchy

Test that the right file loads in the right context:

```bash
# From package directory
cd packages/[name]
cat CLAUDE.md

# From root
cd ../..
cat CLAUDE.md
```

Verify:
- [ ] Root file describes monorepo
- [ ] Package file describes package
- [ ] No duplication between them
- [ ] Package can reference root for shared info

## Step 8: Update Navigation

If creating multiple package files, add to root:

```markdown
## Packages

| Package | Purpose |
|---------|---------|
| api | GraphQL API server |
| web | Next.js frontend |
| shared | Shared utilities |

Each has its own CLAUDE.md for package-specific instructions.
```

## Step 9: Present Result

Show:
1. Updated root file (if changed)
2. New package file
3. How navigation works
4. How to add more packages

</process>

<success_criteria>
Nested instructions are complete when:
- [ ] Root file describes monorepo structure
- [ ] Package file describes package-specific context
- [ ] No content duplication between levels
- [ ] Navigation is clear
- [ ] Package file is minimal (~50-100 words)
- [ ] AGENTS.md synced if needed
- [ ] User understands how to add more packages
</success_criteria>
