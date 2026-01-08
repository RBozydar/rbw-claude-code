#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["cchooks"]
# ///
"""Allow only safe gh api commands (PR comment fetching)."""

import re
import shlex

from cchooks import PreToolUseContext, create_context

# Safe patterns for gh api - read-only PR comment operations
ALLOWED_PATTERNS = [
    # Fetch inline PR comments: gh api repos/{owner}/{repo}/pulls/{num}/comments
    r"^repos/[^/]+/[^/]+/pulls/\d+/comments$",
    # Fetch issue/PR comments: gh api repos/{owner}/{repo}/issues/{num}/comments
    r"^repos/[^/]+/[^/]+/issues/\d+/comments$",
    # Fetch PR reviews: gh api repos/{owner}/{repo}/pulls/{num}/reviews$
    r"^repos/[^/]+/[^/]+/pulls/\d+/reviews$",
    # Fetch specific review comments
    r"^repos/[^/]+/[^/]+/pulls/\d+/reviews/\d+/comments$",
]

# Dangerous HTTP methods to block
DANGEROUS_METHODS = ["POST", "PUT", "PATCH", "DELETE"]


def extract_endpoint(parts: list[str]) -> str | None:
    """Extract the API endpoint from parsed command parts."""
    skip_next = False
    # Flags that take arguments
    flags_with_args = {"-X", "-H", "-f", "-F", "--jq", "-q", "--template", "-t"}

    for part in parts[2:]:  # Skip "gh" and "api"
        if skip_next:
            skip_next = False
            continue
        if part.startswith("-"):
            if part in flags_with_args:
                skip_next = True
            continue
        return part
    return None


def check_for_dangerous_method(parts: list[str]) -> str | None:
    """Check if command uses a dangerous HTTP method. Returns method if found."""
    for i, part in enumerate(parts):
        if part == "-X" and i + 1 < len(parts):
            method = parts[i + 1].upper()
            if method in DANGEROUS_METHODS:
                return method
    return None


def main() -> None:
    c = create_context()
    if not isinstance(c, PreToolUseContext):
        c.output.exit_success()

    command = c.tool_input.get("command", "")

    # Only check gh api commands
    if not command.strip().startswith("gh api"):
        c.output.exit_success()

    try:
        parts = shlex.split(command)
    except ValueError:
        c.output.exit_block("Could not parse gh api command")
        return  # noreturn, but helps type checker

    # Check for dangerous HTTP methods
    dangerous_method = check_for_dangerous_method(parts)
    if dangerous_method:
        c.output.exit_block(
            f"gh api with {dangerous_method} method requires manual approval. "
            "Only GET requests for PR comments are auto-allowed."
        )
        return  # noreturn, but helps type checker

    # Extract the API endpoint
    endpoint = extract_endpoint(parts)
    if endpoint is None:
        c.output.exit_block("Could not determine gh api endpoint")
        return  # noreturn, but helps type checker

    # Check if endpoint matches allowed patterns
    for pattern in ALLOWED_PATTERNS:
        if re.match(pattern, endpoint):
            c.output.exit_success()

    c.output.exit_block(
        f"gh api endpoint '{endpoint}' is not in the allowed list.\n"
        "Allowed: PR comments, issue comments, and PR reviews (read-only).\n"
        "Add to ALLOWED_PATTERNS in the hook if this is a safe read operation."
    )


if __name__ == "__main__":
    main()
