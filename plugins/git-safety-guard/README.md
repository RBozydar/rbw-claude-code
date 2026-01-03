# Git Safety Guard Plugin

Prevents Claude from executing destructive git commands that could result in data loss.

## What it blocks

| Command | Reason |
|---------|--------|
| `git checkout -- <files>` | Discards uncommitted changes |
| `git restore <files>` | Overwrites working directory |
| `git reset --hard` | Destroys uncommitted work |
| `git reset --merge` | Can lose changes |
| `git clean -f` | Deletes untracked files |
| `git push --force` | Destroys remote history |
| `git push --delete` | Removes remote refs |
| `git branch -D` | Force-deletes branches |
| `git stash drop/clear` | Deletes saved work |
| `git reflog expire/delete` | Removes recovery safety net |
| `git filter-branch` | Rewrites history |
| `git gc --prune=now` | Removes unreferenced objects |

## What it allows

- `git checkout -b <branch>` - Creating branches
- `git restore --staged` - Unstaging files
- `git clean -n` / `--dry-run` - Preview mode
- `git push --force-with-lease` - Safer force push

## Installation

```bash
claude plugin add ./plugins/git-safety-guard
```

## Why?

After incidents where Claude executed `git checkout --` on multiple files, erasing hours of uncommitted work, this mechanical enforcement prevents accidents that instructions alone cannot.

## Requirements

- cchooks library (installed automatically via uv)
