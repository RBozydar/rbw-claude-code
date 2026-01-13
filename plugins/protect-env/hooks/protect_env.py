#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["cchooks"]
# ///
"""PreToolUse hook to prevent reading .env files."""

import re

from cchooks import PreToolUseContext, create_context


c = create_context()

assert isinstance(c, PreToolUseContext)

if c.tool_name != "Read":
    c.output.exit_success()

file_path = c.tool_input.get("file_path", "")

# Patterns for env files that should be protected
# Matches: .env, .env.local, .env.production, .env.*, etc.
env_patterns = [
    r"\.env$",           # Exactly .env
    r"\.env\.[^/]+$",    # .env.local, .env.production, etc.
    r"/\.env$",          # .env at any path level
    r"/\.env\.[^/]+$",   # .env.* at any path level
]

for pattern in env_patterns:
    if re.search(pattern, file_path):
        c.output.exit_block(
            f"Reading '{file_path}' is blocked. "
            "Environment files may contain secrets and should not be read by AI assistants."
        )

c.output.exit_success()
