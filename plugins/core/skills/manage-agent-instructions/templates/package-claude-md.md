# Template: Package-Level CLAUDE.md

Use this template for individual packages in a monorepo.

---

```markdown
# {{PACKAGE_NAME}}

{{One-sentence description of this package's responsibility.}}

## Commands

```bash
{{package_manager}} dev      # Start development
{{package_manager}} test     # Run tests
{{package_manager}} build    # Build for production
```

## Stack

{{Package-specific technology stack, e.g.:}}
Node.js GraphQL API using Prisma and PostgreSQL.

## Package Conventions

{{Only conventions specific to this package:}}
For shared conventions, see root CLAUDE.md.
```

---

## Template Notes

**Package description:**
- One sentence describing this package's role
- What responsibility does it handle in the system?
- Example: "GraphQL API server handling user authentication and data access."

**Commands:**
- Package-local commands only
- Assumes running from package directory
- Don't duplicate root-level commands

**Stack:**
- Technology specific to this package
- Helps agent understand the environment
- Keep to one line if possible

**Conventions:**
- Only package-specific deviations
- Reference root for shared conventions
- Delete section if nothing package-specific

**Target size:**
- 50-100 words ideal
- Under 150 words maximum
- If longer, extract to progressive disclosure files

**What NOT to include:**
- Content covered in root CLAUDE.md
- Detailed guides (use docs/ files)
- Cross-package concerns
