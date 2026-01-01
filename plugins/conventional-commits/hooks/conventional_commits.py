#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["cchooks"]
# ///
"""PreToolUse hook to enforce conventional commit format."""

import re

from cchooks import PreToolUseContext, create_context


c = create_context()
assert isinstance(c, PreToolUseContext)

if c.tool_name != "Bash":
    c.output.exit_success()

command = c.tool_input.get("command", "")

if "git commit" not in command:
    c.output.exit_success()

# Extract commit message from -m flag
match = re.search(r'-m\s+["\']([^"\']+)["\']', command)
if not match:
    # Might be using heredoc or other format, allow it
    c.output.exit_success()

message = match.group(1)

# Conventional commit pattern
pattern = r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\(.+\))?: .+"

if not re.match(pattern, message):
    c.output.exit_block(
        "Commit message must follow conventional commits format:\n"
        "  feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert: description\n"
        f"  Got: '{message}'"
    )

c.output.exit_success()
