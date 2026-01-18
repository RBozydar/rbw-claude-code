#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["cchooks"]
# ///
"""PreToolUse hook to enforce conventional commit format.

This hook blocks bypass vectors and validates -m flag content.
A PostToolUse hook provides defense-in-depth by validating actual commits.

Blocked bypass vectors:
- -F/--file (read message from file)
- -C/--reuse-message (reuse existing commit message)
- -c/--reedit-message (reuse and edit)
- -t/--template (use template file)
- --no-verify/-n (skip hooks)
- git commit-tree (low-level plumbing)
- Command substitution in messages ($(), ``)
- Variable expansion in messages ($VAR)
"""

import re

from cchooks import PreToolUseContext, create_context

# Conventional commit pattern
CONVENTIONAL_PATTERN = re.compile(
    r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)"
    r"(\([^)]+\))?"  # Optional scope
    r"!?"  # Optional breaking change indicator
    r": .+"  # Required description
)

# Patterns that indicate git commit activity (including nested shells)
COMMIT_INDICATORS = [
    r"\bgit\s+commit\b",
    r"\bgit\s+cherry-pick\b",
    r"\bgit\s+revert\b",
    r"\bgit\s+merge\b",
    r"\bgit\s+am\b",
    r"\bgit\s+commit-tree\b",
]

# Commands that take large text arguments where git references are OK
# These commands often include documentation, PR descriptions, etc.
SAFE_ARGUMENT_COMMANDS = [
    r"^gh\s+pr\s+create\b",
    r"^gh\s+pr\s+edit\b",
    r"^gh\s+issue\s+create\b",
    r"^gh\s+issue\s+edit\b",
    r"^echo\b",
    r"^printf\b",
]

# Blocked commit methods we cannot reliably validate
BLOCKED_PATTERNS = [
    (
        r"-F\s+\S+|--file[=\s]\S+",
        "Use -m flag instead of -F/--file for commit messages",
    ),
    (
        r"-C\s+\S+|--reuse-message[=\s]\S+",
        "Use -m flag instead of -C/--reuse-message",
    ),
    (
        r"-c\s+\S+|--reedit-message[=\s]\S+",
        "Use -m flag instead of -c/--reedit-message",
    ),
    (r"-t\s+\S+|--template[=\s]\S+", "Use -m flag instead of -t/--template"),
    (r"--no-verify\b", "Cannot skip commit message verification with --no-verify"),
    (r"\bgit\s+commit-tree\b", "Use 'git commit' instead of low-level commit-tree"),
]

# Commands that create commits but aren't 'git commit'
OTHER_COMMIT_COMMANDS = [
    (r"\bgit\s+merge\b", "git merge"),
    (r"\bgit\s+cherry-pick\b", "git cherry-pick"),
    (r"\bgit\s+revert\b", "git revert"),
    (r"\bgit\s+am\b", "git am"),
]


def is_commit_command_context(command: str) -> bool:
    """Check if command is actually executing git commit, not just mentioning it.

    Commands like 'gh pr create --body "... git commit --amend ..."' should NOT
    trigger validation because they're just documenting git commands, not executing them.
    """
    stripped = command.strip()

    for pattern in SAFE_ARGUMENT_COMMANDS:
        if re.match(pattern, stripped):
            return False  # Not a commit context, skip validation

    return True


def extract_all_commands(cmd: str) -> list[str]:
    """Extract commands including those in bash -c, sh -c, eval."""
    commands = [cmd]
    # Find nested shell commands (single and double quoted)
    nested_single = re.findall(r"(?:bash|sh)\s+-c\s+'([^']+)'", cmd)
    nested_double = re.findall(r'(?:bash|sh)\s+-c\s+"([^"]+)"', cmd)
    commands.extend(nested_single)
    commands.extend(nested_double)
    # Find eval commands
    eval_single = re.findall(r"eval\s+'([^']+)'", cmd)
    eval_double = re.findall(r'eval\s+"([^"]+)"', cmd)
    commands.extend(eval_single)
    commands.extend(eval_double)
    return commands


def find_commit_command(command: str) -> str | None:
    """Find a git commit command in the full command string."""
    all_commands = extract_all_commands(command)

    for cmd in all_commands:
        for pattern in COMMIT_INDICATORS:
            if re.search(pattern, cmd, re.IGNORECASE):
                return cmd
    return None


def extract_messages(commit_cmd: str) -> list[str]:
    """Extract all -m messages from a commit command."""
    messages = []

    # Handle multiple patterns for -m flag
    # -m "msg" (double quoted)
    messages.extend(re.findall(r'-m\s+"([^"]*)"', commit_cmd))
    # -m 'msg' (single quoted)
    messages.extend(re.findall(r"-m\s+'([^']*)'", commit_cmd))
    # -m msg (unquoted single token, but not if it starts with -)
    unquoted = re.findall(r"-m\s+([^\s\"'-][^\s]*)", commit_cmd)
    messages.extend(unquoted)

    return messages


