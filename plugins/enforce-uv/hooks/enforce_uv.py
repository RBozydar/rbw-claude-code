#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["cchooks"]
# ///
"""PreToolUse hook to enforce uv usage in commands."""

import re

from cchooks import PreToolUseContext, create_context


c = create_context()

assert isinstance(c, PreToolUseContext)

if c.tool_name != "Bash":
    c.output.exit_success()

command = c.tool_input.get("command", "")

# Skip if already using uv
if command.startswith(("uv ", "uvx ")):
    c.output.exit_success()

# Detect problematic patterns at start of command or after && || ;
# Pattern: start of string or separator, then the bare command
patterns = {
    r"(?:^|&&|\|\||;)\s*python\s": "uv run python",
    r"(?:^|&&|\|\||;)\s*python3\s": "uv run python",
    r"(?:^|&&|\|\||;)\s*pip\s+install": "uv add",
    r"(?:^|&&|\|\||;)\s*pip3\s+install": "uv add",
    r"(?:^|&&|\|\||;)\s*pytest(?:\s|$)": "uv run pytest",
    r"(?:^|&&|\|\||;)\s*ruff\s": "uvx ruff",
}

for pattern, suggestion in patterns.items():
    if re.search(pattern, command):
        # Extract the matched command for clearer message
        cmd = pattern.split(r"\s*")[-1].replace(r"\s", "").replace("(?:", "").replace("|$)", "")
        c.output.exit_block(f"Use '{suggestion}' instead of bare '{cmd}' in uv projects")

c.output.exit_success()
