#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["cchooks"]
# ///
"""PreToolUse hook to prevent reading .env files via any method."""

import re

from cchooks import PreToolUseContext, create_context

# Patterns for env files that should be protected
# Matches: .env, .env.local, .env.production, .env.*, etc.
ENV_FILE_PATTERNS = [
    r"\.env$",  # Exactly .env
    r"\.env\.[^/\s]+",  # .env.local, .env.production, etc.
    r"/\.env$",  # .env at any path level
    r"/\.env\.[^/\s]+",  # .env.* at any path level
]

# Bash commands that read file contents
FILE_READING_COMMANDS = [
    "cat",
    "head",
    "tail",
    "less",
    "more",
    "bat",
    "view",
    "vim",
    "nvim",
    "nano",
    "emacs",
    "code",
    "sed",
    "awk",
    "perl",
    "ruby",
    "python",
    "node",
    "source",
    "\\.",  # source shorthand (escaped for regex)
    "eval",
    "xargs",
    "tee",
    "dd",
    "hexdump",
    "xxd",
    "od",
    "strings",
    "iconv",
    "base64",
    "cut",
    "sort",
    "uniq",
    "wc",
    "diff",
    "comm",
    "paste",
    "join",
    "file",
]

BLOCK_MESSAGE = (
    "Access to '{path}' is blocked. "
    "Environment files may contain secrets and should not be read by AI assistants."
)


def matches_env_file(path: str) -> bool:
    """Check if a path matches any env file pattern."""
    for pattern in ENV_FILE_PATTERNS:
        if re.search(pattern, path):
            return True
    return False


def check_read_tool(tool_input: dict) -> str | None:
    """Check Read tool for .env file access."""
    file_path = tool_input.get("file_path", "")
    if matches_env_file(file_path):
        return BLOCK_MESSAGE.format(path=file_path)
    return None


def check_grep_tool(tool_input: dict) -> str | None:
    """Check Grep tool for .env file access."""
    # Check the path parameter
    path = tool_input.get("path", "")
    if matches_env_file(path):
        return BLOCK_MESSAGE.format(path=path)

    # Check glob patterns that might target .env files
    glob_pattern = tool_input.get("glob", "")
    if glob_pattern:
        # Block globs that explicitly target .env files
        env_glob_patterns = [
            r"\.env",
            r"\*\.env",
            r"\.env\*",
            r"\.env\.",
        ]
        for pattern in env_glob_patterns:
            if re.search(pattern, glob_pattern, re.IGNORECASE):
                return BLOCK_MESSAGE.format(path=glob_pattern)
    return None


def check_bash_command(tool_input: dict) -> str | None:
    """Check Bash command for .env file access."""
    command = tool_input.get("command", "")
    if not command:
        return None

    # Quick check - if no .env anywhere in command, it's safe
    if ".env" not in command.lower():
        return None

    # CRITICAL: Check for shell metacharacter bypasses
    # These patterns detect various obfuscation techniques that bypass simple string matching

    # 1. Brace expansion: cat {.env} or cat .{e,}nv or cat {.,}.env
    if re.search(r"\{[^}]*\.env", command) or re.search(r"\.env[^}]*\}", command):
        return BLOCK_MESSAGE.format(path="<brace expansion targeting .env>")

    # 2. Glob patterns: cat .en? or cat .env* or cat .e*v
    if re.search(r"\.en[v?*\[]", command) or re.search(r"\.e[*?\[].*v", command):
        return BLOCK_MESSAGE.format(path="<glob pattern targeting .env>")

    # 3. Backslash escaping: cat \.env or cat .\/env
    if re.search(r"\\\.env", command) or re.search(r"\.\\/env", command):
        return BLOCK_MESSAGE.format(path="<escaped .env path>")

    # 4. Variable expansion: F=.env && cat $F or VAR=.env; cat $VAR
    # Match variable assignment with .env followed by variable usage
    if re.search(r"\w+\s*=\s*['\"]?\.env", command):
        return BLOCK_MESSAGE.format(
            path="<variable assignment with .env (possible bypass)>"
        )

    # 5. String concatenation: cat .env'' or cat ".env" or cat '.env' or cat .e'n'v
    # Already handled by existing patterns but adding explicit check for quoted fragments
    if re.search(r"\.e['\"].*['\"].*v", command) or re.search(
        r"\.env['\"]['\"]", command
    ):
        return BLOCK_MESSAGE.format(path="<string concatenation targeting .env>")

    # Pattern to find .env files in the command
    # This catches paths like: .env, ./.env, path/.env, .env.local, etc.
    env_in_command = re.findall(
        r'(?:^|[\s\'"/])([^\s\'">|&;]*\.env(?:\.[^\s\'">|&;]*)?)', command
    )

    if env_in_command:
        # Check if any file-reading command is used with the .env file
        command_lower = command.lower()

        # Build regex pattern for file-reading commands
        cmd_pattern = r"(?:^|[|&;]\s*|[\s])(" + "|".join(FILE_READING_COMMANDS) + r")\s"

        if re.search(cmd_pattern, command_lower):
            return BLOCK_MESSAGE.format(path=env_in_command[0])

        # Also catch input redirection: < .env
        if re.search(r"<\s*[^\s]*\.env", command):
            return BLOCK_MESSAGE.format(path=env_in_command[0])

        # Catch process substitution: <(.env) or $(<.env)
        if re.search(r"<\([^)]*\.env", command) or re.search(
            r"\$\(\s*<[^)]*\.env", command
        ):
            return BLOCK_MESSAGE.format(path=env_in_command[0])

        # Catch cp/mv/scp that reads source .env
        if re.search(r"(?:cp|mv|scp|rsync)\s+[^\s]*\.env", command):
            return BLOCK_MESSAGE.format(path=env_in_command[0])

        # Catch direct execution: ./.env or bash .env (unlikely but possible)
        if re.search(r"(?:bash|sh|zsh)\s+[^\s]*\.env", command):
            return BLOCK_MESSAGE.format(path=env_in_command[0])

        # Catch grep/rg/ag searching in .env files
        if re.search(r"(?:grep|rg|ag|ack)\s+.*[^\s]*\.env", command):
            return BLOCK_MESSAGE.format(path=env_in_command[0])

    return None


def main() -> None:
    c = create_context()
    assert isinstance(c, PreToolUseContext)

    tool_name = c.tool_name
    tool_input = c.tool_input

    block_reason: str | None = None

    if tool_name == "Read":
        block_reason = check_read_tool(tool_input)
    elif tool_name == "Grep":
        block_reason = check_grep_tool(tool_input)
    elif tool_name == "Bash":
        block_reason = check_bash_command(tool_input)

    if block_reason:
        c.output.exit_block(block_reason)

    c.output.exit_success()


if __name__ == "__main__":
    main()
