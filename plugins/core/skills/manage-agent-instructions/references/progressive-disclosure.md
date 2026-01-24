# Progressive Disclosure

## The Problem

Every token in the root instruction file loads on every request:
- Irrelevant context wastes instruction budget
- Agent performance degrades with bloated files
- Token cost increases linearly with file size

## The Solution

Structure knowledge in layers. Load only what's needed for the current task.

## Three-Level Architecture

```
Level 1: Root instruction file (~100-300 words)
         - Project purpose
         - Essential commands
         - Pointers to Level 2

Level 2: Domain-specific files (docs/*.md)
         - TypeScript conventions
         - Testing patterns
         - API design guidelines
         - Pointers to Level 3

Level 3: Detailed references
         - External documentation
         - Specific tool guides
         - Complex patterns
```

## Implementation Pattern

**Root file (CLAUDE.md):**
```markdown
# Project Name

React component library for accessible data visualization.

## Commands

npm run build
npm test

## Conventions

For TypeScript: docs/TYPESCRIPT.md
For Testing: docs/TESTING.md
For Components: docs/COMPONENTS.md
```

**Level 2 file (docs/TYPESCRIPT.md):**
```markdown
# TypeScript Conventions

## Type Definitions

Use interface over type for object shapes.
Export types from dedicated .types.ts files.

## Advanced Patterns

For generic patterns: docs/typescript/GENERICS.md
For utility types: docs/typescript/UTILITIES.md
```

## Benefits

| Aspect | Bloated Root | Progressive Disclosure |
|--------|--------------|------------------------|
| Token cost per request | High | Low |
| Relevant context | Mixed | Focused |
| Maintenance | Difficult | Modular |
| Agent performance | Degraded | Optimal |

## Guidelines for Splitting

**Keep in root:**
- Project identity (one sentence)
- Essential build commands
- Package manager
- Critical warnings

**Move to Level 2:**
- Language-specific conventions
- Testing patterns
- Architecture decisions
- API guidelines

**Move to Level 3:**
- Detailed examples
- Complex patterns
- External tool integration
- Edge case handling

## Discovery Pattern

Agents are fast at navigating documentation hierarchies. Trust them to:
1. Read root file
2. Identify relevant pointers
3. Load domain-specific files as needed
4. Navigate deeper when required

## Anti-Pattern: Flat Documentation

```markdown
# Project

## Build
...

## TypeScript
... (200 lines)

## Testing
... (150 lines)

## Components
... (300 lines)

## API
... (250 lines)
```

This loads 900+ lines on every request regardless of task.

## Correct Pattern: Hierarchical

```markdown
# Project

## Build
npm run build

## Conventions

- TypeScript: docs/TYPESCRIPT.md
- Testing: docs/TESTING.md
- Components: docs/COMPONENTS.md
- API: docs/API.md
```

Now only ~20 lines load initially. Agent loads specific files as needed.

## Monorepo Application

```
repo/
├── CLAUDE.md              # Root: 50 lines
├── docs/
│   ├── CONVENTIONS.md     # Shared: 100 lines
│   └── ARCHITECTURE.md    # Shared: 80 lines
└── packages/
    ├── api/
    │   └── CLAUDE.md      # Package: 40 lines
    └── web/
        └── CLAUDE.md      # Package: 40 lines
```

Working in `packages/api/` loads:
- `packages/api/CLAUDE.md` (40 lines)
- Relevant root context as needed

Not the entire documentation tree.
