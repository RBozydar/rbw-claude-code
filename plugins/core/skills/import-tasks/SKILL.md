---
name: import-tasks
description: This skill should be used when importing tasks from another Claude Code session's TaskList into the current session, enabling coordination across sessions without restarting.
argument-hint: "[TaskList ID (UUID)]"
---

# Import Tasks from Another Session

Import tasks from another Claude Code session's TaskList into the current session.

## When to Use

- Picking up work from a `/workflows:plan` that created tasks
- Coordinating with another Claude session
- Continuing work started in a different session
- Enabling a subagent to work on tasks from the main session

## How It Works

Each Claude Code session has its own TaskList stored at:
```
~/.claude/tasks/[session-uuid]/
├── 1.json
├── 2.json
└── ...
```

This skill reads tasks from another session and recreates them in the current session using TaskCreate, preserving descriptions, status, and dependencies.

## Execution Steps

### 1. Validate the TaskList exists

```bash
task_list_id="$ARGUMENTS"

if [ -z "$task_list_id" ]; then
  echo "Error: No TaskList ID provided"
  echo "Usage: skill import-tasks [TaskList ID]"
  exit 1
fi

if [ ! -d ~/.claude/tasks/$task_list_id ]; then
  echo "Error: TaskList not found at ~/.claude/tasks/$task_list_id"
  echo ""
  echo "Available TaskLists:"
  ls -la ~/.claude/tasks/
  exit 1
fi
```

### 2. Read and display tasks from source

```bash
echo "Tasks in source TaskList $task_list_id:"
echo ""
for f in ~/.claude/tasks/$task_list_id/*.json; do
  cat "$f" | jq -r '"#\(.id) [\(.status)] \(.subject)"'
done
```

### 3. Import tasks into current session

For each task in the source TaskList:

1. Read the task JSON
2. Create in current session via TaskCreate (preserving subject, description, activeForm)
3. Note the ID mapping (source ID to new ID) for dependency resolution
4. After all tasks created, set up dependencies via TaskUpdate with mapped IDs

### 4. Verify and report

Run TaskList to confirm all imported tasks, then report:

```
Imported X tasks from TaskList [source_id]

ID Mapping:
- Source #1 → Current #1: [subject]
- Source #2 → Current #2: [subject]

Ready to execute. Use TaskList to see available work.
```

## Notes

- Tasks are copied, not moved -- source TaskList remains unchanged
- Task IDs in the new session may differ from source (use the mapping)
- Dependencies are automatically remapped to new IDs
- Status is preserved (pending/in_progress/completed)
- If the current session already has tasks, imported tasks get new IDs (no conflicts)
