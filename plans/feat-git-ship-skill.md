# feat: Add git-ship Skill for Complete Git Workflow Automation

**Date:** 2025-01-01
**Type:** Enhancement
**Status:** Draft

## Overview

Create a `git-ship` skill that automates the complete git workflow: reviewing changes, writing good commits with conventional format, pushing to remote, creating PRs with structured descriptions, waiting for CI, fetching CI status and PR comments, and handling merges.

## Problem Statement / Motivation

Currently, the git workflow is manual and fragmented across multiple steps:
1. Reviewing changes with `git diff`
2. Writing commit messages (often inconsistent)
3. Pushing to remote
4. Creating PRs with proper descriptions
5. Waiting for CI to complete
6. Checking CI status and PR comments
7. Merging PRs and cleaning up branches

This is error-prone and time-consuming. A unified skill can:
- Ensure consistent conventional commit format
- Generate high-quality PR descriptions based on changes
- Automate CI waiting with proper timeout handling
- Surface CI failures and PR comments for action
- Handle merges with proper strategy selection
- Clean up branches after successful merges

**Why a Skill (not Agent):**
- Multi-step workflow requiring scripts (like `git-worktree`)
- Needs a bash script for CI polling and merge logic
- Can include templates for commits/PRs
- Integrates with existing `/workflows:work` flow

## Proposed Solution

Create `plugins/core/skills/git-ship/` with:
1. `SKILL.md` - Main skill definition with workflow steps
2. `scripts/ship.sh` - Bash script for the complete workflow
3. `templates/` - Commit and PR templates

### Workflow Steps

```
1. Review Changes
   └── git diff, git status, summarize changes

2. Write Commit
   └── Analyze changes → Generate conventional commit message
   └── Present for user approval/edit
   └── Execute commit

3. Push to Remote
   └── git push -u origin <branch>
   └── Handle push failures gracefully

4. Create PR
   └── Generate PR description from commits and plan
   └── gh pr create with structured body
   └── Return PR URL

5. Wait for CI (configurable, default 8 minutes)
   └── gh pr checks --watch with timeout
   └── Handle timeout, success, failure states

6. Fetch Results
   └── CI status and logs for failures
   └── PR comments and review requests
   └── Present actionable summary

7. Merge (optional)
   └── Choose merge strategy (squash, merge, rebase)
   └── Auto-merge when checks pass
   └── Handle merge conflicts
   └── Delete remote branch after merge
   └── Clean up local branch
```

## Technical Approach

### File Structure

```
plugins/core/skills/git-ship/
├── SKILL.md                    # Main skill definition
├── scripts/
│   └── ship.sh                 # Complete workflow script
└── templates/
    ├── commit-template.md      # Commit message template
    └── pr-template.md          # PR description template
```

### SKILL.md Structure

```markdown
---
name: git-ship
description: Complete git workflow automation - commit, push, create PR, wait for CI, fetch results, merge
tools: Bash, Read, Glob
---

# Git Ship Skill

Automate the complete git workflow from commit to merged PR.

## Commands

| Command | Description |
|---------|-------------|
| `ship` | Full workflow: commit → push → PR → wait → results |
| `ship commit` | Just create a good commit |
| `ship pr` | Push and create PR only |
| `ship wait` | Wait for CI on current PR |
| `ship status` | Fetch CI status and PR comments |
| `ship merge` | Merge PR with cleanup |
| `ship full` | Full workflow including merge |

## Usage

### Full Workflow (without merge)
skill: git-ship
args: "ship"

### Full Workflow (with auto-merge)
skill: git-ship
args: "ship full --merge squash"

### With Plan Reference
skill: git-ship
args: "ship --plan plans/my-feature.md"

### Custom CI Wait Time
skill: git-ship
args: "ship --wait 10m"

### Merge Strategies
skill: git-ship
args: "ship merge --strategy squash"  # Squash and merge (default)
args: "ship merge --strategy merge"   # Create merge commit
args: "ship merge --strategy rebase"  # Rebase and merge

## Process

### 1. Review Changes
[Instructions for reviewing staged/unstaged changes]

### 2. Generate Commit Message
[Instructions for analyzing changes and generating conventional commit]

### 3. Push and Create PR
[Instructions for pushing and creating PR with good description]

### 4. Wait for CI
[Instructions for CI monitoring with timeout]

### 5. Fetch Results
[Instructions for fetching and presenting results]

### 6. Merge PR
[Instructions for merging with strategy selection and cleanup]
```

