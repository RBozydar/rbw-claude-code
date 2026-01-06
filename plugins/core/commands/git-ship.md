---
name: git-ship
description: Complete git workflow automation - commit, push, create PR, wait for CI, fetch results, merge
argument-hint: "[ship|full|commit|pr|wait|status|merge]"
---

# Git Ship Command

Automate the complete git workflow from commit to merged PR.

## Skill Reference

Use the git-ship skill for detailed instructions:

```
${PLUGIN_DIR}/skills/git-ship/SKILL.md
```

## Quick Reference

| Argument | Action |
|----------|--------|
| `ship` | Full workflow: commit → push → PR → CI wait → results |
| `full` | Full workflow including merge after CI passes |
| `commit` | Review changes and create conventional commit |
| `pr` | Push branch and create PR with good description |
| `wait` | Wait for CI checks on current PR |
| `status` | Fetch CI status and PR comments |
| `merge` | Merge PR with strategy selection and cleanup |

## Argument

<argument> #$ARGUMENTS </argument>

## Execution

1. Read the full skill instructions from the skill file above
2. Execute the requested workflow step based on the argument
3. If no argument provided, run the default `ship` workflow
