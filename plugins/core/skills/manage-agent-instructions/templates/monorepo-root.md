# Template: Monorepo Root CLAUDE.md

Use this template for monorepo root instruction files.

---

```markdown
# {{MONOREPO_NAME}}

{{One-sentence description of what this system does.}}

## Navigation

This is a monorepo. Explore packages:
```bash
ls packages/  # or ls apps/
```

Each package has its own CLAUDE.md with specific instructions.

## Shared Tools

- Package manager: {{pnpm|yarn|npm}}
- Run all tests: {{package_manager}} test
- Build all: {{package_manager}} build

## Packages

| Package | Purpose |
|---------|---------|
| {{package1}} | {{brief description}} |
| {{package2}} | {{brief description}} |

## Shared Conventions

For conventions that apply across all packages:
- Code style: docs/CONVENTIONS.md
- Testing: docs/TESTING.md
```

---

## Template Notes

**Root file scope:**
- Monorepo-level context only
- How to navigate
- Shared tools
- Cross-cutting concerns

**Package table:**
- Keep brief
- Link to package CLAUDE.md for details
- Update when packages change

**Conventions:**
- Only shared/cross-cutting conventions
- Package-specific conventions go in package CLAUDE.md

**What NOT to include:**
- Package-specific details
- Detailed build instructions per package
- Content duplicated in package files
