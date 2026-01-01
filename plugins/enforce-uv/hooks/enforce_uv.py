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
    "python": (r"(?:^|&&|\|\||;)\s*python\s", "uv run python"),
    "python3": (r"(?:^|&&|\|\||;)\s*python3\s", "uv run python"),
    "pip install": (r"(?:^|&&|\|\||;)\s*pip\s+install", "uv add"),
    "pip3 install": (r"(?:^|&&|\|\||;)\s*pip3\s+install", "uv add"),
    "pytest": (r"(?:^|&&|\|\||;)\s*pytest(?:\s|$)", "uv run pytest"),
    "ruff": (r"(?:^|&&|\|\||;)\s*ruff\s", "uvx ruff"),
}

for cmd, (pattern, suggestion) in patterns.items():
    if re.search(pattern, command):
        c.output.exit_block(f"Use '{suggestion}' instead of bare '{cmd}' in uv projects")

c.output.exit_success()