def has_dynamic_content(msg: str) -> bool:
    """Check if message contains command substitution or variable expansion.

    Allows markdown backticks (paired backticks like `code`) but blocks shell
    command substitution (unpaired or containing shell-like content).
    """
    # Command substitution: $(...) - always dangerous
    if "$(" in msg:
        return True

    # Variable expansion: $VAR or ${VAR}
    if re.search(r"\$\{?\w", msg):
        return True

    # Backticks: check if they're markdown (paired) vs shell substitution
    if "`" in msg:
        # Triple backticks (```code```) are markdown code blocks - safe
        if "```" in msg:
            # Remove triple backtick blocks, then check what remains
            remaining = re.sub(r"```[^`]*```", "", msg)
            if "`" not in remaining:
                return False
            msg = remaining

        # Count single backticks
        backtick_count = msg.count("`")

        # Unpaired backtick (odd count) = likely shell substitution
        if backtick_count % 2 != 0:
            return True

        # Paired backticks - check if content looks like shell commands
        # Extract content between backticks
        backtick_contents = re.findall(r"`([^`]+)`", msg)
        for content in backtick_contents:
            # Shell-like patterns: starts with command + args, or contains pipes/redirects
            # This catches `whoami`, `cat /etc/passwd`, but allows `method_name`, `ClassName`
            if re.search(r"^[a-z/]+\s+", content, re.IGNORECASE):
                # Looks like a command with arguments - block it
                return True
            if re.search(r"[|><]", content):
                # Contains pipe or redirect - block it
                return True

        # Paired backticks with code-like content (identifiers) - safe markdown
        return False

    return False


def main() -> None:
    c = create_context()
    if not isinstance(c, PreToolUseContext):
        c.output.exit_success()

    if c.tool_name != "Bash":
        c.output.exit_success()

    command = c.tool_input.get("command", "")

    # Skip validation for commands that just mention git in text arguments
    # (e.g., gh pr create --body "... git commit --amend ...")
    if not is_commit_command_context(command):
        c.output.exit_success()

    # Find any git commit command (including in nested shells)
    commit_cmd = find_commit_command(command)
    if not commit_cmd:
        c.output.exit_success()
        return  # For type checker

    # Check for blocked bypass patterns
    for pattern, msg in BLOCKED_PATTERNS:
        if re.search(pattern, commit_cmd):
            c.output.exit_block(msg)

    # For non-commit commands (merge, cherry-pick, revert, am), allow without -m
    # These have auto-generated messages that PostToolUse will validate
    for pattern, _cmd_name in OTHER_COMMIT_COMMANDS:
        if re.search(pattern, commit_cmd):
            # If they specify -m, we should validate it
            messages = extract_messages(commit_cmd)
            if messages:
                # Validate the message
                for msg in messages:
                    if has_dynamic_content(msg):
                        c.output.exit_block(
                            "Commit message cannot contain command substitution or variables.\n"
                            "Use a literal message string."
                        )
                # Only validate first message (subject line)
                if not CONVENTIONAL_PATTERN.match(messages[0]):
                    c.output.exit_block(
                        f"Commit message must follow conventional commits format:\n"
                        f"  type(scope): description\n\n"
                        f"Types: feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert\n\n"
                        f"Got: '{messages[0]}'"
                    )
            # No -m flag on merge/cherry-pick/etc is OK (auto-message)
            c.output.exit_success()

    # For git commit, extract and validate -m messages
    messages = extract_messages(commit_cmd)

    # Check for dynamic content in messages
    for msg in messages:
        if has_dynamic_content(msg):
            c.output.exit_block(
                "Commit message cannot contain command substitution or variables.\n"
                "Use a literal message string."
            )

    if not messages:
        # No -m flag - check for special cases
        if "--amend" in commit_cmd:
            # Amending without message change is OK
            c.output.exit_success()

        if "--fixup" in commit_cmd or "--squash" in commit_cmd:
            # These auto-generate messages
            c.output.exit_success()

        # Check for heredoc patterns
        if "EOF" in command or "<<" in command:
            c.output.exit_block(
                "Use -m flag with literal message instead of heredoc.\n"
                'Example: git commit -m "feat: add feature"'
            )

        # No message provided - this will open an editor (which Claude can't use)
        # or fail. Let it through for PostToolUse to catch if needed.
        c.output.exit_success()

    # Validate first message (subject line) against conventional commits
    primary_message = messages[0]

    # Allow fixup!/squash! prefixes
    if primary_message.startswith(("fixup! ", "squash! ")):
        c.output.exit_success()

    if not CONVENTIONAL_PATTERN.match(primary_message):
        c.output.exit_block(
            f"Commit message must follow conventional commits format:\n"
            f"  type(scope): description\n\n"
            f"Types: feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert\n\n"
            f"Got: '{primary_message}'"
        )

    c.output.exit_success()


if __name__ == "__main__":
    main()
