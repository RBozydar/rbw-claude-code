# Dangerous Command Guard Hook

A Claude Code PreToolUse hook that blocks dangerous patterns in `find`, `xargs`, `git`, and other commands while allowing safe usage.

## Problem

Commands like `find` and `xargs` are incredibly useful but have dangerous options:
- `find . -delete` can wipe entire directories
- `find . -exec rm {} \;` executes rm on every match
- `cat files | xargs rm` deletes all listed files
- `git push --force` can overwrite remote history

Rather than blocking these commands entirely, this hook inspects the command arguments and blocks only dangerous patterns.

## Installation

1. Save the hook script to your hooks directory:
   ```bash
   mkdir -p ~/.claude/hooks
   # Save dangerous_command_guard.py to ~/.claude/hooks/
   chmod +x ~/.claude/hooks/dangerous_command_guard.py
   ```

2. Register in your global `settings.json` (`~/.claude/settings.json`):
   ```json
   {
     "hooks": {
       "PreToolUse": [
         {
           "matcher": "Bash",
           "hooks": [
             {
               "type": "command",
               "command": "$HOME/.claude/hooks/dangerous_command_guard.py",
               "timeout": 5
             }
           ]
         }
       ]
     }
   }
   ```

3. Add the commands to your allow list (now safe with hook protection):
   ```json
   {
     "permissions": {
       "allow": [
         "Bash(find:*)",
         "Bash(xargs:*)",
         "Bash(git checkout:*)",
         "Bash(git push:*)",
         "Bash(git stash:*)",
         "Bash(git branch:*)",
         "Bash(chmod:*)"
       ]
     }
   }
   ```

## Hook Script

```python
#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["cchooks"]
# ///
"""
Dangerous Command Guard Hook

Blocks dangerous patterns in common commands while allowing safe usage.
This enables adding powerful commands like find/xargs to the allow list
without risking destructive operations.

Author: [Your Name]
Version: 1.0.0
"""

import re
from cchooks import create_context


# =============================================================================
# DANGEROUS PATTERN DEFINITIONS
# =============================================================================

# find: Block file deletion and destructive exec patterns
FIND_DANGEROUS = [
    (r'\s-delete\b', 'find -delete (deletes matched files)'),
    (r'\s-exec\s+rm\b', 'find -exec rm (deletes via exec)'),
    (r'\s-execdir\s+rm\b', 'find -execdir rm (deletes via execdir)'),
    (r'\s-exec\s+shred\b', 'find -exec shred (secure delete)'),
    (r'\s-exec\s+chmod\s+000', 'find -exec chmod 000 (removes all permissions)'),
    (r'\s-exec\s+mv\s+.*\s+/dev/null', 'find -exec mv to /dev/null'),
]

# xargs: Block piping to destructive commands
XARGS_DANGEROUS = [
    (r'\|\s*xargs\s+rm\b', 'xargs rm (deletes files)'),
    (r'\|\s*xargs\s+-[^\s]*\s+rm\b', 'xargs with flags to rm'),
    (r'\|\s*xargs\s+shred\b', 'xargs shred (secure delete)'),
    (r'\|\s*xargs\s+chmod\s+000', 'xargs chmod 000'),
    (r'\|\s*xargs\s+[^|]*\brm\s+-rf\b', 'xargs with rm -rf'),
]

# git: Block destructive git operations
GIT_DANGEROUS = [
    (r'git\s+push\s+.*--force', 'git push --force (overwrites remote)'),
    (r'git\s+push\s+.*-f\b', 'git push -f (overwrites remote)'),
    (r'git\s+push\s+[^\s]+\s+:', 'git push origin :branch (deletes remote branch)'),
    (r'git\s+branch\s+-D\b', 'git branch -D (force delete branch)'),
    (r'git\s+stash\s+drop', 'git stash drop (loses stashed work)'),
    (r'git\s+stash\s+clear', 'git stash clear (loses all stashes)'),
    (r'git\s+checkout\s+--\s+\.', 'git checkout -- . (discards all changes)'),
    (r'git\s+reset\s+--hard', 'git reset --hard (loses commits/changes)'),
    (r'git\s+clean\s+-[^\s]*f', 'git clean -f (deletes untracked files)'),
]

# chmod: Block dangerous permission changes
CHMOD_DANGEROUS = [
    (r'chmod\s+000\s', 'chmod 000 (removes all permissions)'),
    (r'chmod\s+777\s+.*\.ssh', 'chmod 777 on .ssh (security risk)'),
    (r'chmod\s+777\s+.*\.env', 'chmod 777 on .env (security risk)'),
    (r'chmod\s+-R\s+000', 'chmod -R 000 (recursive permission removal)'),
]

# Combine all patterns by command prefix
PATTERNS = {
    'find': FIND_DANGEROUS,
    'xargs': XARGS_DANGEROUS,
    'git': GIT_DANGEROUS,
    'chmod': CHMOD_DANGEROUS,
}


# =============================================================================
# COMMAND CHECKING LOGIC
# =============================================================================

def check_command(command: str) -> tuple[bool, str]:
    """
    Check if command contains dangerous patterns.

    Args:
        command: The full bash command string

    Returns:
        Tuple of (is_safe, reason_if_blocked)
    """
    cmd_lower = command.lower()

    # Check each category of dangerous patterns
    for cmd_prefix, patterns in PATTERNS.items():
        # Only check if the command contains this prefix
        if cmd_prefix not in cmd_lower:
            continue

        for pattern, description in patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return False, f"Blocked: {description}"

    return True, ""


# =============================================================================
# HOOK ENTRY POINT
# =============================================================================

def main() -> None:
    """Main hook entry point."""
    c = create_context()

    # Only check Bash tool calls
    if c.tool_name != "Bash":
        c.output.exit_success()
        return

    # Extract the command from tool input
    command = c.tool_input.get("command", "")

    # Check for dangerous patterns
    is_safe, reason = check_command(command)

    if not is_safe:
        c.output.exit_block(reason)
    else:
        c.output.exit_success()


if __name__ == "__main__":
    main()
```

