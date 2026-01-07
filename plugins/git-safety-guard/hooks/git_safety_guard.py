#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["cchooks"]
# ///
"""PreToolUse hook to block destructive git commands."""

import re

from cchooks import PreToolUseContext, create_context


c = create_context()
assert isinstance(c, PreToolUseContext)

if c.tool_name != "Bash":
    c.output.exit_success()

command = c.tool_input.get("command", "")

# Safe patterns - allow these even if they match blocked patterns
SAFE_PATTERNS = [
    r"git\s+checkout\s+-b\s",             # Creating a new branch
    r"git\s+checkout\s+--orphan\s",       # Creating orphan branch
    r"git\s+restore\s+--staged",          # Unstaging files (safe)
    r"git\s+clean\s+.*(-n|--dry-run)",    # Dry run mode
    r"git\s+push\s+.*--force-with-lease", # Safer force push
]

# Destructive patterns - block these
BLOCKED_PATTERNS = [
    # Working directory destruction
    (r"git\s+checkout\s+--\s", "git checkout -- discards uncommitted changes permanently"),
    (r"git\s+restore\s+(?!--staged)\S", "git restore overwrites working directory files"),
    (r"git\s+reset\s+--hard", "git reset --hard destroys all uncommitted work"),
    (r"git\s+reset\s+--merge", "git reset --merge can lose uncommitted changes"),
    (r"git\s+clean\s+-[a-zA-Z]*f", "git clean -f permanently deletes untracked files"),

    # Remote/history destruction
    (r"git\s+push\s+.*--force(?!-with-lease)", "git push --force destroys remote history"),
    (r"git\s+push\s+.*\s-[a-zA-Z]*f(?:\s|$)", "git push -f destroys remote history"),
    (r"git\s+push\s+.*--delete", "git push --delete removes remote branches/tags"),
    (r"git\s+push\s+\S+\s+:\S", "git push origin :ref deletes remote refs"),
    (r"git\s+branch\s+-D", "git branch -D force-deletes without merge check"),

    # Saved work destruction
    (r"git\s+stash\s+(drop|clear)", "git stash drop/clear permanently deletes saved work"),

    # Recovery destruction
    (r"git\s+reflog\s+(expire|delete)", "git reflog expire/delete removes recovery safety net"),
    (r"git\s+gc\s+--prune=now", "git gc --prune=now immediately removes unreferenced objects"),

    # History rewriting
    (r"git\s+filter-branch", "git filter-branch rewrites entire repository history"),
    (r"git\s+filter-repo", "git filter-repo rewrites entire repository history"),
]

# Check safe patterns first
for pattern in SAFE_PATTERNS:
    if re.search(pattern, command):
        c.output.exit_success()

# Check blocked patterns
for pattern, reason in BLOCKED_PATTERNS:
    if re.search(pattern, command):
        c.output.exit_block(
            f"BLOCKED: {reason}\n"
            f"Command: {command}\n"
            "If this operation is truly needed, ask the user for explicit permission."
        )

c.output.exit_success()
