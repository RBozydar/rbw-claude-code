# conventional-commits

Validate git commit messages follow the conventional commits format.

## What it does

This plugin enforces conventional commit messages using two hooks:

1. **PreToolUse**: Validates `-m` flag content and blocks bypass vectors
2. **PostToolUse**: Defense-in-depth - validates actual commits and auto-reverts invalid ones

### Format

```
type(scope): description
```

Allowed types:
- `feat` - new feature
- `fix` - bug fix
- `docs` - documentation
- `style` - formatting
- `refactor` - code restructuring
- `perf` - performance improvement
- `test` - adding tests
- `build` - build system
- `ci` - CI configuration
- `chore` - maintenance
- `revert` - reverting changes

## Bypass Protection

This plugin blocks known bypass vectors:

| Bypass Vector | Status | Notes |
|---------------|--------|-------|
| `-m "message"` | Validated | Normal path |
| `-F /file` / `--file` | Blocked | Use -m instead |
| `-C commit` / `--reuse-message` | Blocked | Use -m instead |
| `-c commit` / `--reedit-message` | Blocked | Use -m instead |
| `-t file` / `--template` | Blocked | Use -m instead |
| `--no-verify` | Blocked | Cannot skip validation |
| `git commit-tree` | Blocked | Low-level plumbing |
| `bash -c 'git commit ...'` | Validated | Nested shells scanned |
| `eval 'git commit ...'` | Validated | Eval scanned |
| `$(command)` in message | Blocked | No dynamic content |
| `$VAR` in message | Blocked | No dynamic content |
| Heredocs (`<< EOF`) | Blocked | Use -m instead |

### Auto-generated Messages

These are allowed without conventional format:
- Merge commits (`Merge branch ...`)
- Revert commits (`Revert "..."`)
- Fixup commits (`fixup! ...`)
- Squash commits (`squash! ...`)

### Defense in Depth

If a non-conventional commit somehow gets through (e.g., via an unforeseen bypass), the PostToolUse hook will:
1. Detect the invalid commit message
2. Automatically revert it (`git reset --soft HEAD~1`)
3. Preserve your staged changes
4. Report the error

## Installation

```bash
/plugin install conventional-commits
```

## Example

```bash
# Blocked - invalid format
git commit -m "fixed the bug"

# Blocked - bypass attempt
git commit -F /tmp/msg.txt
git commit --no-verify -m "bad"

# Allowed
git commit -m "fix: resolve null pointer in user service"
git commit -m "feat(auth): add OAuth2 support"
git commit -m "feat!: breaking change to API"
```