## What Gets Blocked

### find commands

| Command | Status | Reason |
|---------|--------|--------|
| `find . -name "*.log"` | Allowed | Safe search |
| `find . -type f -mtime +30` | Allowed | Safe search |
| `find . -delete` | **Blocked** | Deletes matched files |
| `find . -exec rm {} \;` | **Blocked** | Deletes via exec |
| `find . -exec rm -rf {} +` | **Blocked** | Recursive delete |
| `find . -execdir rm {} \;` | **Blocked** | Deletes via execdir |

### xargs commands

| Command | Status | Reason |
|---------|--------|--------|
| `ls \| xargs wc -l` | Allowed | Safe operation |
| `find . \| xargs grep pattern` | Allowed | Safe search |
| `cat list.txt \| xargs rm` | **Blocked** | Deletes files |
| `find . \| xargs rm -rf` | **Blocked** | Recursive delete |

### git commands

| Command | Status | Reason |
|---------|--------|--------|
| `git push origin main` | Allowed | Normal push |
| `git push -u origin feature` | Allowed | Set upstream |
| `git push --force` | **Blocked** | Overwrites remote |
| `git push -f origin main` | **Blocked** | Force push |
| `git push origin :feature` | **Blocked** | Deletes remote branch |
| `git branch -d feature` | Allowed | Safe delete (only if merged) |
| `git branch -D feature` | **Blocked** | Force delete |
| `git checkout feature` | Allowed | Switch branch |
| `git checkout -- file.txt` | Allowed | Restore single file |
| `git checkout -- .` | **Blocked** | Discards ALL changes |
| `git stash` | Allowed | Stash changes |
| `git stash pop` | Allowed | Apply and remove stash |
| `git stash drop` | **Blocked** | Loses stashed work |
| `git stash clear` | **Blocked** | Loses all stashes |
| `git reset HEAD~1` | Allowed | Soft reset |
| `git reset --hard` | **Blocked** | Loses changes |
| `git clean -n` | Allowed | Dry run |
| `git clean -fd` | **Blocked** | Deletes untracked |

### chmod commands

| Command | Status | Reason |
|---------|--------|--------|
| `chmod +x script.sh` | Allowed | Add execute |
| `chmod 644 file.txt` | Allowed | Normal permissions |
| `chmod 000 file.txt` | **Blocked** | Removes all permissions |
| `chmod 777 ~/.ssh/id_rsa` | **Blocked** | Security risk |
| `chmod -R 000 /path` | **Blocked** | Recursive removal |

## Future Improvements

### 1. Add more command categories