### scripts/ship.sh

```bash
#!/bin/bash
set -euo pipefail

# Configuration
DEFAULT_WAIT_MINUTES=8
POLL_INTERVAL=30
DEFAULT_MERGE_STRATEGY="squash"

# Parse arguments
ACTION="${1:-ship}"
PLAN_FILE=""
WAIT_MINUTES=$DEFAULT_WAIT_MINUTES
MERGE_STRATEGY=$DEFAULT_MERGE_STRATEGY
AUTO_MERGE=false
DELETE_BRANCH=true

while [[ $# -gt 0 ]]; do
    case $1 in
        --plan) PLAN_FILE="$2"; shift 2 ;;
        --wait) WAIT_MINUTES="${2%m}"; shift 2 ;;
        --merge) MERGE_STRATEGY="$2"; shift 2 ;;
        --strategy) MERGE_STRATEGY="$2"; shift 2 ;;
        --auto-merge) AUTO_MERGE=true; shift ;;
        --no-delete-branch) DELETE_BRANCH=false; shift ;;
        ship|commit|pr|wait|status|merge|full) ACTION="$1"; shift ;;
        *) shift ;;
    esac
done

# Functions
check_branch() {
    BRANCH=$(git branch --show-current)
    if [[ "$BRANCH" == "main" || "$BRANCH" == "master" ]]; then
        echo "Error: Cannot ship from $BRANCH. Create a feature branch first."
        exit 1
    fi
    echo "$BRANCH"
}

get_main_branch() {
    if git show-ref --verify --quiet refs/heads/main; then
        echo "main"
    elif git show-ref --verify --quiet refs/heads/master; then
        echo "master"
    else
        echo "main"  # Default assumption
    fi
}

review_changes() {
    echo "=== Staged Changes ==="
    git diff --cached --stat
    echo ""
    echo "=== Unstaged Changes ==="
    git diff --stat
    echo ""
    echo "=== Untracked Files ==="
    git status --porcelain | grep "^??" || true
}

wait_for_ci() {
    local pr_number=$1
    local timeout=$((WAIT_MINUTES * 60))

    echo "Waiting up to ${WAIT_MINUTES} minutes for CI..."

    if timeout "$timeout" gh pr checks "$pr_number" --watch --fail-fast; then
        echo "✓ All CI checks passed!"
        return 0
    else
        local exit_code=$?
        if [[ $exit_code -eq 124 ]]; then
            echo "⏱ Timeout waiting for CI after ${WAIT_MINUTES} minutes"
            return 2
        else
            echo "✗ CI checks failed"
            return 1
        fi
    fi
}

fetch_status() {
    local pr_number=$1

    echo "=== CI Status ==="
    gh pr checks "$pr_number" --json name,state,conclusion 2>/dev/null || echo "No checks found"

    echo ""
    echo "=== PR Comments ==="
    gh pr view "$pr_number" --json comments --jq '.comments[] | "[\(.author.login)] \(.body | split("\n")[0])"' 2>/dev/null || echo "No comments"

    echo ""
    echo "=== Review Status ==="
    gh pr view "$pr_number" --json reviews --jq '.reviews[] | "[\(.author.login)] \(.state)"' 2>/dev/null || echo "No reviews"
}

merge_pr() {
    local pr_number=$1
    local strategy=$2
    local delete_branch=$3

    echo "=== Merging PR #$pr_number ==="
    echo "Strategy: $strategy"

    # Check if PR is mergeable
    local mergeable
    mergeable=$(gh pr view "$pr_number" --json mergeable --jq '.mergeable')

    if [[ "$mergeable" == "CONFLICTING" ]]; then
        echo "✗ Error: PR has merge conflicts"
        echo ""
        echo "To resolve:"
        echo "1. git fetch origin"
        echo "2. git rebase origin/$(get_main_branch)"
        echo "3. Resolve conflicts"
        echo "4. git push --force-with-lease"
        return 1
    fi

    if [[ "$mergeable" == "UNKNOWN" ]]; then
        echo "⚠ Merge status unknown. Attempting merge anyway..."
    fi

    # Perform merge
    local merge_args="--$strategy"
    if [[ "$delete_branch" == "true" ]]; then
        merge_args="$merge_args --delete-branch"
    fi

    if gh pr merge "$pr_number" $merge_args; then
        echo "✓ PR merged successfully!"

        # Clean up local branch
        local branch
        branch=$(git branch --show-current)
        local main_branch
        main_branch=$(get_main_branch)

        if [[ "$branch" != "$main_branch" ]]; then
            echo ""
            echo "=== Cleaning up local branch ==="
            git checkout "$main_branch"
            git pull origin "$main_branch"
            git branch -d "$branch" 2>/dev/null || echo "Note: Local branch already deleted or has unmerged changes"
            echo "✓ Switched to $main_branch and cleaned up"
        fi

        return 0
    else
        echo "✗ Merge failed"
        return 1
    fi
}

enable_auto_merge() {
    local pr_number=$1
    local strategy=$2

    echo "=== Enabling Auto-Merge ==="
    if gh pr merge "$pr_number" --auto --"$strategy"; then
        echo "✓ Auto-merge enabled. PR will merge when all checks pass."
        return 0
    else
        echo "✗ Failed to enable auto-merge"
        echo "Note: Auto-merge requires branch protection rules to be configured"
        return 1
    fi
}

# Main execution based on action
case $ACTION in
    commit)
        review_changes
        echo "Ready to commit. Claude should generate the commit message."
        ;;
    pr)
        BRANCH=$(check_branch)
        git push -u origin "$BRANCH"
        echo "Ready to create PR. Claude should generate the PR description."
        ;;
    wait)
        PR_NUMBER=$(gh pr view --json number --jq '.number' 2>/dev/null)
        if [[ -z "$PR_NUMBER" ]]; then
            echo "Error: No PR found for current branch"
            exit 1
        fi
        wait_for_ci "$PR_NUMBER"
        ;;
    status)
        PR_NUMBER=$(gh pr view --json number --jq '.number' 2>/dev/null)
        if [[ -z "$PR_NUMBER" ]]; then
            echo "Error: No PR found for current branch"
            exit 1
        fi
        fetch_status "$PR_NUMBER"
        ;;
    merge)
        PR_NUMBER=$(gh pr view --json number --jq '.number' 2>/dev/null)
        if [[ -z "$PR_NUMBER" ]]; then
            echo "Error: No PR found for current branch"
            exit 1
        fi

        if [[ "$AUTO_MERGE" == "true" ]]; then
            enable_auto_merge "$PR_NUMBER" "$MERGE_STRATEGY"
        else
            merge_pr "$PR_NUMBER" "$MERGE_STRATEGY" "$DELETE_BRANCH"
        fi
        ;;
    full)
        # Full workflow including merge
        BRANCH=$(check_branch)
        review_changes
        echo ""
        echo "=== Full Ship Workflow ==="
        echo "Branch: $BRANCH"
        echo "Plan: ${PLAN_FILE:-none}"
        echo "CI Wait: ${WAIT_MINUTES} minutes"
        echo "Merge Strategy: $MERGE_STRATEGY"
        echo "Auto-Merge: $AUTO_MERGE"
        echo ""
        echo "Claude should now:"
        echo "1. Generate commit message based on changes"
        echo "2. Execute commit"
        echo "3. Push to origin"
        echo "4. Create PR with description"
        echo "5. Wait for CI (or enable auto-merge)"
        echo "6. Merge PR and cleanup"
        echo "7. Report results"
        ;;
    ship)
        BRANCH=$(check_branch)
        review_changes
        echo ""
        echo "=== Ship Workflow ==="
        echo "Branch: $BRANCH"
        echo "Plan: ${PLAN_FILE:-none}"
        echo "CI Wait: ${WAIT_MINUTES} minutes"
        echo ""
        echo "Claude should now:"
        echo "1. Generate commit message based on changes"
        echo "2. Execute commit"
        echo "3. Push to origin"
        echo "4. Create PR with description"
        echo "5. Wait for CI"
        echo "6. Report results"
        echo ""
        echo "To also merge, use: ship full --merge squash"
        ;;
esac
```

