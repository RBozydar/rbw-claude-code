---
name: file-todos
description: This skill should be used when managing the file-based todo tracking system in the todos/ directory. It provides workflows for creating todos, managing status and dependencies, conducting triage, and integrating with slash commands and code review processes.
---

# File-Based Todo Tracking

## Overview

The `todos/` directory contains a file-based tracking system for managing code review feedback, technical debt, feature requests, and work items. Each todo is a markdown file with YAML frontmatter and structured sections.

## File Naming Convention

```
{issue_id}-{status}-{priority}-{description}.md
```

- **issue_id**: Sequential number (001, 002, 003...) -- never reused
- **status**: `pending` (needs triage), `ready` (approved), `complete` (done)
- **priority**: `p1` (critical), `p2` (important), `p3` (nice-to-have)
- **description**: kebab-case, brief description

## File Structure

Each todo is a markdown file with YAML frontmatter and structured sections. Use the template at [todo-template.md](./assets/todo-template.md) as a starting point.

**Required sections:** Problem Statement, Findings, Proposed Solutions, Recommended Action, Acceptance Criteria, Work Log

**Optional sections:** Technical Details, Resources, Notes

**YAML frontmatter fields:**
```yaml
---
status: ready              # pending | ready | complete
priority: p1              # p1 | p2 | p3
issue_id: "002"
tags: [rails, performance, database]
dependencies: ["001"]     # Issue IDs this is blocked by
---
```

## Common Workflows

### Creating a New Todo

1. Determine next issue ID: `ls todos/ | grep -o '^[0-9]\+' | sort -n | tail -1`
2. Copy template: `cp assets/todo-template.md todos/{NEXT_ID}-pending-{priority}-{description}.md`
3. Fill required sections: Problem Statement, Findings, Proposed Solutions, Acceptance Criteria, initial Work Log entry
4. Determine status: `pending` (needs triage) or `ready` (pre-approved)
5. Add relevant tags for filtering

**Create a todo when:** work requires >15 minutes, needs research/planning, has dependencies, requires approval, or is part of a larger effort.

**Act immediately when:** issue is trivial (<15 min), complete context is available, no planning needed, or user requests immediate action.

### Triaging Pending Items

1. List pending items: `ls todos/*-pending-*.md`
2. For each: read Problem Statement and Findings, review Proposed Solutions, decide (approve, defer, or modify priority)
3. Update approved todos: rename file status to `ready`, update frontmatter, fill "Recommended Action" section

Use `/triage` for interactive approval workflow.

### Managing Dependencies

```yaml
dependencies: ["002", "005"]  # Blocked by issues 002 and 005
dependencies: []               # No blockers
```

Check blockers: `grep "^dependencies:" todos/003-*.md`
Find dependents: `grep -l 'dependencies:.*"002"' todos/*.md`

### Updating Work Logs

Always add a work log entry when working on a todo:

```markdown
### YYYY-MM-DD - Session Title

**By:** Claude Code / Developer Name

**Actions:**
- Specific changes made (include file:line references)
- Commands executed, tests run, investigation results

**Learnings:**
- What worked / what didn't, patterns discovered
```

### Completing a Todo

1. Verify all acceptance criteria checked off
2. Update Work Log with final session and results
3. Rename file status to `complete`, update frontmatter
4. Check for unblocked work: `grep -l 'dependencies:.*"002"' todos/*-ready-*.md`

## Integration with Development Workflows

| Trigger | Flow | Tool |
|---------|------|------|
| Code review | `/workflows:review` → Findings → `/triage` → Todos | Review agent + skill |
| PR comments | `/resolve_pr_parallel` → Individual fixes → Todos | gh CLI + skill |
| Code TODOs | `/resolve_todo_parallel` → Fixes + Complex todos | Agent + skill |
| Planning | Brainstorm → Create todo → Work → Complete | Skill |

## Key Distinctions

| System | Storage | Scope | Persistence |
|--------|---------|-------|-------------|
| **File-todos** (this skill) | `todos/*.md` | Project tracking | Disk (permanent) |
| **Rails Todo model** | Database (`app/models/todo.rb`) | User-facing app feature | Database |
| **TodoWrite tool** | In-memory | Single conversation | None |
| **TaskList tools** | `~/.claude/tasks/` | Session execution tracking | Disk (session-scoped) |

**Recommended combination:** File-todos for detailed documentation, TaskList for execution tracking.
