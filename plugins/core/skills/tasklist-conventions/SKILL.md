---
name: tasklist-conventions
description: This skill should be used when working with built-in TaskList tools (TaskCreate, TaskUpdate, TaskList, TaskGet) to track execution progress within and across Claude Code sessions.
---

# TaskList Conventions

## Overview

TaskList is a built-in Claude Code feature for tracking task execution. Tasks are stored in `~/.claude/tasks/[session-uuid]/` and can be shared across sessions using the `import-tasks` skill.

## When to Use TaskList

**Use TaskList when:**
- Executing a plan with multiple steps
- Tracking dependencies between work items
- Coordinating work across sessions or subagents
- Progress needs to be visible and trackable

**Consider file-todos instead when:**
- Findings need detailed documentation (Problem Statement, Findings, Solutions)
- Work items need to be committed to the repository
- Rich context with work logs is needed

**Use both when:**
- Review findings need documentation (file-todos) AND execution tracking (TaskList)

## Built-in Tools

| Tool | Purpose |
|------|---------|
| `TaskCreate` | Create a new task with subject, description, activeForm |
| `TaskUpdate` | Update status, add dependencies, modify tasks |
| `TaskList` | View all tasks with status and blockers |
| `TaskGet` | Get full details of a specific task |

## Task Fields

**Required:** `subject` (imperative form), `description` (detailed scope)

**Recommended:** `activeForm` (present continuous for spinner display)

**Set via TaskUpdate:** `status` (pending/in_progress/completed), `addBlockedBy`, `addBlocks`

## Conventions

### Task Subjects

Use imperative form (like git commits): "Implement user authentication", "Add validation for email field", "Write integration tests"

### ActiveForm

Use present continuous: Subject "Run database migrations" → ActiveForm "Running database migrations"

### Status Workflow

```
pending → in_progress → completed
```

### Dependencies

```
TaskCreate: "Implement User model" → #1
TaskCreate: "Add authentication service" → #2
TaskUpdate: #2 addBlockedBy [#1]
```

### Task Granularity

Create tasks that are completable in a focused session (1-4 hours), specific enough to know when done, independent or with clear dependencies, and verifiable.

## Execution Loop

```
while TaskList shows pending tasks:
  TaskList                              # Check available work
  TaskUpdate: #X status=in_progress     # Claim next unblocked task
  # ... implementation ...
  TaskUpdate: #X status=completed       # Mark complete
```

## Cross-Session Coordination

### Including TaskList ID in Plan Files

```yaml
---
title: Add user authentication
task_list_id: a69ce44f-1559-4052-89e2-66605323adca
---
```

### Importing in Another Session

Use the `import-tasks` skill to import tasks from another session's TaskList.

### Parallel Subagent Execution

Multiple agents can work on the same TaskList by importing it and claiming individual tasks.

## Relationship to Other Systems

| System | Storage | Purpose | Persistence |
|--------|---------|---------|-------------|
| **TaskList** (this) | `~/.claude/tasks/` | Execution tracking | Session-scoped |
| **file-todos** | `todos/` in repo | Detailed documentation | Git-committed |
| **TodoWrite tool** | In-memory | Temporary tracking | None |

**Recommended:** File-todos for detailed findings, TaskList for execution tracking. Link them via description references.
