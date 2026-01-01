# conventional-commits

Validate git commit messages follow the conventional commits format.

## What it does

This PreToolUse hook checks commit messages and blocks commits that don't follow the format:

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

## Installation

```bash
/plugin install conventional-commits
```

## Example

```bash
# Blocked
git commit -m "fixed the bug"

# Allowed
git commit -m "fix: resolve null pointer in user service"
git commit -m "feat(auth): add OAuth2 support"
```
