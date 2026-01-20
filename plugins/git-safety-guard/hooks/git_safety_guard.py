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
    r"git\s+checkout\s+-b\s",  # Creating a new branch
    r"git\s+checkout\s+--orphan\s",  # Creating orphan branch
    r"git\s+restore\s+--staged",  # Unstaging files (safe)
    r"git\s+clean\s+.*(-n|--dry-run)",  # Dry run mode
]

# Destructive patterns - block these
BLOCKED_PATTERNS = [
    # Working directory destruction
    (
        r"git\s+checkout\s+--\s",
        "git checkout -- discards uncommitted changes permanently",
    ),
    (
        r"git\s+restore\s+(?!--staged)\S",
        "git restore overwrites working directory files",
    ),
    (r"git\s+reset\s+--hard", "git reset --hard destroys all uncommitted work"),
    (r"git\s+reset\s+--merge", "git reset --merge can lose uncommitted changes"),
    (r"git\s+clean\s+-[a-zA-Z]*f", "git clean -f permanently deletes untracked files"),
    # Remote/history destruction
    (
        r"git\s+push\s+.*--force",
        "git push --force rewrites remote history (use new commits instead)",
    ),
    (
        r"git\s+push\s+(?:.*\s)?-[a-zA-Z]*f(?:\s|$)",
        "git push -f destroys remote history",
    ),
    (r"git\s+push\s+.*--delete", "git push --delete removes remote branches/tags"),
    (r"git\s+push\s+\S+\s+:\S", "git push origin :ref deletes remote refs"),
    (r"git\s+branch\s+-D", "git branch -D force-deletes without merge check"),
    # Saved work destruction
    (
        r"git\s+stash\s+(drop|clear)",
        "git stash drop/clear permanently deletes saved work",
    ),
    # Recovery destruction
    (
        r"git\s+reflog\s+(expire|delete)",
        "git reflog expire/delete removes recovery safety net",
    ),
    (
        r"git\s+gc\s+--prune=now",
        "git gc --prune=now immediately removes unreferenced objects",
    ),
    # History rewriting
    (r"git\s+filter-branch", "git filter-branch rewrites entire repository history"),
    (r"git\s+filter-repo", "git filter-repo rewrites entire repository history"),
    # Reference manipulation (alternative to branch deletion)
    (r"git\s+update-ref\s+-d", "git update-ref -d deletes references directly"),
    (r"git\s+update-ref\s+--delete", "git update-ref --delete removes references"),
    # Worktree destruction
    (
        r"git\s+worktree\s+remove\s+.*--force",
        "git worktree remove --force can lose work",
    ),
    # Submodule destruction
    (
        r"git\s+submodule\s+deinit\s+.*--force",
        "git submodule deinit --force removes submodule data",
    ),
    # Commit amendment (rewrites history)
    (r"git\s+commit\s+.*--amend", "git commit --amend rewrites commit history"),
    # Rebase (rewrites history)
    (
        r"git\s+rebase\b(?!\s+--(abort|continue|skip))",
        "git rebase rewrites commit history",
    ),
]

# Pattern for bash -c / sh -c / eval containing git commands
SHELL_WRAPPER_PATTERN = re.compile(
    r"""(?:(?:ba)?sh\s+-c|eval)\s+['"].*\bgit\s+""",
    re.IGNORECASE,
)

# Check for shell wrapper bypass attempts
if SHELL_WRAPPER_PATTERN.search(command):
    # Extract the inner command and check it
    inner_match = re.search(r"""(?:(?:ba)?sh\s+-c|eval)\s+['"](.+?)['"]""", command)
    if inner_match:
        inner_command = inner_match.group(1)
        # Check if inner command contains dangerous git operations
        for pattern, reason in BLOCKED_PATTERNS:
            if re.search(pattern, inner_command):
                c.output.exit_block(
                    f"BLOCKED: {reason} (detected inside shell wrapper)\n"
                    f"Command: {command}\n"
                    "If this operation is truly needed, ask the user for explicit permission."
                )

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
