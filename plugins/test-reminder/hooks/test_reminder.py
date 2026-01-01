#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["cchooks"]
# ///
"""PostToolUse hook to remind about test files for new Python modules."""

import os
from pathlib import Path

from cchooks import PostToolUseContext, create_context


c = create_context()
assert isinstance(c, PostToolUseContext)

if c.tool_name != "Write":
    c.output.exit_success()

file_path = c.tool_input.get("file_path", "")

# Only for new Python files
if not file_path.endswith(".py"):
    c.output.exit_success()

# Skip test files, __init__.py, and config files
basename = os.path.basename(file_path)
if basename.startswith("test_") or basename in ("__init__.py", "conftest.py"):
    c.output.exit_success()

# Skip if file is already in a tests directory
if "tests" in Path(file_path).parts or "test" in Path(file_path).parts:
    c.output.exit_success()

# Check if corresponding test file exists
module_name = basename.replace(".py", "")
dir_path = os.path.dirname(file_path)

# Look for tests in common locations
possible_test_paths = [
    os.path.join(dir_path, f"test_{module_name}.py"),
    os.path.join(dir_path, "tests", f"test_{module_name}.py"),
    os.path.join(os.path.dirname(dir_path), "tests", f"test_{module_name}.py"),
]

test_exists = any(os.path.exists(p) for p in possible_test_paths)

if not test_exists:
    print(f"Reminder: Consider adding tests for {basename}")

c.output.exit_success()
