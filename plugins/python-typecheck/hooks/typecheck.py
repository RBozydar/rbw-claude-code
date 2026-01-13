#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["cchooks"]
# ///
"""PostToolUse hook to run type checking after Python file edits."""

import subprocess

from cchooks import PostToolUseContext, create_context


c = create_context()
assert isinstance(c, PostToolUseContext)

if c.tool_name in ("Write", "Edit") and c.tool_input.get("file_path", "").endswith(".py"):
    file_path = c.tool_input["file_path"]

    # Use uvx pyright directly - no Makefile dependency
    result = subprocess.run(
        ["uvx", "pyright", file_path],
        check=False,
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print("Type check passed")
    else:
        print(f"Type errors:\n{result.stdout}")

c.output.exit_success()