### Integration with /workflows:work

Update `plugins/core/commands/workflows/work.md` Phase 4 to reference the skill:

```markdown
### Phase 4: Ship It

Use the `git-ship` skill for the complete workflow:

skill: git-ship
args: "ship --plan [plan-file]"

Or for full workflow with merge:
skill: git-ship
args: "ship full --merge squash"

Or manually:
1. Create Commit (see git-ship skill for format)
2. Create Pull Request (see git-ship skill for format)
3. Wait for CI
4. Merge (optional)
5. Notify User
```

## Acceptance Criteria

### Functional Requirements

- [ ] Skill created at `plugins/core/skills/git-ship/SKILL.md`
- [ ] Script created at `plugins/core/skills/git-ship/scripts/ship.sh`
- [ ] Script is executable and handles all workflow steps
- [ ] Conventional commit format enforced
- [ ] PR description includes Summary, Testing, Related sections
- [ ] CI waiting with configurable timeout (default 8 minutes)
- [ ] Graceful handling of CI timeout, success, failure
- [ ] Fetches and displays PR comments and review status
- [ ] Merge with strategy selection (squash, merge, rebase)
- [ ] Auto-merge option for repos with branch protection
- [ ] Merge conflict detection with resolution instructions
- [ ] Branch cleanup after successful merge (remote and local)

