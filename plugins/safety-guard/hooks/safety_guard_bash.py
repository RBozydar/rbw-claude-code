#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["cchooks"]
# ///
"""PreToolUse hook to block destructive file operations and supply chain attacks."""

import re

from cchooks import PreToolUseContext, create_context


c = create_context()
assert isinstance(c, PreToolUseContext)

if c.tool_name != "Bash":
    c.output.exit_success()

command = c.tool_input.get("command", "")

# Safe patterns - allow these
SAFE_PATTERNS = [
    r"rm\s+-rf\s+(/tmp/|/var/tmp/|\$TMPDIR|\${TMPDIR})",
    r"rm\s+-fr\s+(/tmp/|/var/tmp/|\$TMPDIR|\${TMPDIR})",
]

# Destructive patterns - block these
BLOCKED_PATTERNS = [
    # File destruction
    (r"rm\s+(-[rRf]+\s+)+(?!/tmp/)(?!/var/tmp/)(?!\$TMPDIR)", "rm -rf is destructive outside temp directories"),
    (r"find\s+.*-delete", "find -delete permanently removes files"),
    (r"find\s+.*-exec\s+rm", "find -exec rm permanently removes files"),
    (r"shred\s+", "shred permanently destroys file data"),
    (r"truncate\s+", "truncate destroys file contents"),

    # Supply chain attacks
    (r"curl\s+.*\|\s*(ba)?sh", "curl pipe to shell is a supply chain attack vector"),
    (r"wget\s+.*\|\s*(ba)?sh", "wget pipe to shell is a supply chain attack vector"),
    (r"curl\s+.*\|\s*zsh", "curl pipe to shell is a supply chain attack vector"),
    (r"wget\s+.*\|\s*zsh", "wget pipe to shell is a supply chain attack vector"),

    # Command execution bypass (check for destructive git commands hidden in bash -c)
    (r"(ba)?sh\s+-c\s+['\"].*git\s+reset\s+--hard", "bash -c with destructive git command detected"),
    (r"(ba)?sh\s+-c\s+['\"].*git\s+push\s+.*--force", "bash -c with destructive git command detected"),
    (r"(ba)?sh\s+-c\s+['\"].*rm\s+-rf", "bash -c with rm -rf detected"),
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
