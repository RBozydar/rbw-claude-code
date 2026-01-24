#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["cchooks"]
# ///
"""PreToolUse hook to prevent reading .env files (except examples/templates)."""

import re

from cchooks import PreToolUseContext, create_context


c = create_context()
assert isinstance(c, PreToolUseContext)

if c.tool_name != "Read":
    c.output.exit_success()

file_path = c.tool_input.get("file_path", "")

# Safe patterns - allow these .env files
SAFE_PATTERNS = [
    r"\.env\.example$",
    r"\.env\.sample$",
    r"\.env\.template$",
    r"\.env\.dist$",
]

# Check safe patterns first
for pattern in SAFE_PATTERNS:
    if re.search(pattern, file_path):
        c.output.exit_success()

# Block patterns for env files
ENV_PATTERNS = [
    r"\.env$",           # Exactly .env
    r"\.env\.[^/]+$",    # .env.local, .env.production, etc.
    r"\.envrc$",        # .envrc files
]

for pattern in ENV_PATTERNS:
    if re.search(pattern, file_path):
        c.output.exit_block(
            f"Reading '{file_path}' is blocked.\n"
            "Environment files may contain secrets and should not be read by AI assistants.\n"
            "If you need to see the structure, check .env.example instead."
        )

c.output.exit_success()