### Non-Functional Requirements

- [ ] Clear error messages for all failure modes
- [ ] Works with any GitHub repo using gh CLI
- [ ] No secrets or credentials in scripts
- [ ] Integrates with existing conventional-commits hook

### Quality Gates

- [ ] Plugin validation passes: `claude plugin validate .`
- [ ] Script runs without errors in test repo
- [ ] All gh CLI commands work correctly
- [ ] Merge workflow tested with all strategies

## Implementation Phases

### Phase 1: Core Skill Creation

**Tasks:**
1. Create `plugins/core/skills/git-ship/SKILL.md`
   - YAML frontmatter with name, description, tools
   - Commands table (ship, commit, pr, wait, status, merge, full)
   - Detailed process sections
   - Output format for each step

2. Create `plugins/core/skills/git-ship/scripts/ship.sh`
   - Argument parsing
   - All workflow functions including merge
   - Error handling

3. Create `plugins/core/skills/git-ship/templates/`
   - `commit-template.md` - Conventional commit format
   - `pr-template.md` - Structured PR description

### Phase 2: Integration

**Tasks:**
1. Update `plugins/core/commands/workflows/work.md`
   - Reference git-ship skill in Phase 4

2. Update `plugins/core/README.md`
   - Add git-ship to skills table

### Phase 3: Testing

**Tasks:**
1. Manual testing
   - Full ship workflow (without merge)
   - Full workflow with merge (all strategies)
   - Individual commands (commit, pr, wait, status, merge)
   - Error cases (no changes, CI timeout, push failure, merge conflicts)
   - Auto-merge functionality

2. Validate plugin: `claude plugin validate .`

## Dependencies & Prerequisites

