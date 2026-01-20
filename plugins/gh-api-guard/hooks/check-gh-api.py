#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["cchooks"]
# ///
"""Block dangerous gh CLI commands, allow only safe read operations."""

import re
import shlex

from cchooks import PreToolUseContext, create_context

# Safe patterns for gh api - read-only operations
# Note: Leading slash is stripped before matching
ALLOWED_API_PATTERNS = [
    # PR comments (inline/review comments)
    r"^repos/[^/]+/[^/]+/pulls/\d+/comments$",
    # Issue/PR conversation comments
    r"^repos/[^/]+/[^/]+/issues/\d+/comments$",
    # PR reviews
    r"^repos/[^/]+/[^/]+/pulls/\d+/reviews$",
    # Specific review comments
    r"^repos/[^/]+/[^/]+/pulls/\d+/reviews/\d+/comments$",
    # PR details
    r"^repos/[^/]+/[^/]+/pulls/\d+$",
    # Issue details
    r"^repos/[^/]+/[^/]+/issues/\d+$",
    # Commit comments
    r"^repos/[^/]+/[^/]+/commits/[a-f0-9]+/comments$",
    # Repository info
    r"^repos/[^/]+/[^/]+$",
    # List PRs/issues (useful for searching)
    r"^repos/[^/]+/[^/]+/pulls$",
    r"^repos/[^/]+/[^/]+/issues$",
    # PR files (for reviewing changes)
    r"^repos/[^/]+/[^/]+/pulls/\d+/files$",
    # Commits on a PR
    r"^repos/[^/]+/[^/]+/pulls/\d+/commits$",
]

# Dangerous HTTP methods to block
DANGEROUS_METHODS = ["POST", "PUT", "PATCH", "DELETE"]

# Dangerous gh subcommands that should ALWAYS be blocked
# These are destructive or security-sensitive operations
BLOCKED_SUBCOMMANDS = [
    # Repository destruction
    (r"\bgh\s+repo\s+delete\b", "gh repo delete permanently destroys repositories"),
    (r"\bgh\s+repo\s+archive\b", "gh repo archive requires manual approval"),
    # PR/Issue modifications
    (r"\bgh\s+pr\s+merge\b", "gh pr merge requires manual approval"),
    (r"\bgh\s+pr\s+close\b", "gh pr close requires manual approval"),
    (r"\bgh\s+issue\s+close\b", "gh issue close requires manual approval"),
    (r"\bgh\s+issue\s+delete\b", "gh issue delete requires manual approval"),
    # Secrets and variables (security-sensitive)
    (r"\bgh\s+secret\s+set\b", "gh secret set modifies repository secrets"),
    (r"\bgh\s+secret\s+delete\b", "gh secret delete removes repository secrets"),
    (r"\bgh\s+variable\s+set\b", "gh variable set modifies repository variables"),
    (r"\bgh\s+variable\s+delete\b", "gh variable delete removes repository variables"),
    # Release management
    (r"\bgh\s+release\s+delete\b", "gh release delete requires manual approval"),
    # Branch protection
    (r"\bgh\s+ruleset\b", "gh ruleset commands modify branch protection"),
    # Workflow runs
    (r"\bgh\s+run\s+cancel\b", "gh run cancel requires manual approval"),
    (r"\bgh\s+run\s+delete\b", "gh run delete requires manual approval"),
    # Cache management
    (r"\bgh\s+cache\s+delete\b", "gh cache delete requires manual approval"),
    # GraphQL mutations (can do anything)
    (
        r"\bgh\s+api\s+graphql\b.{0,2000}?\bmutation\b",
        "GraphQL mutations require manual approval",
    ),
]

# Pattern for bash -c / sh -c / eval containing gh commands
SHELL_WRAPPER_PATTERN = re.compile(
    r"""(?:(?:ba)?sh\s+-c|eval)\s+['"].*\bgh\s+""",
    re.IGNORECASE,
)

# Pattern for heredoc with gh commands
HEREDOC_GH_PATTERN = re.compile(
    r"<<-?\s*['\"]?\w+['\"]?.*\bgh\s+",
    re.DOTALL | re.IGNORECASE,
)


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


def check_blocked_subcommands(command: str) -> str | None:
    """Check if command contains blocked gh subcommands. Returns reason if blocked."""
    for pattern, reason in BLOCKED_SUBCOMMANDS:
        if re.search(pattern, command, re.IGNORECASE | re.DOTALL):
            return reason
    return None


def check_gh_api(command: str, c: PreToolUseContext) -> None:
    """Validate gh api commands."""
    try:
        parts = shlex.split(command)
    except ValueError:
        c.output.exit_block("Could not parse gh api command")
        return

    # Check for dangerous HTTP methods
    dangerous_method = check_for_dangerous_method(parts)
    if dangerous_method:
        c.output.exit_block(
            f"gh api with {dangerous_method} method requires manual approval. "
            "Only GET requests for PR comments are auto-allowed."
        )
        return

    # Extract the API endpoint
    endpoint = extract_endpoint(parts)
    if endpoint is None:
        c.output.exit_block("Could not determine gh api endpoint")
        return

    # Strip leading slash for consistent matching
    endpoint = endpoint.lstrip("/")

    # Check if endpoint matches allowed patterns
    for pattern in ALLOWED_API_PATTERNS:
        if re.match(pattern, endpoint):
            c.output.exit_success()

    c.output.exit_block(
        f"gh api endpoint '{endpoint}' is not in the allowed list.\n"
        "Allowed: PR comments, issue comments, and PR reviews (read-only).\n"
        "Add to ALLOWED_API_PATTERNS in the hook if this is a safe read operation."
    )


def main() -> None:
    c = create_context()
    if not isinstance(c, PreToolUseContext):
        c.output.exit_success()

    command = c.tool_input.get("command", "")

    # Quick check: if "gh" not in command, skip
    if "gh" not in command.lower():
        c.output.exit_success()

    # Check for shell wrapper bypass attempts (bash -c, eval)
    if SHELL_WRAPPER_PATTERN.search(command):
        c.output.exit_block(
            "gh commands inside bash -c or eval require manual approval.\n"
            "Run gh commands directly without shell wrappers."
        )
        return

    # Check for heredoc bypass
    if HEREDOC_GH_PATTERN.search(command):
        c.output.exit_block(
            "Heredoc with gh commands requires manual approval.\n"
            f"Command: {command}\n"
            "Run gh commands directly without heredocs."
        )
        return

    # Check for blocked subcommands first
    blocked_reason = check_blocked_subcommands(command)
    if blocked_reason:
        c.output.exit_block(
            f"BLOCKED: {blocked_reason}\n"
            f"Command: {command}\n"
            "If this operation is truly needed, ask the user for explicit permission."
        )
        return

    # Check if this is a gh api command
    # Use shlex to properly handle quoted arguments (e.g., --jq '.[] | .body')
    try:
        parts = shlex.split(command)
        # Find 'gh' followed by 'api' in the command parts
        for i, part in enumerate(parts):
            if part == "gh" and i + 1 < len(parts) and parts[i + 1] == "api":
                # Reconstruct the gh api command from this point
                # (shlex already handled the quoting correctly)
                check_gh_api(command, c)
                return
    except ValueError:
        # If shlex fails, fall back to simple check
        if re.search(r"\bgh\s+api\b", command):
            check_gh_api(command, c)
            return

    # For other gh commands not explicitly blocked, allow them
    c.output.exit_success()


if __name__ == "__main__":
    main()
