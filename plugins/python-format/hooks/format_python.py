#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["cchooks"]
# ///
"""PostToolUse hook to auto-format Python files with ruff."""

import subprocess

from cchooks import PostToolUseContext, create_context


c = create_context()
assert isinstance(c, PostToolUseContext)

if c.tool_name in ("Write", "Edit") and c.tool_input.get("file_path", "").endswith(".py"):
    file_path = c.tool_input["file_path"]

    # Use uvx ruff directly - no Makefile dependency
    result = subprocess.run(
        ["uvx", "ruff", "format", file_path],
        check=False,
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print(f"Formatted: {file_path}")
    else:
        print(f"Format warning: {result.stderr}")

c.output.exit_success()
