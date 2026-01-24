---
name: tasklist-conventions
description: This skill documents conventions for using the built-in TaskList tools (TaskCreate, TaskUpdate, TaskList, TaskGet) for tracking execution progress within and across Claude Code sessions.
---

# TaskList Conventions

## Overview

TaskList is a built-in Claude Code feature for tracking task execution. Tasks are stored in `~/.claude/tasks/[session-uuid]/` and can be shared across sessions using the `import-tasks` skill.

This skill documents conventions for using TaskList tools effectively. For importing tasks from another session, see the `import-tasks` skill.

## When to Use TaskList

**Use TaskList when:**
- Executing a plan with multiple steps
- Tracking dependencies between work items
- Coordinating work across multiple sessions or subagents
- Progress needs to be visible and trackable
- Work items have clear completion criteria

**Consider file-todos instead when:**
- Findings need detailed documentation (Problem Statement, Findings, Solutions)
- Work items need to be committed to the repository
- Team visibility is important
- Rich context with work logs is needed

**Use both when:**
- Review findings need documentation (file-todos) AND execution tracking (TaskList)
- Plan implementation needs progress tracking AND permanent record

## Built-in Tools

| Tool | Purpose |
|------|---------|
| `TaskCreate` | Create a new task with subject, description, activeForm |
| `TaskUpdate` | Update status, add dependencies, modify tasks |
| `TaskList` | View all tasks with status and blockers |
| `TaskGet` | Get full details of a specific task |

## Task Fields

**Required fields:**
- `subject`: Brief, actionable title in imperative form ("Implement user model")
- `description`: Detailed description of what needs to be done

**Recommended fields:**
- `activeForm`: Present continuous form shown in spinner ("Implementing user model")

**Set via TaskUpdate:**
- `status`: `pending` → `in_progress` → `completed`
- `addBlockedBy`: Task IDs that must complete before this task
- `addBlocks`: Task IDs that this task blocks

## Conventions

### Task Subjects

Use imperative form (like git commits):
- ✅ "Implement user authentication"
- ✅ "Add validation for email field"
- ✅ "Write integration tests"
- ❌ "Implementing authentication" (use for activeForm)
- ❌ "User auth" (too vague)

### ActiveForm

Use present continuous for progress visibility:
- Subject: "Run database migrations"
- ActiveForm: "Running database migrations"

### Status Workflow

```
pending → in_progress → completed
```

- `pending`: Task created, not yet started
- `in_progress`: Currently being worked on
- `completed`: Work finished and verified

### Dependencies

Set dependencies when tasks must complete in order:

```
TaskCreate: "Implement User model" → #1
TaskCreate: "Add authentication service" → #2
TaskCreate: "Write integration tests" → #3

TaskUpdate: #2 addBlockedBy [#1]  # Service needs model
TaskUpdate: #3 addBlockedBy [#1, #2]  # Tests need both
```

### Task Granularity

Good tasks are:
- Completable in a focused session (1-4 hours of work)
- Specific enough to know when done
- Independent or with clear dependencies
- Verifiable (you can confirm completion)

Examples:
- ✅ "Implement UserService.authenticate method"
- ✅ "Add unit tests for password validation"
- ❌ "Do the backend" (too vague)
- ❌ "Fix everything" (not specific)

## Creating Tasks from a Plan

When executing a plan, create tasks for each major work item:

```
# From plan acceptance criteria:
# - [ ] User model with email, password_hash
# - [ ] Authentication service with JWT
# - [ ] Login/logout endpoints
# - [ ] Integration tests

TaskCreate:
  subject: "Implement User model"
  description: "Create User model with email, password_hash fields. Add validations and password hashing."
  activeForm: "Implementing User model"

TaskCreate:
  subject: "Add authentication service"
  description: "Create AuthService with JWT token generation. Implement authenticate() and verify() methods."
  activeForm: "Adding authentication service"

# Set dependency - service needs model
TaskUpdate: #2 addBlockedBy [#1]
```

## Creating Tasks from Review Findings

When review findings need execution tracking:

```
# From synthesized review findings:
# - P1: SQL injection in search endpoint
# - P2: N+1 query in user listing
# - P3: Unused import in helpers

TaskCreate:
  subject: "Fix SQL injection in search endpoint"
  description: "Parameterize query in SearchController#index. See todos/001-pending-p1-sql-injection.md"
  activeForm: "Fixing SQL injection vulnerability"

TaskCreate:
  subject: "Resolve N+1 query in user listing"
  description: "Add includes(:posts) to User.all query. See todos/002-pending-p2-n-plus-one.md"
  activeForm: "Resolving N+1 query"
```

Link tasks to file-todos for full context.

## Execution Loop

Standard pattern for working through tasks:

```
while TaskList shows pending tasks:
  # 1. Check available work
  TaskList  # Shows tasks with status and blockers

  # 2. Claim next unblocked task
  TaskUpdate: #X status=in_progress

  # 3. Execute the work
  # ... implementation ...

  # 4. Mark complete
  TaskUpdate: #X status=completed
```

## Cross-Session Coordination

### Getting TaskList ID

After creating tasks, get the session UUID:

```bash
task_list_id=$(ls -t ~/.claude/tasks/ | head -1)
echo "TaskList ID: $task_list_id"
```

### Including in Plan Files

Add to YAML frontmatter for later import:

```yaml
---
title: Add user authentication
type: feat
date: 2026-01-24
task_list_id: a69ce44f-1559-4052-89e2-66605323adca
---
```

### Importing in Another Session

Use the `import-tasks` skill:

```
skill: import-tasks a69ce44f-1559-4052-89e2-66605323adca
```

### Parallel Subagent Execution

Multiple agents can work on the same TaskList:

```
# Main session creates tasks
TaskCreate: "Task A" → #1
TaskCreate: "Task B" → #2
TaskCreate: "Task C" → #3

# Get TaskList ID
task_list_id=$(ls -t ~/.claude/tasks/ | head -1)

# Spawn subagents
Task(python-coder): "Import tasks from $task_list_id, work on #1"
Task(python-coder): "Import tasks from $task_list_id, work on #2"
```

Subagents:
1. Import using `skill: import-tasks [id]`
2. Claim tasks with `TaskUpdate: status=in_progress`
3. Complete and mark `status=completed`

## Relationship to Other Systems

| System | Storage | Purpose | Persistence |
|--------|---------|---------|-------------|
| **TaskList** (this) | `~/.claude/tasks/` | Execution tracking | Session-scoped |
| **file-todos** | `todos/` in repo | Detailed documentation | Git-committed |
| **TodoWrite tool** | In-memory | Temporary tracking | None |

**Recommended combination:**
- Use file-todos for detailed findings with Problem Statement, Solutions, Work Log
- Use TaskList for execution tracking with dependencies and status
- Link them via description references: "See todos/001-pending-p1-issue.md"
