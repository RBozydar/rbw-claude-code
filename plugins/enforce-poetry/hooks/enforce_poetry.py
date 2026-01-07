#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["cchooks"]
# ///
"""PreToolUse hook to enforce poetry usage in commands."""

import re

from cchooks import PreToolUseContext, create_context


c = create_context()

assert isinstance(c, PreToolUseContext)

if c.tool_name != "Bash":
    c.output.exit_success()

command = c.tool_input.get("command", "")

# Skip if already using poetry
if command.startswith("poetry "):
    c.output.exit_success()

# Detect problematic patterns at start of command or after && || ;
# Pattern: start of string or separator, then the bare command
patterns = {
    "python": (r"(?:^|&&|\|\||;)\s*python\s", "poetry run python"),
    "python3": (r"(?:^|&&|\|\||;)\s*python3\s", "poetry run python"),
    "pip install": (r"(?:^|&&|\|\||;)\s*pip\s+install", "poetry add"),
    "pip3 install": (r"(?:^|&&|\|\||;)\s*pip3\s+install", "poetry add"),
    "pytest": (r"(?:^|&&|\|\||;)\s*pytest(?:\s|$)", "poetry run pytest"),
    "ruff": (r"(?:^|&&|\|\||;)\s*ruff\s", "poetry run ruff"),
}

for cmd, (pattern, suggestion) in patterns.items():
    if re.search(pattern, command):
        c.output.exit_block(f"Use '{suggestion}' instead of bare '{cmd}' in poetry projects")

c.output.exit_success()
