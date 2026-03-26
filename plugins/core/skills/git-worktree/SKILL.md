---
name: git-worktree
description: This skill should be used when managing Git worktrees for isolated parallel development -- creating, listing, switching between, and cleaning up worktrees with interactive confirmations and automatic .env file copying.
---

# Git Worktree Manager

Manage Git worktrees for isolated parallel development through a unified manager script.

## Critical: Always Use the Manager Script

**Never call `git worktree add` directly.** The manager script handles critical setup that raw git commands miss: copying `.env` files, managing `.gitignore`, and maintaining consistent directory structure.

```bash
# CORRECT
bash ${CLAUDE_PLUGIN_ROOT}/skills/git-worktree/scripts/worktree-manager.sh create feature-name

# WRONG
git worktree add .worktrees/feature-name -b feature-name main
```

## Commands

```bash
SCRIPT="${CLAUDE_PLUGIN_ROOT}/skills/git-worktree/scripts/worktree-manager.sh"

# Create a new worktree (copies .env files automatically)
bash $SCRIPT create <branch-name> [from-branch]

# List all worktrees with status
bash $SCRIPT list

# Switch to an existing worktree
bash $SCRIPT switch <name>

# Copy .env files to an existing worktree
bash $SCRIPT copy-env <name>

# Clean up completed worktrees interactively
bash $SCRIPT cleanup
```

Run `bash $SCRIPT help` for full option details.

## When to Use

1. **Code review** (`/workflows:review`): If not on the PR branch, use a worktree for isolated review
2. **Feature work** (`/workflows:work`): For parallel development alongside other branches
3. **Parallel development**: Working on multiple features simultaneously
4. **Cleanup**: After completing work in a worktree

## Workflow Integration

### With `/workflows:review`

```
1. Check current branch
2. If already on PR branch → stay, no worktree needed
3. If different branch → offer worktree for isolated review
```

### With `/workflows:work`

```
1. Ask: new branch on current worktree, or worktree for parallel work?
2. If parallel → create worktree from main
```

## Troubleshooting

**"Worktree already exists"** -- the script offers to switch to it instead.

**"Cannot remove: current worktree"** -- switch out first: `cd $(git rev-parse --show-toplevel)` then cleanup.

**Missing .env files** -- run `bash $SCRIPT copy-env <name>` to copy them to an existing worktree.

**Lost in a worktree** -- run `bash $SCRIPT list` to see all worktrees and current location.
