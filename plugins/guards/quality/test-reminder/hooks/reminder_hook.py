#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["cchooks"]
# ///
"""PostToolUse hook to remind about test files for new Python modules."""

from __future__ import annotations

import os
from pathlib import Path

from cchooks import PostToolUseContext, create_context


SKIP_BASENAMES = {"__init__.py", "conftest.py"}


def should_remind_about_tests(file_path: str) -> bool:
    if not file_path.endswith(".py"):
        return False

    basename = os.path.basename(file_path)
    if basename.startswith("test_") or basename in SKIP_BASENAMES:
        return False

    parts = Path(file_path).parts
    if "tests" in parts or "test" in parts:
        return False

    return True


def possible_test_paths(file_path: str) -> list[str]:
    basename = os.path.basename(file_path)
    module_name = basename.removesuffix(".py")
    dir_path = os.path.dirname(file_path)
    parent_dir = os.path.dirname(dir_path)
    return [
        os.path.join(dir_path, f"test_{module_name}.py"),
        os.path.join(dir_path, "tests", f"test_{module_name}.py"),
        os.path.join(parent_dir, "tests", f"test_{module_name}.py"),
    ]


def has_corresponding_test(file_path: str) -> bool:
    return any(os.path.exists(path) for path in possible_test_paths(file_path))


def main() -> None:
    c = create_context()
    assert isinstance(c, PostToolUseContext)

    if c.tool_name != "Write":
        c.output.exit_success()

    file_path = c.tool_input.get("file_path", "")
    if not should_remind_about_tests(file_path):
        c.output.exit_success()

    if not has_corresponding_test(file_path):
        print(f"Reminder: Consider adding tests for {os.path.basename(file_path)}")

    c.output.exit_success()


if __name__ == "__main__":
    main()