```python
# rm: Block recursive/force deletion
RM_DANGEROUS = [
    (r'rm\s+-rf\s+/', 'rm -rf / (catastrophic)'),
    (r'rm\s+-rf\s+~', 'rm -rf ~ (deletes home)'),
    (r'rm\s+-rf\s+\*', 'rm -rf * (deletes everything)'),
    (r'rm\s+-rf\s+\.', 'rm -rf . (deletes current dir)'),
]

# curl/wget: Block piping to shell
DOWNLOAD_DANGEROUS = [
    (r'curl\s+.*\|\s*sh', 'curl | sh (arbitrary code execution)'),
    (r'curl\s+.*\|\s*bash', 'curl | bash (arbitrary code execution)'),
    (r'wget\s+.*-O-\s*\|\s*sh', 'wget -O- | sh (arbitrary code execution)'),
]

# Python: Block dangerous one-liners
PYTHON_DANGEROUS = [
    (r'python.*-c\s+.*os\.system', 'python -c with os.system'),
    (r'python.*-c\s+.*subprocess', 'python -c with subprocess'),
    (r'python.*-c\s+.*__import__.*os', 'python -c importing os'),
]
```

### 2. Add allowlist for specific safe patterns

```python
# Sometimes you legitimately need force push to your own feature branch
GIT_ALLOWLIST = [
    r'git\s+push\s+--force-with-lease',  # Safer force push
    r'git\s+push\s+-f\s+origin\s+feature/',  # Force to feature branches only
]

def check_allowlist(command: str, allowlist: list[str]) -> bool:
    """Check if command matches an allowed exception."""
    for pattern in allowlist:
        if re.search(pattern, command, re.IGNORECASE):
            return True
    return False
```

### 3. Add interactive confirmation mode

Instead of blocking, prompt for confirmation:

```python
def main() -> None:
    c = create_context()

    if c.tool_name != "Bash":
        c.output.exit_success()
        return

    command = c.tool_input.get("command", "")
    is_safe, reason = check_command(command)

    if not is_safe:
        # Could use exit_with_confirmation if cchooks supports it
        # For now, just block
        c.output.exit_block(f"{reason}\n\nTo proceed, run this command manually.")
    else:
        c.output.exit_success()
```

### 4. Add logging for blocked commands

```python
import logging
from datetime import datetime
from pathlib import Path

LOG_FILE = Path.home() / ".claude" / "logs" / "blocked_commands.log"

def log_blocked_command(command: str, reason: str) -> None:
    """Log blocked commands for security auditing."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().isoformat()
    with open(LOG_FILE, "a") as f:
        f.write(f"{timestamp} | {reason} | {command}\n")
```

### 5. Add severity levels

```python
from enum import Enum

class Severity(Enum):
    BLOCK = "block"      # Always block
    WARN = "warn"        # Warn but allow
    LOG = "log"          # Just log, allow silently

FIND_PATTERNS = [
    (r'\s-delete\b', 'find -delete', Severity.BLOCK),
    (r'\s-exec\s+rm\b', 'find -exec rm', Severity.BLOCK),
    (r'\s-exec\s', 'find -exec (any)', Severity.WARN),  # Warn on any exec
]
```

### 6. Configuration file support

```python
# ~/.claude/hooks/dangerous_command_guard.yaml
block_patterns:
  find:
    - pattern: '\s-delete\b'
      description: 'find -delete'
      severity: block
  git:
    - pattern: 'git\s+push\s+--force'
      description: 'force push'
      severity: block

allow_patterns:
  git:
    - 'git\s+push\s+--force-with-lease'  # Safer alternative
```

## Testing the Hook

```bash
# Test that safe commands pass
echo 'find . -name "*.py"' | dangerous_command_guard.py  # Should pass
echo 'git push origin main' | dangerous_command_guard.py  # Should pass

# Test that dangerous commands are blocked
echo 'find . -delete' | dangerous_command_guard.py  # Should block
echo 'git push --force' | dangerous_command_guard.py  # Should block
```

## Related Hooks

- `enforce-uv`: Block bare python/pip commands in favor of uv
- `protect-env`: Block reading .env files
- `git-safety-guard`: Additional git protections
- `supply-chain-guard`: Block suspicious package installations

## Changelog

### 1.0.0
- Initial release
- Support for find, xargs, git, chmod patterns
- Pattern-based blocking with descriptive messages

---

## Recommended Global Allow List

This is the full recommended allow list for `~/.claude/settings.json`, designed to work with this hook for maximum safety:

