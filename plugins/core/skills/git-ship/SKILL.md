---
name: git-ship
description: This skill should be used when automating the complete git workflow -- committing, pushing, creating PRs, waiting for CI, fetching results, and merging. It handles shipping changes with conventional commits and structured PR descriptions.
---

# Git Ship

Automate the complete git workflow from commit to merged PR.

## Commands

| Command | Description |
|---------|-------------|
| `ship` | Commit, push, create PR, wait for CI, fetch results |
| `ship full` | Full workflow including merge after CI passes |
| `ship commit` | Review changes and create conventional commit |
| `ship pr` | Push branch and create PR |
| `ship wait` | Wait for CI checks on current PR |
| `ship status` | Fetch CI status and PR comments |
| `ship merge` | Merge PR with strategy selection and cleanup |

## When to Use Which

- **Standard changes:** `ship` -- commits, pushes, creates PR, waits for CI
- **Ready to merge:** `ship full` -- does everything including merge
- **Just commit:** `ship commit` -- when not ready to push yet
- **Check progress:** `ship status` -- after creating a PR

## Prerequisites

- Git repository with remote configured
- GitHub CLI (`gh`) installed and authenticated
- Feature branch (not main/master)

## Usage

```bash
# Standard workflow
bash ${CLAUDE_PLUGIN_ROOT}/skills/git-ship/scripts/ship.sh ship

# Full workflow with merge
bash ${CLAUDE_PLUGIN_ROOT}/skills/git-ship/scripts/ship.sh full --merge squash

# With plan reference for better PR descriptions
bash ${CLAUDE_PLUGIN_ROOT}/skills/git-ship/scripts/ship.sh ship --plan plans/my-feature.md

# Custom CI wait time
bash ${CLAUDE_PLUGIN_ROOT}/skills/git-ship/scripts/ship.sh ship --wait 10m
```

### Merge Strategies

```bash
# Squash and merge (default, recommended)
bash ${CLAUDE_PLUGIN_ROOT}/skills/git-ship/scripts/ship.sh merge --strategy squash

# Create merge commit
bash ${CLAUDE_PLUGIN_ROOT}/skills/git-ship/scripts/ship.sh merge --strategy merge

# Rebase and merge
bash ${CLAUDE_PLUGIN_ROOT}/skills/git-ship/scripts/ship.sh merge --strategy rebase

# Auto-merge (for repos with branch protection)
bash ${CLAUDE_PLUGIN_ROOT}/skills/git-ship/scripts/ship.sh merge --auto-merge --strategy squash
```

## CI Wait Exit Codes

- `0` -- all checks passed
- `1` -- checks failed
- `2` -- timeout

## Integration

- `/workflows:work` -- used in Phase 4 (Ship It)
- `conventional-commits` hook -- validates commit format
- `pr-comment-resolver` agent -- resolves PR feedback
- `git-worktree` skill -- for parallel development
