#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["cchooks"]
# ///
"""PostToolUse hook to validate commit messages after creation.

This is defense-in-depth: validates the ACTUAL commit message from git,
catching any bypasses that slipped through the PreToolUse hook.

If an invalid commit is detected, it is automatically reverted.
"""

import re
import subprocess

from cchooks import PostToolUseContext, create_context

# Conventional commit pattern
CONVENTIONAL_PATTERN = re.compile(
    r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)"
    r"(\([^)]+\))?"  # Optional scope
    r"!?"  # Optional breaking change indicator
    r": .+"  # Required description
)

# Commands that create commits
COMMIT_COMMANDS = [
    "git commit",
    "git merge",
    "git cherry-pick",
    "git revert",
    "git am",
]


def get_latest_commit_message() -> str | None:
    """Get the subject line of the most recent commit."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%s"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            return None
        return result.stdout.strip()
    except Exception:
        return None


def get_commit_hash() -> str | None:
    """Get the hash of the most recent commit."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            return None
        return result.stdout.strip()[:8]
    except Exception:
        return None


def revert_commit() -> bool:
    """Revert the most recent commit (soft reset)."""
    try:
        result = subprocess.run(
            ["git", "reset", "--soft", "HEAD~1"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except Exception:
        return False


def main() -> None:
    c = create_context()
    if not isinstance(c, PostToolUseContext):
        c.output.exit_success()

    if c.tool_name != "Bash":
        c.output.exit_success()

    command = c.tool_input.get("command", "")

    # Check if a commit-creating command was run
    if not any(cmd in command for cmd in COMMIT_COMMANDS):
        c.output.exit_success()

    # Check if the command succeeded (exit code 0)
    # If it failed, no commit was created
    stdout = c.tool_response.get("stdout", "")

    # Look for signs that a commit was actually created
    commit_created_indicators = [
        "create mode",
        "delete mode",
        "[main ",
        "[master ",
        "files changed",
        "insertions(+)",
        "deletions(-)",
    ]

    if not any(indicator in stdout for indicator in commit_created_indicators):
        # No commit was created
        c.output.exit_success()

    # Get the actual commit message
    message = get_latest_commit_message()
    if not message:
        c.output.exit_success()
        return  # For type checker

    # Allow merge commits (auto-generated)
    if message.startswith("Merge "):
        c.output.exit_success()

    # Allow revert commits (auto-generated)
    if message.startswith("Revert "):
        c.output.exit_success()

    # Allow fixup/squash commits
    if message.startswith(("fixup! ", "squash! ")):
        c.output.exit_success()

    # Validate against conventional commits
    if CONVENTIONAL_PATTERN.match(message):
        c.output.exit_success()

    # Invalid commit detected - revert it
    commit_hash = get_commit_hash()
    reverted = revert_commit()

    if reverted:
        c.output.exit_continue(
            f"COMMIT REVERTED! Message doesn't follow conventional format.\n"
            f"  Commit: {commit_hash}\n"
            f"  Got: '{message}'\n"
            f"  Expected: type(scope): description\n"
            f"  Types: feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert\n\n"
            f"Your changes are still staged. Please commit again with a valid message."
        )
    else:
        c.output.exit_continue(
            f"WARNING: Invalid commit message detected but could not revert.\n"
            f"  Got: '{message}'\n"
            f"  Expected: type(scope): description\n"
            f'Please amend the commit with: git commit --amend -m "type: description"'
        )


if __name__ == "__main__":
    main()