### Required
- GitHub CLI (`gh`) installed and authenticated
- Git repository with remote configured
- Conventional commits hook (already exists)

### Optional
- Plan file for context-aware PR descriptions
- Branch protection rules (for auto-merge)

## Risk Analysis & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| gh CLI not installed | Medium | High | Check on startup, clear error message |
| CI timeout too short | Medium | Low | Configurable wait time, reasonable default |
| Push failures (auth, conflicts) | Low | Medium | Clear error messages, suggest resolution |
| Merge conflicts | Medium | Medium | Detect and provide resolution instructions |
| Auto-merge not available | Medium | Low | Fallback to manual merge, clear message |
| No PR comments to fetch | Low | Low | Graceful "no comments" message |

## References

### Internal References
- `plugins/core/skills/git-worktree/SKILL.md:1-303` - Similar skill pattern
- `plugins/core/commands/workflows/work.md:166-209` - Current commit/PR pattern
- `plugins/conventional-commits/hooks/conventional_commits.py:1-42` - Commit validation
- `plugins/core/agents/workflow/pr-comment-resolver.md:1-68` - PR comment handling

### External References
- [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)
- [gh pr create](https://cli.github.com/manual/gh_pr_create)
- [gh pr checks](https://cli.github.com/manual/gh_pr_checks)
- [gh pr view](https://cli.github.com/manual/gh_pr_view)
- [gh pr merge](https://cli.github.com/manual/gh_pr_merge)

## MVP Implementation

### `plugins/core/skills/git-ship/SKILL.md`

```markdown
---
name: git-ship
description: Complete git workflow automation - commit, push, create PR, wait for CI, fetch results, merge. Use when you need to ship changes with proper commits and PR descriptions.
tools: Bash, Read, Glob, Grep
---

# Git Ship Skill

Automate the complete git workflow from commit to merged PR.

## Commands

| Command | Description |
|---------|-------------|
| `ship` | Workflow: commit → push → PR → CI wait → results |
| `ship full` | Full workflow including merge after CI passes |
| `ship commit` | Review changes and create conventional commit |
| `ship pr` | Push branch and create PR with good description |
| `ship wait` | Wait for CI checks on current PR |
| `ship status` | Fetch CI status and PR comments |
| `ship merge` | Merge PR with strategy selection and cleanup |

## Prerequisites

- Git repository with remote configured
- GitHub CLI (`gh`) installed and authenticated
- Feature branch (not main/master)

## Usage

### Standard Ship Workflow

```
skill: git-ship
args: "ship"
```

### Full Workflow with Merge

```
skill: git-ship
args: "ship full --merge squash"
```

### With Plan Reference (better PR descriptions)

```
skill: git-ship
args: "ship --plan plans/my-feature.md"
```

### Custom CI Wait Time

```
skill: git-ship
args: "ship --wait 10m"
```

### Merge Strategies

```
skill: git-ship
args: "ship merge --strategy squash"   # Squash and merge (default)
args: "ship merge --strategy merge"    # Create merge commit
args: "ship merge --strategy rebase"   # Rebase and merge
```

### Auto-Merge (for repos with branch protection)

```
skill: git-ship
args: "ship merge --auto-merge --strategy squash"
```

## Process

### 1. Review Changes

First, understand what's being shipped:

```bash
# Run the ship script to review
./scripts/ship.sh commit
```

Analyze:
- Staged vs unstaged changes
- Files modified, added, deleted
- Logical grouping of changes

### 2. Generate Commit Message

Based on the changes, generate a conventional commit message:

```
<type>(<scope>): <description>

<body>

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Types:** feat, fix, docs, style, refactor, perf, test, build, ci, chore

**Guidelines:**
- Use imperative mood: "add" not "added"
- Keep subject under 50 characters
- Body explains "why" not "what"
- Reference issues if applicable

**Execute:**
```bash
git add .
git commit -m "$(cat <<'EOF'
feat(module): add new capability

Detailed explanation of why this change was made.

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

### 3. Push and Create PR

```bash
# Push branch
BRANCH=$(git branch --show-current)
git push -u origin "$BRANCH"

# Create PR with structured description
gh pr create --title "feat(module): add new capability" --body "$(cat <<'EOF'
## Summary
- What was changed
- Why it was needed
- Key decisions made

## Type of Change
- [x] New feature

## Testing
- Tests added/modified
- Manual testing performed

## Related Issues
Closes #123

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

### 4. Wait for CI

```bash
# Wait with default timeout (8 minutes)
./scripts/ship.sh wait

# Or with custom timeout
./scripts/ship.sh wait --wait 10m
```

**Exit codes:**
- `0` - All checks passed
- `1` - Checks failed
- `2` - Timeout

### 5. Fetch Results

```bash
./scripts/ship.sh status
```

Reports:
- CI check status (passed/failed/pending)
- PR comments
- Review status (approved/changes requested/pending)

### 6. Merge PR

```bash
# Squash and merge (default, recommended)
./scripts/ship.sh merge --strategy squash

# Create merge commit
./scripts/ship.sh merge --strategy merge

# Rebase and merge
./scripts/ship.sh merge --strategy rebase

# Enable auto-merge (for branch protection)
./scripts/ship.sh merge --auto-merge --strategy squash
```

**What happens on merge:**
1. Checks if PR is mergeable (no conflicts)
2. Merges with selected strategy
3. Deletes remote branch (unless --no-delete-branch)
4. Switches to main/master locally
5. Pulls latest changes
6. Deletes local feature branch

## Output Format

### After Ship Complete

```markdown
## Ship Results

**PR:** #123 - https://github.com/org/repo/pull/123
**Branch:** feature/my-feature

### Commit
feat(module): add new capability

### CI Status
✓ build (passed)
✓ test (passed)
✓ lint (passed)

### Reviews
- @reviewer1: APPROVED
- @reviewer2: CHANGES_REQUESTED

### Comments
- [@reviewer2] Please fix the typo on line 42

### Next Steps
- [ ] Address review comments
- [ ] Re-request review after fixes
```

### After Merge Complete

```markdown
## Merge Results

**PR:** #123 - MERGED
**Strategy:** squash
**Branch:** feature/my-feature → deleted

### Cleanup
✓ Remote branch deleted
✓ Switched to main
✓ Pulled latest changes
✓ Local branch deleted

### Summary
Your changes are now on main!
```

## Error Handling

### Not on Feature Branch
```
Error: Cannot ship from main. Create a feature branch first.
Suggestion: git checkout -b feat/my-feature
```

### Push Failed
```
Error: Push failed. Possible causes:
- Remote branch has new commits (git pull --rebase)
- No push access (check permissions)
- Branch protection rules
```

### CI Timeout
```
Warning: CI checks still running after 8 minutes.
Current status:
- build: ✓ passed
- test: ⏳ running (12m elapsed)

Options:
1. Continue waiting: ship wait --wait 15m
2. Check GitHub Actions: gh run view
3. Enable auto-merge: ship merge --auto-merge
```

### Merge Conflicts
```
Error: PR has merge conflicts.

To resolve:
1. git fetch origin
2. git rebase origin/main
3. Resolve conflicts in your editor
4. git add <resolved-files>
5. git rebase --continue
6. git push --force-with-lease
7. ship merge --strategy squash
```

### Auto-Merge Not Available
```
Warning: Auto-merge not available.

Auto-merge requires branch protection rules. Either:
1. Enable branch protection in repo settings
2. Wait for CI manually: ship wait
3. Merge manually: ship merge
```

## Integration

This skill integrates with:
- `/workflows:work` - Used in Phase 4 (Ship It)
- `conventional-commits` hook - Validates commit format
- `pr-comment-resolver` agent - Resolves PR feedback
- `git-worktree` skill - For parallel development
```

### `plugins/core/skills/git-ship/scripts/ship.sh`

See Technical Approach section for full script.