```json
{
  "permissions": {
    "allow": [
      "Bash(cat:*)",
      "Bash(ls:*)",
      "Bash(grep:*)",
      "Bash(tree:*)",
      "Bash(wc:*)",
      "Bash(cut:*)",
      "Bash(sort:*)",
      "Bash(mkdir:*)",
      "Bash(find:*)",
      "Bash(xargs:*)",
      "Bash(chmod:*)",
      "Bash(git checkout:*)",
      "Bash(git add:*)",
      "Bash(git commit:*)",
      "Bash(git push:*)",
      "Bash(git pull:*)",
      "Bash(git fetch:*)",
      "Bash(git show:*)",
      "Bash(git merge:*)",
      "Bash(git merge-base:*)",
      "Bash(git branch:*)",
      "Bash(git log:*)",
      "Bash(git diff:*)",
      "Bash(git status:*)",
      "Bash(git stash:*)",
      "Bash(git worktree:*)",
      "Bash(gh pr create:*)",
      "Bash(gh pr view:*)",
      "Bash(gh pr checks:*)",
      "Bash(gh pr merge:*)",
      "Bash(gh run list:*)",
      "Bash(gh run view:*)",
      "Bash(gh search:*)",
      "Bash(gh release create:*)",
      "Bash(gh release view:*)",
      "Bash(gh release list:*)",
      "Bash(make fmt:*)",
      "Bash(make lint:*)",
      "Bash(make typecheck:*)",
      "Bash(make test:*)",
      "Bash(make ci:*)",
      "Bash(make coverage:*)",
      "Bash(uv sync:*)",
      "Bash(uv add:*)",
      "Bash(uv remove:*)",
      "Bash(uv lock:*)",
      "Bash(uv tree:*)",
      "Bash(uv venv:*)",
      "Bash(uv build:*)",
      "Bash(uv run pytest:*)",
      "Bash(uv run mypy:*)",
      "Bash(uv run ruff:*)",
      "Bash(uv pip list:*)",
      "Bash(uv pip show:*)",
      "Bash(uv pip check:*)",
      "Bash(uvx ruff:*)",
      "Bash(uvx pyright:*)",
      "Bash(uvx pre-commit:*)",
      "WebSearch",
      "WebFetch(domain:github.com)",
      "WebFetch(domain:raw.githubusercontent.com)",
      "WebFetch(domain:docs.pydantic.dev)",
      "WebFetch(domain:docs.litellm.ai)",
      "WebFetch(domain:docs.astral.sh)",
      "WebFetch(domain:pypi.org)",
      "Skill(core:plan_review)",
      "Skill(core:workflows:work)",
      "Skill(core:agent-native-architecture)",
      "Skill(core:compound-docs)",
      "Skill(core:create-agent-skills)",
      "Skill(core:file-todos)",
      "Skill(core:git-ship)",
      "Skill(core:git-worktree)",
      "Skill(core:skill-creator)",
      "mcp__plugin_core_context7__resolve-library-id",
      "mcp__plugin_core_context7__query-docs"
    ]
  }
}
```

### Categories Summary

| Category | Commands | Notes |
|----------|----------|-------|
| **File ops (read)** | `cat`, `ls`, `grep`, `tree`, `wc`, `cut`, `sort` | Safe read-only |
| **File ops (write)** | `mkdir`, `find`, `xargs`, `chmod` | Protected by hook |
| **Git (safe)** | `add`, `commit`, `pull`, `fetch`, `show`, `merge`, `merge-base`, `log`, `diff`, `status`, `worktree` | Always safe |
| **Git (protected)** | `checkout`, `push`, `branch`, `stash` | Protected by hook |
| **GitHub CLI** | `gh pr *`, `gh run *`, `gh search`, `gh release *` | Scoped to GH |
| **Make** | `fmt`, `lint`, `typecheck`, `test`, `ci`, `coverage` | Explicit targets only |
| **uv (package)** | `sync`, `add`, `remove`, `lock`, `tree`, `venv`, `build` | Package management |
| **uv (run)** | `pytest`, `mypy`, `ruff` | Explicit tools only |
| **uv (pip)** | `list`, `show`, `check` | Read-only |
| **uvx** | `ruff`, `pyright`, `pre-commit` | Dev tools |
| **Web** | `WebSearch`, `WebFetch` (6 domains) | Documentation sites |
| **Skills** | 9 core skills | Workflow automation |
| **MCP** | `context7` tools | Documentation lookup |

### What's NOT in the list (by design)

| Excluded | Reason |
|----------|--------|
| `Bash(python:*)`, `Bash(python3:*)` | Use `uv run python` instead |
| `Bash(pytest:*)` | Use `uv run pytest` instead |
| `Bash(rm:*)` | Too dangerous, no hook protection |
| `Bash(make:*)` | Too broad, use explicit targets |
| `Bash(git:*)` | Too broad, use explicit commands |
| `Bash(uv run:*)` | Too broad, allows `uv run python -c "..."` |
| `Bash(uv run python:*)` | Allows arbitrary code execution |
